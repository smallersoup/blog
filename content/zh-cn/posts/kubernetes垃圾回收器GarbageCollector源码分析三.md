title: kubernetes垃圾回收器GarbageCollector 源码分析（三）
date: '2019-10-21 17:40:11'
updated: '2019-10-22 10:39:05'
tags: [kubernetes]
permalink: /201910211740k8s
---
> **kubernetes版本：1.13.2**

接前两节：
[kubernetes垃圾回收器GarbageCollector Controller源码分析（一）](https://liabio.blog.csdn.net/article/details/100081941)
[kubernetes垃圾回收器GarbageCollector Controller源码分析（二）](https://liabio.blog.csdn.net/article/details/100549251)

## 主要步骤
GarbageCollector Controller源码主要分为以下几部分：
 1. `monitors`作为生产者将变化的资源放入`graphChanges`队列；同时`restMapper`定期检测集群内资源类型，刷新`monitors`
 2. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToDelete`队列；
 3. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToOrphan`队列；
 4. `runAttemptToDeleteWorker`从`attemptToDelete`队列取出，尝试删除垃圾资源；
 5. `runAttemptToOrphanWorker`从`attemptToOrphan`队列取出，处理该孤立的资源；
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190903103422219.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
上一节分析了第2,3部分，本节分析第4、5部分。

## 终结器
**在阅读以下代码时，有必要先了解一下终结器。**

对象的终结器是在对象删除之前需要执行的逻辑，所有的对象在删除之前，它的终结器字段必须为空，终结器提供了一个通用的 API，它的功能不只是用于阻止级联删除，还能过通过它在对象删除之前加入钩子：
```go
type ObjectMeta struct {
	// ...
	Finalizers []string
}
```
终结器在对象被删之前运行，每当终结器成功运行之后，就会将它自己从 Finalizers 数组中删除，当最后一个终结器被删除之后，API Server 就会删除该对象。

在默认情况下，删除一个对象会删除它的全部依赖，但是我们在一些特定情况下我们只是想删除当前对象本身并不想造成复杂的级联删除，垃圾回收机制在这时引入了 OrphanFinalizer，它会在对象被删除之前向 Finalizers 数组添加或者删除 OrphanFinalizer。

该终结器会监听对象的更新事件并将它自己从它全部依赖对象的 OwnerReferences 数组中删除，与此同时会删除所有依赖对象中已经失效的 OwnerReferences 并将 OrphanFinalizer 从 Finalizers 数组中删除。

通过 OrphanFinalizer 我们能够在删除一个 Kubernetes 对象时保留它的全部依赖，为使用者提供一种更灵活的办法来保留和删除对象。

**同时，也希望可以看一下"垃圾回收"官网文档**：
[垃圾收集](https://kubernetes.io/zh/docs/concepts/workloads/controllers/garbage-collection/)

## attemptToDelete队列
来到代码$GOPATH\src\k8s.io\kubernetes\pkg\controller\garbagecollector\garbagecollector.go中：
```go
func (gc *GarbageCollector) runAttemptToDeleteWorker() {
	for gc.attemptToDeleteWorker() {
	}
}
```
从attemptToDelete队列中取出资源，调用gc.attemptToDeleteItem(n)处理，期间如果出现error，则通过rateLimited重新加回attemptToDelete队列。
```go
func (gc *GarbageCollector) attemptToDeleteWorker() bool {
	//从队列里取出需要尝试删除的资源
	item, quit := gc.attemptToDelete.Get()
	gc.workerLock.RLock()
	defer gc.workerLock.RUnlock()
	if quit {
		return false
	}
	defer gc.attemptToDelete.Done(item)
	n, ok := item.(*node)
	if !ok {
		utilruntime.HandleError(fmt.Errorf("expect *node, got %#v", item))
		return true
	}
	err := gc.attemptToDeleteItem(n)
	if err != nil {
		if _, ok := err.(*restMappingError); ok {
			// There are at least two ways this can happen:
			// 1. The reference is to an object of a custom type that has not yet been
			//    recognized by gc.restMapper (this is a transient error).
			// 2. The reference is to an invalid group/version. We don't currently
			//    have a way to distinguish this from a valid type we will recognize
			//    after the next discovery sync.
			// For now, record the error and retry.
			klog.V(5).Infof("error syncing item %s: %v", n, err)
		} else {
			utilruntime.HandleError(fmt.Errorf("error syncing item %s: %v", n, err))
		}
		// retry if garbage collection of an object failed.
		// 如果对象的垃圾收集失败，则重试。
		gc.attemptToDelete.AddRateLimited(item)
	} else if !n.isObserved() {
		// requeue if item hasn't been observed via an informer event yet.
		// otherwise a virtual node for an item added AND removed during watch reestablishment can get stuck in the graph and never removed.
		// see https://issue.k8s.io/56121
		klog.V(5).Infof("item %s hasn't been observed via informer yet", n.identity)
		gc.attemptToDelete.AddRateLimited(item)
	}
	return true
}
```
关键方法attemptToDeleteItem：
```go
func (gc *GarbageCollector) attemptToDeleteItem(item *node) error {
	klog.V(2).Infof("processing item %s", item.identity)
	// "being deleted" is an one-way trip to the final deletion. We'll just wait for the final deletion, and then process the object's dependents.
	// item资源被标记为正在删除,即deletionTimestamp不为nil;且不是正在删除从资源(这个从上一节可以看出,只有item被foreground方式删除时,deletingDependents才会被设置为true)
	// item在删除中,且为Orphan和Background方式删除则直接返回
	if item.isBeingDeleted() && !item.isDeletingDependents() {
		klog.V(5).Infof("processing item %s returned at once, because its DeletionTimestamp is non-nil", item.identity)
		return nil
	}
	// TODO: It's only necessary to talk to the API server if this is a
	// "virtual" node. The local graph could lag behind the real status, but in
	// practice, the difference is small.
	//根据item里的信息获取object对象体
	latest, err := gc.getObject(item.identity)
	switch {
	case errors.IsNotFound(err):
		// the GraphBuilder can add "virtual" node for an owner that doesn't
		// exist yet, so we need to enqueue a virtual Delete event to remove
		// the virtual node from GraphBuilder.uidToNode.
		klog.V(5).Infof("item %v not found, generating a virtual delete event", item.identity)
		gc.dependencyGraphBuilder.enqueueVirtualDeleteEvent(item.identity)
		// since we're manually inserting a delete event to remove this node,
		// we don't need to keep tracking it as a virtual node and requeueing in attemptToDelete
		item.markObserved()
		return nil
	case err != nil:
		return err
	}

	//uid不匹配
	if latest.GetUID() != item.identity.UID {
		klog.V(5).Infof("UID doesn't match, item %v not found, generating a virtual delete event", item.identity)
		gc.dependencyGraphBuilder.enqueueVirtualDeleteEvent(item.identity)
		// since we're manually inserting a delete event to remove this node,
		// we don't need to keep tracking it as a virtual node and requeueing in attemptToDelete
		//因为我们手动插入删除事件以删除此节点，我们不需要将其作为虚拟节点跟踪并在attemptToDelete中重新排队
		item.markObserved()
		return nil
	}

	// TODO: attemptToOrphanWorker() routine is similar. Consider merging
	// attemptToOrphanWorker() into attemptToDeleteItem() as well.
	// item的从资源正在删除中,同时删除其从资源
	if item.isDeletingDependents() {
		return gc.processDeletingDependentsItem(item)
	}

	// compute if we should delete the item
	// 获取该object里metadata.ownerReference
	// 计算我们是否应删除该项目
	ownerReferences := latest.GetOwnerReferences()
	if len(ownerReferences) == 0 {
		//没有owner的不用处理
		klog.V(2).Infof("object %s's doesn't have an owner, continue on next item", item.identity)
		return nil
	}

	//solid(owner存在,owner没被删或者终结器不为foregroundDeletion Finalizer); dangling(owner不存在)
	// waitingForDependentsDeletion(owner存在,owner的deletionTimestamp为非nil，并且有foregroundDeletion Finalizer)owner列表
	solid, dangling, waitingForDependentsDeletion, err := gc.classifyReferences(item, ownerReferences)
	if err != nil {
		return err
	}
	klog.V(5).Infof("classify references of %s.\nsolid: %#v\ndangling: %#v\nwaitingForDependentsDeletion: %#v\n", item.identity, solid, dangling, waitingForDependentsDeletion)

	switch {
	//item对象的owner存在,且不是正在删除
	case len(solid) != 0:
		klog.V(2).Infof("object %#v has at least one existing owner: %#v, will not garbage collect", solid, item.identity)
		if len(dangling) == 0 && len(waitingForDependentsDeletion) == 0 {
			return nil
		}
		klog.V(2).Infof("remove dangling references %#v and waiting references %#v for object %s", dangling, waitingForDependentsDeletion, item.identity)
		// waitingForDependentsDeletion needs to be deleted from the
		// ownerReferences, otherwise the referenced objects will be stuck with
		// the FinalizerDeletingDependents and never get deleted.
		// waitingForDependentsDeletion需要从 ownerReferences中删除，否则引用的对象将被
		// FinalizerDeletingDependents所卡住，并且永远不会被删除。
		//需要移除的ownerUids
		ownerUIDs := append(ownerRefsToUIDs(dangling), ownerRefsToUIDs(waitingForDependentsDeletion)...)
		//拼接patch请求参数
		patch := deleteOwnerRefStrategicMergePatch(item.identity.UID, ownerUIDs...)
		//发送patch请求
		_, err = gc.patch(item, patch, func(n *node) ([]byte, error) {
			return gc.deleteOwnerRefJSONMergePatch(n, ownerUIDs...)
		})
		return err
	//item对象的owner正在被删除; 且item有从资源
	case len(waitingForDependentsDeletion) != 0 && item.dependentsLength() != 0:
		deps := item.getDependents()
		// 遍历item从资源
		for _, dep := range deps {
			if dep.isDeletingDependents() {
				// this circle detection has false positives, we need to
				// apply a more rigorous detection if this turns out to be a
				// problem.
				// there are multiple workers run attemptToDeleteItem in
				// parallel, the circle detection can fail in a race condition.
				klog.V(2).Infof("processing object %s, some of its owners and its dependent [%s] have FinalizerDeletingDependents, to prevent potential cycle, its ownerReferences are going to be modified to be non-blocking, then the object is going to be deleted with Foreground", item.identity, dep.identity)
				// 生成一个补丁，该补丁会取消设置item所有ownerReferences的BlockOwnerDeletion字段,避免阻塞item的owner删除
				patch, err := item.unblockOwnerReferencesStrategicMergePatch()
				if err != nil {
					return err
				}
				//执行patch
				if _, err := gc.patch(item, patch, gc.unblockOwnerReferencesJSONMergePatch); err != nil {
					return err
				}
				break
			}
		}
		//item对象的至少一个owner具有foregroundDeletion Finalizer，并且该对象本身具有依赖项，因此它将在Foreground中删除
		klog.V(2).Infof("at least one owner of object %s has FinalizerDeletingDependents, and the object itself has dependents, so it is going to be deleted in Foreground", item.identity)
		// the deletion event will be observed by the graphBuilder, so the item
		// will be processed again in processDeletingDependentsItem. If it
		// doesn't have dependents, the function will remove the
		// FinalizerDeletingDependents from the item, resulting in the final
		// deletion of the item.
		// graphBuilder将观察删除事件，因此将在processDeletingDependentsItem中再次处理该项目。
		// 如果没有依赖项，该函数将从项中删除foregroundDeletion Finalizer，最终删除item。
		policy := metav1.DeletePropagationForeground
		return gc.deleteObject(item.identity, &policy)
	default:
		// item doesn't have any solid owner, so it needs to be garbage
		// collected. Also, none of item's owners is waiting for the deletion of
		// the dependents, so set propagationPolicy based on existing finalizers.
		// item没有任何实体所有者，因此需要收集垃圾 。此外，项目的所有者都没有等待删除
		// 依赖项，因此请根据现有的终结器设置propagationPolicy。
		var policy metav1.DeletionPropagation
		switch {
		case hasOrphanFinalizer(latest):
			// if an existing orphan finalizer is already on the object, honor it.
			//如果现有的孤儿终结器已经在对象上，请尊重它。
			policy = metav1.DeletePropagationOrphan
		case hasDeleteDependentsFinalizer(latest):
			// if an existing foreground finalizer is already on the object, honor it.
			//如果现有的前景终结器已经在对象上，请尊重它。
			policy = metav1.DeletePropagationForeground
		default:
			// otherwise, default to background.
			//否则，默认为背景。
			policy = metav1.DeletePropagationBackground
		}
		klog.V(2).Infof("delete object %s with propagation policy %s", item.identity, policy)
		//删除孤儿对象
		return gc.deleteObject(item.identity, &policy)
	}
}
```
主要做以下事情：
1、item在删除中，且为Orphan和Background方式删除则直接返回；
2、item是foreground方式删除时，调用processDeletingDependentsItem去处理阻塞其删除的从资源，将其放到attemptToDelete队列；
3、获取item的owner对象集，调用classifyReferences将owner集合分为3类，分别为solid（owner存在或者终结器不为foregroundDeletion的owner集合）, dangling（已经不存在了的owner集群）, waitingForDependentsDeletion（owner的deletionTimestamp为非nil，并且为foregroundDeletion终结器的owner集合）
4、switch第一个case：solid集合不为空，即item存在没被删除的owner。当dangling和waitingForDependentsDeletion都为空，则直接返回；当dangling或waitingForDependentsDeletion不为空，合并两个集合uid，执行patch请求，将这些uid对应的ownerReferences从item中删除
5、switch第二个case：waitingForDependentsDeletion集合不为空，且item有从资源。即item的owner不存在，或正在被foregroundDeletion方式删除，如果item的从资源正在删除依赖项，则取消阻止item的owner删除，给item执行patch请求，最终采用foregroundDeletion方式删除item；
6、switch第三个case：以上条件不符合时，则直接根据item中的终结器删除item，默认为Background方式删除。

----
往细了说，processDeletingDependentsItem方法获取item从资源中BlockOwnerDeletion为true的ownerReferences集合，如果为空，则移除item的foregroundDeletion终结器。否则遍历，将未开始删除的依赖项的从资源dep加入到尝试删除队列attemptToDelete。
```go
//等待其依赖项被删除的进程项
func (gc *GarbageCollector) processDeletingDependentsItem(item *node) error {
	//阻塞item资源删除的从资源列表
	blockingDependents := item.blockingDependents()
	//没有阻塞item资源删除的从资源,则移除item资源的foregroundDeletion终结器
	if len(blockingDependents) == 0 {
		klog.V(2).Infof("remove DeleteDependents finalizer for item %s", item.identity)
		return gc.removeFinalizer(item, metav1.FinalizerDeleteDependents)
	}
	//遍历阻塞item资源删除的从资源
	for _, dep := range blockingDependents {
		// 如果dep的从资源没有开始删除,则将dep加入到尝试删除队列中
		if !dep.isDeletingDependents() {
			klog.V(2).Infof("adding %s to attemptToDelete, because its owner %s is deletingDependents", dep.identity, item.identity)
			//将从资源加入删除队列
			gc.attemptToDelete.Add(dep)
		}
	}
	return nil
}
```
gc.classifyReferences(item, ownerReferences)方法：遍历了item的owner列表，调用isDangling方法将已不存在的owner加入到isDangling列表；owner正在被删除,且owner有foregroundDeletion终结器的加入到waitingForDependentsDeletion列表；owner没开始删或者终结器不为foregroundDeletion的加入到solid列表。
```go
// 将latestReferences分为三类：
// solid：所有者存在，且不是waitingForDependentsDeletion
// dangling悬空：所有者不存在
// waitingForDependentsDeletion: 所有者存在，其deletionTimestamp为非nil，并且有FinalizerDeletingDependents
func (gc *GarbageCollector) classifyReferences(item *node, latestReferences []metav1.OwnerReference) (
	solid, dangling, waitingForDependentsDeletion []metav1.OwnerReference, err error) {
	//遍历该node的owner
	for _, reference := range latestReferences {
		//获取owner是否存在;isDangling为true表示不存在,发生err则最终将该item加入AddRateLimited attemptToDelete队列
		isDangling, owner, err := gc.isDangling(reference, item)
		if err != nil {
			return nil, nil, nil, err
		}
		//将不存在的owner加入dangling切片
		if isDangling {
			dangling = append(dangling, reference)
			continue
		}

		//owner存在,获取accessor
		ownerAccessor, err := meta.Accessor(owner)
		if err != nil {
			return nil, nil, nil, err
		}
		//owner正在被删除,且owner有foregroundDeletion Finalizer
		if ownerAccessor.GetDeletionTimestamp() != nil && hasDeleteDependentsFinalizer(ownerAccessor) {
			//owner将等待依赖删除;收集等待删除依赖的owner列表
			waitingForDependentsDeletion = append(waitingForDependentsDeletion, reference)
		} else {
			//owner没被删或者终结器不为foregroundDeletion Finalizer
			solid = append(solid, reference)
		}
	}
	return solid, dangling, waitingForDependentsDeletion, nil
}
```
gc.isDangling(reference, item)方法：先从absentOwnerCache缓存中根据owner uid获取owner是否存在；如果缓存中没有，则根据ownerReferences中的参数，构建参数，调用apiserver接口获取owner对象是否能查到。查到如果uid不匹配，加入absentOwnerCache缓存，并返回false。
```go
// isDangling检查引用是否指向不存在的对象。 如果isDangling在API服务器上查找引用的对象，它也返回其最新状态。
func (gc *GarbageCollector) isDangling(reference metav1.OwnerReference, item *node) (
	dangling bool, owner *unstructured.Unstructured, err error) {
	if gc.absentOwnerCache.Has(reference.UID) {
		klog.V(5).Infof("according to the absentOwnerCache, object %s's owner %s/%s, %s does not exist", item.identity.UID, reference.APIVersion, reference.Kind, reference.Name)
		return true, nil, nil
	}
	// TODO: we need to verify the reference resource is supported by the
	// system. If it's not a valid resource, the garbage collector should i)
	// ignore the reference when decide if the object should be deleted, and
	// ii) should update the object to remove such references. This is to
	// prevent objects having references to an old resource from being
	// deleted during a cluster upgrade.
	resource, namespaced, err := gc.apiResource(reference.APIVersion, reference.Kind)
	if err != nil {
		return false, nil, err
	}

	// TODO: It's only necessary to talk to the API server if the owner node
	// is a "virtual" node. The local graph could lag behind the real
	// status, but in practice, the difference is small.
	owner, err = gc.dynamicClient.Resource(resource).Namespace(resourceDefaultNamespace(namespaced, item.identity.Namespace)).Get(reference.Name, metav1.GetOptions{})
	switch {
	case errors.IsNotFound(err):
		gc.absentOwnerCache.Add(reference.UID)
		klog.V(5).Infof("object %s's owner %s/%s, %s is not found", item.identity.UID, reference.APIVersion, reference.Kind, reference.Name)
		return true, nil, nil
	case err != nil:
		return false, nil, err
	}

	if owner.GetUID() != reference.UID {
		klog.V(5).Infof("object %s's owner %s/%s, %s is not found, UID mismatch", item.identity.UID, reference.APIVersion, reference.Kind, reference.Name)
		gc.absentOwnerCache.Add(reference.UID)
		return true, nil, nil
	}
	return false, owner, nil
}
```

## attemptToOrphan队列
来到代码：
```go
func (gc *GarbageCollector) runAttemptToOrphanWorker() {
	for gc.attemptToOrphanWorker() {
	}
}
```
死循环一直从attemptToOrphan队列中获取item资源，调用gc.orphanDependents(owner.identity, dependents)方法，从item从资源中删掉该item的ownerReferences，期间如果发生错误，则通过rateLimited重新加回attemptToOrphan队列。最后移除item中的orphan终结器。
```go
// attemptToOrphanWorker将一个节点从attemptToOrphan中取出，然后根据GC维护的图找到它的依赖项，然后将其从其依赖项的
// OwnerReferences中删除，最后更新item以删除孤儿终结器。如果这些步骤中的任何一个失败，则将节点添加回attemptToOrphan。
func (gc *GarbageCollector) attemptToOrphanWorker() bool {
	item, quit := gc.attemptToOrphan.Get()
	gc.workerLock.RLock()
	defer gc.workerLock.RUnlock()
	if quit {
		return false
	}
	defer gc.attemptToOrphan.Done(item)
	owner, ok := item.(*node)
	if !ok {
		utilruntime.HandleError(fmt.Errorf("expect *node, got %#v", item))
		return true
	}
	// we don't need to lock each element, because they never get updated
	owner.dependentsLock.RLock()
	dependents := make([]*node, 0, len(owner.dependents))
	for dependent := range owner.dependents {
		dependents = append(dependents, dependent)
	}
	owner.dependentsLock.RUnlock()
	// 处理孤儿
	err := gc.orphanDependents(owner.identity, dependents)
	if err != nil {
		utilruntime.HandleError(fmt.Errorf("orphanDependents for %s failed with %v", owner.identity, err))
		gc.attemptToOrphan.AddRateLimited(item)
		return true
	}
	// update the owner, remove "orphaningFinalizer" from its finalizers list
	// 移除item的orphan终结器
	err = gc.removeFinalizer(owner, metav1.FinalizerOrphanDependents)
	if err != nil {
		utilruntime.HandleError(fmt.Errorf("removeOrphanFinalizer for %s failed with %v", owner.identity, err))
		gc.attemptToOrphan.AddRateLimited(item)
	}
	return true
}
```
gc.orphanDependents(owner.identity, dependents)方法：遍历item的从资源，并发的执行patch请求，删除从资源中和item同uid的ownerReferences，将error加入到errCh channel中，最后给调用者返回error列表：
```go
// dependents are copies of pointers to the owner's dependents, they don't need to be locked.
func (gc *GarbageCollector) orphanDependents(owner objectReference, dependents []*node) error {
	errCh := make(chan error, len(dependents))
	wg := sync.WaitGroup{}
	wg.Add(len(dependents))
	for i := range dependents {
		go func(dependent *node) {
			defer wg.Done()
			// the dependent.identity.UID is used as precondition
			patch := deleteOwnerRefStrategicMergePatch(dependent.identity.UID, owner.UID)
			_, err := gc.patch(dependent, patch, func(n *node) ([]byte, error) {
				return gc.deleteOwnerRefJSONMergePatch(n, owner.UID)
			})
			// note that if the target ownerReference doesn't exist in the
			// dependent, strategic merge patch will NOT return an error.
			if err != nil && !errors.IsNotFound(err) {
				errCh <- fmt.Errorf("orphaning %s failed, %v", dependent.identity, err)
			}
		}(dependents[i])
	}
	wg.Wait()
	close(errCh)

	var errorsSlice []error
	for e := range errCh {
		errorsSlice = append(errorsSlice, e)
	}

	if len(errorsSlice) != 0 {
		return fmt.Errorf("failed to orphan dependents of owner %s, got errors: %s", owner, utilerrors.NewAggregate(errorsSlice).Error())
	}
	klog.V(5).Infof("successfully updated all dependents of owner %s", owner)
	return nil
}
```
deleteOwnerRefStrategicMergePatch方法：拼接patch请求参数。该方法同样的，在处理attemptToDelete死循中，第一个switch case处被调用。
```go
func deleteOwnerRefStrategicMergePatch(dependentUID types.UID, ownerUIDs ...types.UID) []byte {
	var pieces []string
	//拼接需要删除的uid
	for _, ownerUID := range ownerUIDs {
		pieces = append(pieces, fmt.Sprintf(`{"$patch":"delete","uid":"%s"}`, ownerUID))
	}
	//拼接patch请求参数
	patch := fmt.Sprintf(`{"metadata":{"ownerReferences":[%s],"uid":"%s"}}`, strings.Join(pieces, ","), dependentUID)
	return []byte(patch)
}
```

## 回到初衷
中间件redis容器化后，在测试环境上部署的redis集群，在kubernetes apiserver重启后，redis集群被异常删除（包括redis exporter statefulset、redis statefulset）。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154538243.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
### 原因定位
在开发环境上经多次复现，apiserver重启后，通过查询redis operator日志，并没有发现主动去删除redis集群（redis statefulset）、监控实例（redis exporter）。进一步去查看kube-controller-manager的日志，将其日志级别设置--v=5，继续复现，最终在kube-controller-manager日志中发现如下日志：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154548906.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

可以看到，垃圾回收器garbage collector在处理redis exporter statefulset时，发现其加了ownerReferences，在exporter所在分区（monitoring）查询其owner——redisCluster对象redis-0826，而redisCluster对象redis-0826存在于kube-system分区，所以在monitoring分区查询到的是404 Not Found，garbage collector会将该owner不存在信息（uid）存入缓存absentOwnerCache。
因redis exporter statefulset的owner不存在，所以gc认为需要回收垃圾，故将其删除掉。同理，当处理redis statefulset时，从缓存中发现owner不存在，也会回收垃圾，将其删除掉。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154600217.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
 
经过多次复现故障，发现重启kube-controller-manager时有概率复现。（Apiserver的重启时，kube-controller-manager在连接apiserver失败多次后，也会发生自重启），之所以是概率问题，这和garbage collector将资源对象加入attemptToDelete队列的顺序有关：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154616873.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
 
先同步monitoring分区的exporter statefulset，后同步kube-system分区的redis statefulset，就会出现该故障；反之就不会出现故障，这取决于garbage collector启动时全量获取集群内资源（listwatch）的顺序。
在apiserver和kube-controller-manager正常运行时不出现该故障，可以从garbage collector源码中看到以下代码逻辑：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154641446.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154650524.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
Garbage collector中维护一个父子关系图表，controller-manager启动时该图里节点是不存在的，会走上图switch的第一个case，之后图形成之后，会走第二个case。第二个case里只有在owner发生变化时才会触发将资源对象加入attemptToDelete队列，所以在各个组件正常运行时没有出现该故障。

获取图表的接口地址，IP和端口都是controller-manager的，可以重定向到tmp.dot文件
```shell
curl http://127.0.0.1:10252/debug/controllers/garbagecollector/graph

curl http://127.0.0.1:10252/debug/controllers/garbagecollector/graph?uid=11211212edsaddkqedmk12
```
之后用可视化工具Graphviz软件，进入到bin目录下，执行以下命令生成svg文件，用浏览器打开，Graphviz和dot的使用可以自行谷歌。
```shell
dot -Tsvg -o graph2.svg tmp.dot
```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154706864.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154726832.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

### 解决方法
在redis operator创建redis集群时，将exporter放到和redis同一分区。
### 思考反思
1、出现该故障，主要是因进行了跨命名空间owner引用。在使用垃圾回收机制时，应该尽量参考kubernetes官方网站中的说明.
如下，官网中说明了owner引用在设计时就不允许跨namespace使用，这意味着：

1）命名空间范围的从属只能指定同一命名空间中的所有者，以及群集范围的所有者。

2）群集作用域的从属只能指定群集作用域的所有者，而不能指定命名空间作用域的所有者。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191021154741284.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
## 参考文档
垃圾回收官方文档：

https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/

详解 Kubernetes 垃圾收集器的实现原理：

https://draveness.me/kubernetes-garbage-collector#


* * *

**本公众号**免费**提供csdn下载服务，海量IT学习资源，**如果你准备入IT坑，励志成为优秀的程序猿，那么这些资源很适合你，包括但不限于java、go、python、springcloud、elk、嵌入式 、大数据、面试资料、前端 等资源。同时我们组建了一个技术交流群，里面有很多大佬，会不定时分享技术文章，如果你想来一起学习提高，可以公众号后台回复【**2**】，免费邀请加技术交流群互相学习提高，会不定期分享编程IT相关资源。

* * *

扫码关注，精彩内容第一时间推给你

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTYzZTRkMDc2OWM2MGUyODY)
