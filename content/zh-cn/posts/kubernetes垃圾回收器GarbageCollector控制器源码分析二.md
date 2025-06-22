---
title: kubernetes垃圾回收器GarbageCollector控制器源码分析（二）
date: '2019-10-16 23:29:12'
updated: '2019-10-22 19:40:05'
tags: [kubernetes]
permalink: /201910162329kube
---
![](https://img.hacpai.com/bing/20190103.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)

> **kubernetes版本：1.13.2**

接上一节：[kubernetes垃圾回收器GarbageCollector Controller源码分析（一）](https://liabio.blog.csdn.net/article/details/100081941)

## 主要步骤
GarbageCollector Controller源码主要分为以下几部分：
 1. `monitors`作为生产者将变化的资源放入`graphChanges`队列；同时`restMapper`定期检测集群内资源类型，刷新`monitors`
 2. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToDelete`队列；
 3. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToOrphan`队列；
 4. `runAttemptToDeleteWorker`从`attemptToDelete`队列取出，尝试删除垃圾资源；
 5. `runAttemptToOrphanWorker`从`attemptToOrphan`队列取出，处理该孤立的资源；
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190903103422219.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
代码较复杂，便于讲的更清楚，调整了下讲解顺序。上一节分析了第1部分，本节分析第2、3部分。

## runProcessGraphChanges处理主流程
来到源码k8s.io\kubernetes\pkg\controller\garbagecollector\graph_builder.go中，runProcessGraphChanges中一直死循环处理变化的资源对象：

```go
func (gb *GraphBuilder) runProcessGraphChanges() {
	for gb.processGraphChanges() {
	}
}
```
一个协程一直循环从graphChanges队列中获取变化的资源对象，更新图形，填充dirty_queue。(graphChanges队列里数据来源于各个资源的monitors监听资源变化回调addFunc、updateFunc、deleteFunc)
```go
// Dequeueing an event from graphChanges, updating graph, populating dirty_queue.
//从graphChanges中获取事件，更新图形，填充dirty_queue。(graphChanges队列里数据来源于各个资源的monitors监听资源变化回调addFunc、updateFunc、deleteFunc)
func (gb *GraphBuilder) processGraphChanges() bool {
	item, quit := gb.graphChanges.Get()
	if quit {
		return false
	}
	defer gb.graphChanges.Done(item)
	event, ok := item.(*event)
	if !ok {
		utilruntime.HandleError(fmt.Errorf("expect a *event, got %v", item))
		return true
	}
	obj := event.obj
	//获取该变化资源obj的accessor
	accessor, err := meta.Accessor(obj)
	if err != nil {
		utilruntime.HandleError(fmt.Errorf("cannot access obj: %v", err))
		return true
	}
	klog.V(5).Infof("GraphBuilder process object: %s/%s, namespace %s, name %s, uid %s, event type %v", event.gvk.GroupVersion().String(), event.gvk.Kind, accessor.GetNamespace(), accessor.GetName(), string(accessor.GetUID()), event.eventType)
	// Check if the node already exists
	// 检查节点是否已存在
	//根据该变化资源obj的UID
	//uidToNode维护着资源对象依赖关系图表结构
	existingNode, found := gb.uidToNode.Read(accessor.GetUID())
	if found {
		// this marks the node as having been observed via an informer event
		// 1. this depends on graphChanges only containing add/update events from the actual informer
		// 2. this allows things tracking virtual nodes' existence to stop polling and rely on informer events
	    //这标志着节点已经通过informer事件
		// 1.进行了观察。这取决于仅包含来自实际informer的添加/更新事件的graphChange
		// 2.这允许跟踪虚拟节点的存在以停止轮询和依赖informer事件
		existingNode.markObserved()
	}
	switch {
	//gc第一次运行时，uidToNode尚且没有初始化资源对象依赖关系图表结构，所以found为false，会新增节点
	case (event.eventType == addEvent || event.eventType == updateEvent) && !found:
		newNode := &node{
			identity: objectReference{
				OwnerReference: metav1.OwnerReference{
					APIVersion: event.gvk.GroupVersion().String(),
					Kind:       event.gvk.Kind,
					UID:        accessor.GetUID(),
					Name:       accessor.GetName(),
				},
				Namespace: accessor.GetNamespace(),
			},
			dependents:         make(map[*node]struct{}),
			owners:             accessor.GetOwnerReferences(),
			deletingDependents: beingDeleted(accessor) && hasDeleteDependentsFinalizer(accessor),
			beingDeleted:       beingDeleted(accessor),
		}
		gb.insertNode(newNode)
		// the underlying delta_fifo may combine a creation and a deletion into
		// one event, so we need to further process the event.
		//底层delta_fifo可以将创建和删除组合成一个事件，因此我们需要进一步处理事件。
		gb.processTransitions(event.oldObj, accessor, newNode)
	//uidToNode已经初始化资源对象依赖关系图表结构，所以found为true
	case (event.eventType == addEvent || event.eventType == updateEvent) && found:
		// handle changes in ownerReferences
		//处理ownerReferences中的更改
		added, removed, changed := referencesDiffs(existingNode.owners, accessor.GetOwnerReferences())
		if len(added) != 0 || len(removed) != 0 || len(changed) != 0 {
			// check if the changed dependency graph unblock owners that are
			// waiting for the deletion of their dependents.
			//检查更改的依赖关系图是否取消阻止等待删除其依赖项的所有者。
			gb.addUnblockedOwnersToDeleteQueue(removed, changed)
			// update the node itself
			//更新node的owner
			existingNode.owners = accessor.GetOwnerReferences()
			// Add the node to its new owners' dependent lists.
			//给新owner添加依赖资源列表
			gb.addDependentToOwners(existingNode, added)
			// remove the node from the dependent list of node that are no longer in
			// the node's owners list.
			//从不再属于该资源owner列表中删除该节点。
			gb.removeDependentFromOwners(existingNode, removed)
		}

		// 该对象正在被删除中
		if beingDeleted(accessor) {
			existingNode.markBeingDeleted()
		}
		gb.processTransitions(event.oldObj, accessor, existingNode)
	//处理资源对象被删除的场景，涉及垃圾。比如，owner被删除，其依赖资源（从资源）也需要被删除掉，除非设置了Orphan
	case event.eventType == deleteEvent:
		if !found {
			klog.V(5).Infof("%v doesn't exist in the graph, this shouldn't happen", accessor.GetUID())
			return true
		}
		// 从图标中移除item资源，同时遍历owners，移除owner下的item资源
		gb.removeNode(existingNode)
		existingNode.dependentsLock.RLock()
		defer existingNode.dependentsLock.RUnlock()
		//如果该资源的从资源数大于0,则将该资源被删除信息加入absentOwnerCache缓存
		if len(existingNode.dependents) > 0 {
			gb.absentOwnerCache.Add(accessor.GetUID())
		}
		//遍历该资源的从资源加到删除队列里
		for dep := range existingNode.dependents {
			gb.attemptToDelete.Add(dep)
		}
		for _, owner := range existingNode.owners {
			ownerNode, found := gb.uidToNode.Read(owner.UID)
			//owner没发现 或者 owner的从资源不是正在被删除(只有该资源对象的终结器为foregroundDeletion Finalizer时deletingDependents被设为true,因为后台删除owner直接被删除,不会被其从资源block,故这里都不需要去尝试删除owner了)
			if !found || !ownerNode.isDeletingDependents() {
				continue
			}
			
			// 这是让attempToDeleteItem检查是否删除了owner的依赖项，如果是，则删除所有者。
			gb.attemptToDelete.Add(ownerNode)
		}
	}
	return true
}
```
该方法功能主要将对象、owner、从资源加入到attemptToDelete或attemptToOrphan。

### 1、 出队
从graphChanges队列取出资源对象，从GraphBuilder.uidToNode中读取该资源节点（uidToNode维护着资源对象依赖关系图表结构），found为true时表示图表存在该资源节点；


### 2、switch的第一个case
如果该资源是新增或者更新触发，且该资源对象不存在于图表中，gb.uidToNode.Write(n)会将其写入图标；
gb.insertNode(newNode)中的gb.addDependentToOwners(n, n.owners)方法则会遍历该资源的owner，如果其owner不存在于图标中，则新增owner的虚拟节点到图标中，并将该资源和owner产生关联。如果owner不存在时，则尝试将owner加入到attemptToDelete队列中去；
```go
// addDependentToOwners将n添加到所有者的从属列表中。如果所有者不存在于gb.uidToNode中，则将创建"虚拟"节点以表示
// 所有者。 "虚拟"节点将入队到attemptToDelete，因此
// attemptToDeleteItem()将根据API服务器验证所有者是否存在。
func (gb *GraphBuilder) addDependentToOwners(n *node, owners []metav1.OwnerReference) {
	//遍历owner
	for _, owner := range owners {
		//获取owner node如果不存在于图中,则加虚拟owner节点
		ownerNode, ok := gb.uidToNode.Read(owner.UID)
		if !ok {
			// Create a "virtual" node in the graph for the owner if it doesn't
			// exist in the graph yet.
			//如果图形中尚未存在，则在图表中为所有者创建“虚拟”节点。
			ownerNode = &node{
				identity: objectReference{
					OwnerReference: owner,
					Namespace:      n.identity.Namespace,
				},
				dependents: make(map[*node]struct{}),
				virtual:    true,
			}
			klog.V(5).Infof("add virtual node.identity: %s\n\n", ownerNode.identity)
			gb.uidToNode.Write(ownerNode)
		}
		//给owner加该资源作为依赖
		ownerNode.addDependent(n)
		//owner不存在于图中时，才往删除队列添加
		if !ok {
			// Enqueue the virtual node into attemptToDelete.
			// The garbage processor will enqueue a virtual delete
			// event to delete it from the graph if API server confirms this
			// owner doesn't exist.
			//将虚拟节点排入attemptToDelete。
			// 如果API服务器确认owner不存在，垃圾处理器将排队虚拟删除事件以将其从图中删除。
			gb.attemptToDelete.Add(ownerNode)
		}
	}
}

```
gb.processTransitions方法：
新item正在被删,旧item没开始被删除,且终结器为Orphan Finalizer加入到attemptToOrphan队列；
新item正在被删,旧item没开始被删除,且终结器为foregroundDeletion Finalizer，则加入到attemptToDelete队列。
```go
func (gb *GraphBuilder) processTransitions(oldObj interface{}, newAccessor metav1.Object, n *node) {
	//新的正在被删,旧的没开始被删除,且终结器为Orphan Finalizer
	if startsWaitingForDependentsOrphaned(oldObj, newAccessor) {
		klog.V(5).Infof("add %s to the attemptToOrphan", n.identity)
		//加入到Orphan队列
		gb.attemptToOrphan.Add(n)
		return
	}

	//新的正在被删,旧的没开始被删除,且终结器为foregroundDeletion Finalizer
	if startsWaitingForDependentsDeleted(oldObj, newAccessor) {
		klog.V(2).Infof("add %s to the attemptToDelete, because it's waiting for its dependents to be deleted", n.identity)
		// if the n is added as a "virtual" node, its deletingDependents field is not properly set, so always set it here.
		n.markDeletingDependents()
		for dep := range n.dependents {
			gb.attemptToDelete.Add(dep)
		}
		gb.attemptToDelete.Add(n)
	}
}
```



### 3、switch的第二个case
如果该资源是新增或者更新触发，且该资源对象存在于图表中。对比owneReferences是否有变更，referencesDiffs方法里会根据uid对比，added表示新owner里有,旧owner里没有的, removed表示旧owner里有,新owner里没有的, changed表示相同uid的owner不deepEqual的。
```go
func referencesDiffs(old []metav1.OwnerReference, new []metav1.OwnerReference) (added []metav1.OwnerReference, removed []metav1.OwnerReference, changed []ownerRefPair) {
	//key为uid, value为OwnerReference
	oldUIDToRef := make(map[string]metav1.OwnerReference)
	for _, value := range old {
		oldUIDToRef[string(value.UID)] = value
	}
	oldUIDSet := sets.StringKeySet(oldUIDToRef)

	//key为uid, value为OwnerReference
	newUIDToRef := make(map[string]metav1.OwnerReference)
	for _, value := range new {
		newUIDToRef[string(value.UID)] = value
	}
	newUIDSet := sets.StringKeySet(newUIDToRef)

	//新的里有,旧的里没有的为新增(根据uid判断)
	addedUID := newUIDSet.Difference(oldUIDSet)

	//旧的里有,新的里没有的为删除(根据uid判断)
	removedUID := oldUIDSet.Difference(newUIDSet)

	//取交集, 旧的和新的里都有的owner(根据uid判断)
	intersection := oldUIDSet.Intersection(newUIDSet)

	for uid := range addedUID {
		added = append(added, newUIDToRef[uid])
	}
	for uid := range removedUID {
		removed = append(removed, oldUIDToRef[uid])
	}

	//根据uid判断,两个uid相等的OwnerReference是否deepEqual,不等则加到changed
	for uid := range intersection {
		if !reflect.DeepEqual(oldUIDToRef[uid], newUIDToRef[uid]) {
			changed = append(changed, ownerRefPair{oldRef: oldUIDToRef[uid], newRef: newUIDToRef[uid]})
		}
	}
	return added, removed, changed
}
```
整体来说，owner发生变化，addUnblockedOwnersToDeleteQueue方法会判断：如果阻塞ownerReference指向某个对象被删除，或者设置为`BlockOwnerDeletion=false`，则将该对象添加到attemptToDelete队列；
```go
// if an blocking ownerReference points to an object gets removed, or gets set to
// "BlockOwnerDeletion=false", add the object to the attemptToDelete queue.
//如果阻塞ownerReference指向某个对象被删除，或者设置为
// "BlockOwnerDeletion = false"，则将该对象添加到attemptToDelete队列。
func (gb *GraphBuilder) addUnblockedOwnersToDeleteQueue(removed []metav1.OwnerReference, changed []ownerRefPair) {
	for _, ref := range removed {
		//被移除的OwnersReferences,BlockOwnerDeletion为true
		if ref.BlockOwnerDeletion != nil && *ref.BlockOwnerDeletion {
			//依赖图表中发现,则加入删除队列
			node, found := gb.uidToNode.Read(ref.UID)
			if !found {
				klog.V(5).Infof("cannot find %s in uidToNode", ref.UID)
				continue
			}
			//加入尝试删除队列删除这个owner
			gb.attemptToDelete.Add(node)
		}
	}

	// Owners存在且发生变化,旧的BlockOwnerDeletion为true, 新的BlockOwnerDeletion为空或者BlockOwnerDeletion为false则删除owner(父节点)
	for _, c := range changed {
		wasBlocked := c.oldRef.BlockOwnerDeletion != nil && *c.oldRef.BlockOwnerDeletion
		isUnblocked := c.newRef.BlockOwnerDeletion == nil || (c.newRef.BlockOwnerDeletion != nil && !*c.newRef.BlockOwnerDeletion)
		if wasBlocked && isUnblocked {
			node, found := gb.uidToNode.Read(c.newRef.UID)
			if !found {
				klog.V(5).Infof("cannot find %s in uidToNode", c.newRef.UID)
				continue
			}
			gb.attemptToDelete.Add(node)
		}
	}
}
```
更新node的owner；
在依赖图表中给新owner添加该node；
在依赖图表中,被删除的owner列表下删除该节点。

gb.processTransitions方法：
新item正在被删,旧item没开始被删除,且终结器为Orphan Finalizer加入到attemptToOrphan队列；
新item正在被删,旧item没开始被删除,且终结器为foregroundDeletion Finalizer，则加入到attemptToDelete队列。


### 4、switch的第三个case
如果该资源是删除时触发，从图表中移除item资源，同时遍历owners，移除owner下的item资源；
如果该资源的从资源数大于0,则将该资源被删除信息（uid）加入absentOwnerCache缓存，这样处理该资源的从资源时，就知道owner不存在了。
遍历该资源的从资源加到删除队列里；
如果从图表中发现 owner或者 owner的从资源正在被删除，则尝试将owner加入到attemptToDelete队列中，去尝试删除owner。

## 整理流程

 - 当controllermanager重启时，会全量listwatch一遍所有对象，gc collector维护的uidToNode图表里各个资源对象node是不存在的，此时会走第一个switch case，构建完整关系图表，如果owner不存在则先构建虚拟owner节点，同时加入attemptToDelete队列，尝试去删除这个owner，其实即使加入到attemptToDelete队列，也不一定会被删除，还会进行一系列判断，这个下一节再分析；将正在删除的资源，同时Finalizer为Orphan的加入到attemptToOrphan队列；为foreground的资源以及其从资源加入到attemptToDelete队列，并将deletingDependents设置为true；
 - 添加或者更新事件时，且图表中存在item资源对象时，会走第二个switch case，对item的owner变化进行判断，并维护更新图表；同理将正在删除的资源，同时Finalizer为Orphan的加入到attemptToOrphan队列；Finalizer为foreground的资源以及其从资源加入到attemptToDelete队列，并将deletingDependents设置为true；
 - 如果是删除事件，则会更新图表，并处理和其相关的从资源和其owner加入到attemptToDelete队列。


## 参考：

k8s官方文档garbage-collection英文版：
https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/

依赖图标生成库gonum Api文档：
https://godoc.org/gonum.org/v1/gonum/graph

graphviz下载：
https://graphviz.gitlab.io/_pages/Download/Download_windows.html


