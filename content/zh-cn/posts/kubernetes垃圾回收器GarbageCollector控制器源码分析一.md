---
title: kubernetes垃圾回收器GarbageCollector控制器源码分析（一）
date: '2019-10-16 23:14:24'
updated: '2019-10-22 19:40:57'
tags: [kubernetes]
permalink: /201910162317kube
---
![](https://img.hacpai.com/bing/20190604.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)



> **kubernetes版本：1.13.2**

## 背景
由于operator创建的redis集群，在kubernetes apiserver重启后，redis集群被异常删除（包括redis exporter statefulset、redis statefulset）。删除后operator将其重建，重新组建集群，实例IP发生变更（中间件容器化，我们开发了固定IP，当statefulset删除后，IP会被回收），导致创建集群失败，最终集群不可用。

经多次复现，apiserver重启后，通过查询redis operator日志，并没有发现主动去删除redis集群（redis statefulset）、监控实例（redis exporter）。进一步去查看kube-controller-manager的日志，将其日志级别设置--v=5，继续复现，最终在kube-controller-manager日志中发现如下日志：
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/2019090122334772.png)
可以看到是garbage collector触发删除操作的。这个问题在apiserver正常的时候是不存在，要想弄其究竟，就得看看kube-controller-manager内置组件garbage collector这个控制器的逻辑。

**由于内容偏长，分为多节来讲：**
 1. `monitors`作为生产者将变化的资源放入`graphChanges`队列；同时`restMapper`定期检测集群内资源类型，刷新`monitors`
 2. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToDelete`队列；
 3. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToOrphan`队列；
 4. `runAttemptToDeleteWorker`从`attemptToDelete`队列取出，尝试删除垃圾资源；
 5. `runAttemptToOrphanWorker`从`attemptToOrphan`队列取出，处理该孤立的资源；
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190903103422219.png)

---

## 正文

想要启用`GC`，需要在`kube-apiserver`和`kube-controller-manager`的启动参数中都设置`--enable-garbage-collector`为`true`,`1.13.2`版本中默认开启`GC`。

**需要注意：两组件该参数必须保持同步。**

----
`kube-controller-manager`启动入口，`app.NewControllerManagerCommand()`中加载`controller manage`r默认启动参数，创建`* cobra.Command`对象：

```go
func main() {
    	rand.Seed(time.Now().UnixNano())
    	//加载controller manager默认启动参数，创建* cobra.Command对象
    	command := app.NewControllerManagerCommand()
    	//......省略.......
    	//执行cobra.command，并启动controller-manager
    	if err := command.Execute(); err != nil {
    		fmt.Fprintf(os.Stderr, "%v\n", err)
    		os.Exit(1)
    	}
}
```
以下代码处去启动`kube-controller-manager`：
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190902115228781.png)
`NewDefaultComponentConfig(ports.InsecureKubeControllerManagerPort)`加载各个控制器的配置：
```go
//NewKubeControllerManagerOptions使用默认配置创建一个新的KubeControllerManagerOptions
func NewKubeControllerManagerOptions() (*KubeControllerManagerOptions, error) {
	//加载各个控制器的默认配置
	componentConfig, err := NewDefaultComponentConfig(ports.InsecureKubeControllerManagerPort)
	if err != nil {
		return nil, err
	}

	s := KubeControllerManagerOptions{
		Generic:         cmoptions.NewGenericControllerManagerConfigurationOptions(componentConfig.Generic),
		//.....省略
		GarbageCollectorController: &GarbageCollectorControllerOptions{
			ConcurrentGCSyncs:      componentConfig.GarbageCollectorController.ConcurrentGCSyncs,
			EnableGarbageCollector: componentConfig.GarbageCollectorController.EnableGarbageCollector,
		},
		//.....省略
	}
	//gc忽略的资源对象列表
	gcIgnoredResources := make([]kubectrlmgrconfig.GroupResource, 0, len(garbagecollector.DefaultIgnoredResources()))
	for r := range garbagecollector.DefaultIgnoredResources() {
		gcIgnoredResources = append(gcIgnoredResources, kubectrlmgrconfig.GroupResource{Group: r.Group, Resource: r.Resource})
	}
	s.GarbageCollectorController.GCIgnoredResources = gcIgnoredResources
	return &s, nil
}
```


```go
// NewDefaultComponentConfig返回kube-controller管理器配置对象
func NewDefaultComponentConfig(insecurePort int32) (kubectrlmgrconfig.KubeControllerManagerConfiguration, error) {
	scheme := runtime.NewScheme()
	if err := kubectrlmgrschemev1alpha1.AddToScheme(scheme); err != nil {
		return kubectrlmgrconfig.KubeControllerManagerConfiguration{}, err
	}
	if err := kubectrlmgrconfig.AddToScheme(scheme); err != nil {
		return kubectrlmgrconfig.KubeControllerManagerConfiguration{}, err
	}

	versioned := kubectrlmgrconfigv1alpha1.KubeControllerManagerConfiguration{}
	//加载默认参数
	scheme.Default(&versioned)

	internal := kubectrlmgrconfig.KubeControllerManagerConfiguration{}
	if err := scheme.Convert(&versioned, &internal, nil); err != nil {
		return internal, err
	}
	internal.Generic.Port = insecurePort
	return internal, nil
}
```

```
// 根据Object，获取提供的默认参数
func (s *Scheme) Default(src Object) {
	if fn, ok := s.defaulterFuncs[reflect.TypeOf(src)]; ok {
		fn(src)
	}
}
```
s.defaulterFuncs类型为map[reflect.Type]func(interface{})，用于根据指针类型获取默认值函数。该map中的数据从哪里来的呢？

代码位于src\k8s.io\kubernetes\pkg\controller\apis\config\v1alpha1\zz_generated.defaults.go
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190902154212234.png)
可以看到默认参数中garbage collector中默认开启gc（EnableGarbageCollector），并发数为20（ConcurrentGCSyncs）
```go
func SetDefaults_GarbageCollectorControllerConfiguration(obj *kubectrlmgrconfigv1alpha1.GarbageCollectorControllerConfiguration) {
	if obj.EnableGarbageCollector == nil {
		obj.EnableGarbageCollector = utilpointer.BoolPtr(true)
	}
	if obj.ConcurrentGCSyncs == 0 {
		obj.ConcurrentGCSyncs = 20
	}
}
```

回到Run函数，里面调用了NewControllerInitializers启动所有控制器：
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190902154623724.png)
重点来到启动garbage collector的startGarbageCollectorController函数：

```go
func startGarbageCollectorController(ctx ControllerContext) (http.Handler, bool, error) {
	//k8s 1.13.2中默认为true,可在kube-apiserver和kube-controller-manager的启动参数中加--enable-garbage-conllector=false设置
	//需保证这两个组件中参数值一致
	if !ctx.ComponentConfig.GarbageCollectorController.EnableGarbageCollector {
		return nil, false, nil
	}

	//k8s各种原生资源对象客户端集合(默认启动参数中用SimpleControllerClientBuilder构建)
	gcClientset := ctx.ClientBuilder.ClientOrDie("generic-garbage-collector")
	discoveryClient := cacheddiscovery.NewMemCacheClient(gcClientset.Discovery())

	//生成rest config
	config := ctx.ClientBuilder.ConfigOrDie("generic-garbage-collector")
	dynamicClient, err := dynamic.NewForConfig(config)
	if err != nil {
		return nil, true, err
	}

	// Get an initial set of deletable resources to prime the garbage collector.
	//获取一组初始可删除资源以填充垃圾收集器。
	deletableResources := garbagecollector.GetDeletableResources(discoveryClient)
	ignoredResources := make(map[schema.GroupResource]struct{})

	//忽略gc的资源类型
	for _, r := range ctx.ComponentConfig.GarbageCollectorController.GCIgnoredResources {
		ignoredResources[schema.GroupResource{Group: r.Group, Resource: r.Resource}] = struct{}{}
	}
	garbageCollector, err := garbagecollector.NewGarbageCollector(
		dynamicClient,
		ctx.RESTMapper,
		deletableResources,
		ignoredResources,
		ctx.InformerFactory,
		ctx.InformersStarted,
	)
	if err != nil {
		return nil, true, fmt.Errorf("Failed to start the generic garbage collector: %v", err)
	}

	// Start the garbage collector.
	//启动参数中默认是20个协程
	workers := int(ctx.ComponentConfig.GarbageCollectorController.ConcurrentGCSyncs)
	//启动monitors和deleteWorkers、orphanWorkers
	go garbageCollector.Run(workers, ctx.Stop)

	// Periodically refresh the RESTMapper with new discovery information and sync
	// the garbage collector.
	//使用新的发现信息定期刷新RESTMapper并同步垃圾收集器。
	go garbageCollector.Sync(gcClientset.Discovery(), 30*time.Second, ctx.Stop)

	//gc提供debug dot grap依赖关系图接口
	return garbagecollector.NewDebugHandler(garbageCollector), true, nil
}
```
该函数主要作用有：
1、deletableResources := garbagecollector.GetDeletableResources(discoveryClient)获取集群内所有可删除的资源对象；排除掉忽略的资源对象。
2、构建garbageCollector结构体对象；
3、garbageCollector.Run(workers, ctx.Stop)启动一个monitors用来监听资源对象的变化（对应的由runProcessGraphChanges死循环处理），和默认20个deleteWorkers协程处理可删除的资源对象、20个orphanWorkers协程处理孤儿对象。
4、garbageCollector.Sync(gcClientset.Discovery(), 30*time.Second, ctx.Stop) 定时去获取一个集群内是否有新类型的资源对象的加入，并重新刷新monitors，以监听新类型的资源对象。
5、garbagecollector.NewDebugHandler(garbageCollector)注册debug接口，用来提供获取dot流程图接口：
```
curl http://127.0.0.1:10252/debug/controllers/garbagecollector/graph?uid=11211212edsaddkqedmk12
```
使用graphviz提供的dot.exe可以生成svg格式的图，可用google浏览器查看如下：
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190902233525953.png)

```go
// curl http://127.0.0.1:10252/debug/controllers/garbagecollector/graph?uid=11211212edsaddkqedmk12
func (h *debugHTTPHandler) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	if req.URL.Path != "/graph" {
		http.Error(w, "", http.StatusNotFound)
		return
	}

	var graph graph.Directed
	if uidStrings := req.URL.Query()["uid"]; len(uidStrings) > 0 {
		uids := []types.UID{}
		for _, uidString := range uidStrings {
			uids = append(uids, types.UID(uidString))
		}
		graph = h.controller.dependencyGraphBuilder.uidToNode.ToGonumGraphForObj(uids...)

	} else {
		graph = h.controller.dependencyGraphBuilder.uidToNode.ToGonumGraph()
	}

	//生成dot流程图数据,用graphviz工具中的dot.exe工具转换为svg图(用google浏览器打开)或者png图
	//API参考:https://godoc.org/gonum.org/v1/gonum/graph
	//graphviz下载地址:https://graphviz.gitlab.io/_pages/Download/Download_windows.html
	//dot.exe test.dot -T svg -o test.svg
	data, err := dot.Marshal(graph, "full", "", "  ", false)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Write(data)
	w.WriteHeader(http.StatusOK)
}
```

![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/2019090223362528.png)
GarbageCollector通过restMapper定期重置可删除的资源类型，更新GraphBuilder中的monitors，monitors将创建所有资源类型的变更通知回调函数，将变化的资源对象加入到GraphBuilder的graphChanges队列，GraphBuilder的runProcessGraphChanges()会一直从队列中获取变化，构建一个缓存对象之间依赖关系的图形，以及触发dependencyGraphBuilder将可能被垃圾收集的对象排队到`attemptToDelete`队列，并将其依赖项需要孤立的对象排队到`attemptToOrphan`队列。GarbageCollector具有使用这两个队列的工作人员runAttemptToDeleteWorker和runAttemptToOrphanWorker死循环，分别从`attemptToDelete`队列和`attemptToOrphan`队列取出，向API服务器发送请求以相应地删除更新对象。

```go
// GarbageCollector运行反射器来监视托管API对象的更改，将结果汇总到单线程dependencyGraphBuilder，
// 构建一个缓存对象之间依赖关系的图形。由图变化触发，dependencyGraphBuilder将可能被垃圾收集的对象
// 排队到`attemptToDelete`队列，并将其依赖项需要孤立的对象排队到`attemptToOrphan`队列。
// GarbageCollector具有使用这两个队列的工作人员，向API服务器发送请求以相应地删除更新对象。
// 请注意，让dependencyGraphBuilder通知垃圾收集器确保垃圾收集器使用至少与发送通知一样最新的图形进行操作。
type GarbageCollector struct {
	// resettableRESTMapper是一个RESTMapper，它能够在discovery资源类型时重置自己
	restMapper    resettableRESTMapper
	// dynamicClient提供操作集群内所有资源对象的接口方法,包括k8s内置、CRD生成的自定义资源
	dynamicClient dynamic.Interface
	//垃圾收集器尝试在时间成熟时删除attemptToDelete队列中的item
	attemptToDelete workqueue.RateLimitingInterface
	//垃圾收集器尝试孤立attemptToOrphan队列中item的依赖项，然后删除item
	attemptToOrphan        workqueue.RateLimitingInterface
	dependencyGraphBuilder *GraphBuilder
	// 有owner的资源对象,才会给absentOwnerCache填充不存在的Owner信息
	absentOwnerCache *UIDCache
	sharedInformers  informers.SharedInformerFactory

	workerLock sync.RWMutex
}
```

```
// GraphBuilder：基于informers提供的事件，GraphBuilder更新
// uidToNode，一个缓存我们所知的依赖关系的图，并将
// 项放入attemptToDelete和attemptToOrphan队列
type GraphBuilder struct {
	restMapper meta.RESTMapper

	//每个监视器列表/监视资源，结果汇集到dependencyGraphBuilder
	monitors    monitors
	monitorLock sync.RWMutex
	// informersStarted is closed after after all of the controllers have been initialized and are running.
	// After that it is safe to start them here, before that it is not.
	// informersStarted在所有控制器初始化并运行后关闭。之后在这里启动它们是安全的，在此之前它不是。
	informersStarted <-chan struct{}

	// stopCh drives shutdown. When a receive from it unblocks, monitors will shut down.
	// This channel is also protected by monitorLock.
	// stopCh驱动器关闭当来自它的接收解除阻塞时，监视器将关闭。 此channel也受monitorLock保护。
	stopCh <-chan struct{}

	// running tracks whether Run() has been called.
	// it is protected by monitorLock.
	//运行轨道是否已调用Run()它受monitorLock保护。
	running bool

	dynamicClient dynamic.Interface
	// monitors are the producer of the graphChanges queue, graphBuilder alters
	// the in-memory graph according to the changes.
	// monitor是graphChanges队列的生成者，graphBuilder根据更改改变了内存中的图形。
	graphChanges workqueue.RateLimitingInterface

	// uidToNode doesn't require a lock to protect, because only the
	// single-threaded GraphBuilder.processGraphChanges() reads/writes it.
	//uidToNode不需要锁保护，因为只有单线程GraphBuilder.processGraphChanges()读写它。
	uidToNode *concurrentUIDToNode

	// GraphBuilder is the producer of attemptToDelete and attemptToOrphan, GC is the consumer.
	// GraphBuilder是attemptToDelete和attemptToOrphan的生产者，GC是消费者。
	attemptToDelete workqueue.RateLimitingInterface
	attemptToOrphan workqueue.RateLimitingInterface

	// GraphBuilder and GC share the absentOwnerCache. Objects that are known to
	// be non-existent are added to the cached.
	// GraphBuilder和GC共享absentOwnerCache。已知不存在的对象将添加到缓存中。
	absentOwnerCache *UIDCache

	//所有k8s资源对象集的informer
	sharedInformers  informers.SharedInformerFactory

	//监视器忽略的资源对象集
	ignoredResources map[schema.GroupResource]struct{}
}
```

创建NewGarbageCollector结构体：
```go
func NewGarbageCollector(
	dynamicClient dynamic.Interface,
	mapper resettableRESTMapper,
	deletableResources map[schema.GroupVersionResource]struct{},
	ignoredResources map[schema.GroupResource]struct{},
	sharedInformers informers.SharedInformerFactory,
	informersStarted <-chan struct{},
) (*GarbageCollector, error) {
	attemptToDelete := workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "garbage_collector_attempt_to_delete")
	attemptToOrphan := workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "garbage_collector_attempt_to_orphan")
	absentOwnerCache := NewUIDCache(500)
	gc := &GarbageCollector{
		dynamicClient:    dynamicClient,
		restMapper:       mapper,
		attemptToDelete:  attemptToDelete,
		attemptToOrphan:  attemptToOrphan,
		absentOwnerCache: absentOwnerCache,
	}
	gb := &GraphBuilder{
		dynamicClient:    dynamicClient,
		informersStarted: informersStarted,
		restMapper:       mapper,
		graphChanges:     workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "garbage_collector_graph_changes"),
		uidToNode: &concurrentUIDToNode{
			uidToNode: make(map[types.UID]*node),
		},
		attemptToDelete:  attemptToDelete,
		attemptToOrphan:  attemptToOrphan,
		absentOwnerCache: absentOwnerCache,
		sharedInformers:  sharedInformers,
		ignoredResources: ignoredResources,
	}
	//初始化各个资源对象的monitors，启动各资源对象的监听器，变化时触发回调，将其加入graphChanges 队列
	if err := gb.syncMonitors(deletableResources); err != nil {
		utilruntime.HandleError(fmt.Errorf("failed to sync all monitors: %v", err))
	}
	gc.dependencyGraphBuilder = gb

	return gc, nil
}
```
主要功能：
1、构建GarbageCollector结构体；
2、构建依赖结构图维护结构体GraphBuilder，和GarbageCollector共用attemptToDelete和attemptToOrphan队列，GraphBuilder作为生产着将适当资源放到attemptToDelete或者attemptToOrphan队列，供GarbageCollector中的worker进行消费；
3、初始化各个资源对象的monitors，启动各资源对象的监听器，变化时触发回调，将其加入graphChanges 队列。

`gb.syncMonitors(deletableResources)`方法中最主要的是`c, s, err := gb.controllerFor(resource, kind)`

```go
func (gb *GraphBuilder) controllerFor(resource schema.GroupVersionResource, kind schema.GroupVersionKind) (cache.Controller, cache.Store, error) {
	handlers := cache.ResourceEventHandlerFuncs{
		// add the event to the dependencyGraphBuilder's graphChanges.
		// 将事件添加到dependencyGraphBuilder的graphChanges中。
		AddFunc: func(obj interface{}) {
			event := &event{
				eventType: addEvent,
				obj:       obj,
				gvk:       kind,
			}
			gb.graphChanges.Add(event)
		},
		UpdateFunc: func(oldObj, newObj interface{}) {
			// TODO: check if there are differences in the ownerRefs,
			// finalizers, and DeletionTimestamp; if not, ignore the update.
			//TODO：检查ownerRefs， finalizers和DeletionTimestamp是否存在差异;如果没有，请忽略更新。
			event := &event{
				eventType: updateEvent,
				obj:       newObj,
				oldObj:    oldObj,
				gvk:       kind,
			}
			gb.graphChanges.Add(event)
		},
		DeleteFunc: func(obj interface{}) {
			// delta fifo may wrap the object in a cache.DeletedFinalStateUnknown, unwrap it
			// delta fifo可以将对象包装在cache.DeletedFinalStateUnknown中，解包它
			if deletedFinalStateUnknown, ok := obj.(cache.DeletedFinalStateUnknown); ok {
				obj = deletedFinalStateUnknown.Obj
			}
			event := &event{
				eventType: deleteEvent,
				obj:       obj,
				gvk:       kind,
			}
			gb.graphChanges.Add(event)
		},
	}
	shared, err := gb.sharedInformers.ForResource(resource)
	if err == nil {
		klog.V(4).Infof("using a shared informer for resource %q, kind %q", resource.String(), kind.String())
		// need to clone because it's from a shared cache
		shared.Informer().AddEventHandlerWithResyncPeriod(handlers, ResourceResyncTime)
		return shared.Informer().GetController(), shared.Informer().GetStore(), nil
	} else {
		//获取资源对象时出错会到这里,比如非k8s内置RedisCluster、clusterbases、clusters、esclusters、volumeproviders、stsmasters、appapps、mysqlclusters、brokerclusters、clustertemplates;
		//内置的networkPolicies、apiservices、customresourcedefinitions
		klog.V(4).Infof("unable to use a shared informer for resource %q, kind %q: %v", resource.String(), kind.String(), err)
	}

	// TODO: consider store in one storage.
	// TODO: 考虑存储在一个存储中。
	klog.V(5).Infof("create storage for resource %s", resource)
	//上面失败的资源对象的store和controller
	store, monitor := cache.NewInformer(
		listWatcher(gb.dynamicClient, resource),
		nil,
		ResourceResyncTime,
		// don't need to clone because it's not from shared cache
		//不需要克隆，因为它不是来自共享缓存
		handlers,
	)
	return monitor, store, nil
}
```
该方法主要功能是：
1、将新增、更改、删除的资源对象构建为event结构体，放入GraphBuilder的graphChanges队列里，最终被runProcessGraphChanges这个worker消费；
2、构建大多数内置资源的SharedInformerFactory，构建失败的用cache.NewInformer构建（通过CRD定义的对象以及部分k8s内置对象）

代码继续回到k8s.io\kubernetes\cmd\kube-controller-manager\app\core.go中的`startGarbageCollectorController`中，看`
garbageCollector.Run(workers, ctx.Stop)`方法：

```go
func (gc *GarbageCollector) Run(workers int, stopCh <-chan struct{}) {
	defer utilruntime.HandleCrash()
	defer gc.attemptToDelete.ShutDown()
	defer gc.attemptToOrphan.ShutDown()
	defer gc.dependencyGraphBuilder.graphChanges.ShutDown()

	klog.Infof("Starting garbage collector controller")
	defer klog.Infof("Shutting down garbage collector controller")

	//协程运行生产者monitors
	go gc.dependencyGraphBuilder.Run(stopCh)

	//等待dependencyGraphBuilder缓存开始同步
	if !controller.WaitForCacheSync("garbage collector", stopCh, gc.dependencyGraphBuilder.IsSynced) {
		return
	}

	//垃圾收集器：所有资源监视器都已同步。继续收集垃圾
	klog.Infof("Garbage collector: all resource monitors have synced. Proceeding to collect garbage")

	// gc workers
	//协程运行消费者DeleteWorkers和OrphanWorkers
	for i := 0; i < workers; i++ {
		//默认参数为20个并发协程尝试delete worker
		go wait.Until(gc.runAttemptToDeleteWorker, 1*time.Second, stopCh)
		//默认参数为20个并发协程尝试orphan worker
		go wait.Until(gc.runAttemptToOrphanWorker, 1*time.Second, stopCh)
	}

	<-stopCh
}
```
`gc.dependencyGraphBuilder.Run(stopCh)`主要功能：
1、gb.startMonitors()启动监听资源变化的informer；
2、wait.Until(gb.runProcessGraphChanges, 1*time.Second, stopCh)开启从队列GraphBuilder.graphChanges中消费的worker

启动20个runAttemptToDeleteWorker和20个runAttemptToOrphanWorker



## 参考

k8s官方文档garbage-collection英文版：
https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/

依赖图标生成库gonum Api文档：
https://godoc.org/gonum.org/v1/gonum/graph

graphviz下载：
https://graphviz.gitlab.io/_pages/Download/Download_windows.html


