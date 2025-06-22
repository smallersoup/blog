---
title: kubernetes垃圾回收器GarbageCollector源码分析
date: '2019-10-22 10:57:26'
updated: '2019-10-22 19:39:43'
tags: [kubernetes]
permalink: /201910221057gc
---

# kubernetes垃圾回收器GarbageCollector 源码分析



> **kubernetes版本：1.13.2**



## 背景

由于operator创建的redis集群，在kubernetes apiserver重启后，redis集群被异常删除（包括redis exporter statefulset、redis statefulset）。删除后operator将其重建，重新组建集群，实例IP发生变更（中间件容器化，我们开发了固定IP，当statefulset删除后，IP会被回收），导致创建集群失败，最终集群不可用。

经多次复现，apiserver重启后，通过查询redis operator日志，并没有发现主动去删除redis集群（redis statefulset）、监控实例（redis exporter）。进一步去查看kube-controller-manager的日志，将其日志级别设置--v=5，继续复现，最终在kube-controller-manager日志中发现如下日志：
![在这里插入图片描述](https://img-blog.csdnimg.cn/2019090122334772.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
可以看到是garbage collector触发删除操作的。这个问题在apiserver正常的时候是不存在，要想弄其究竟，就得看看kube-controller-manager内置组件garbage collector这个控制器的逻辑。

## 正文

### gc整体架构

**GarbageCollector Controller源码主要分为以下几部分：**

1. `monitors`作为生产者将变化的资源放入`graphChanges`队列；同时`restMapper`定期检测集群内资源类型，刷新`monitors`
2. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToDelete`队列；
3. `runProcessGraphChanges`从`graphChanges`队列中取出变化的`item`，根据情况放入`attemptToOrphan`队列；
4. `runAttemptToDeleteWorker`从`attemptToDelete`队列取出，尝试删除垃圾资源；
5. `runAttemptToOrphanWorker`从`attemptToOrphan`队列取出，处理该孤立的资源；


![在这里插入图片描述](https://img-blog.csdnimg.cn/20190903103422219.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

---



想要启用`GC`，需要在`kube-apiserver`和`kube-controller-manager`的启动参数中都设置`--enable-garbage-collector`为`true`,`1.13.2`版本中默认开启`GC`。

**需要注意：两组件该参数必须保持同步。**

----
### gc启动

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
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190902115228781.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
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
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190902154212234.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
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
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190902154623724.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
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
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190902233525953.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

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

![在这里插入图片描述](https://img-blog.csdnimg.cn/2019090223362528.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
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



### runProcessGraphChanges处理主流程

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

#### 1、 出队

从graphChanges队列取出资源对象，从GraphBuilder.uidToNode中读取该资源节点（uidToNode维护着资源对象依赖关系图表结构），found为true时表示图表存在该资源节点；

#### 2、switch的第一个case

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



#### 3、switch的第二个case

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

#### 4、switch的第三个case

如果该资源是删除时触发，从图表中移除item资源，同时遍历owners，移除owner下的item资源；
如果该资源的从资源数大于0,则将该资源被删除信息（uid）加入absentOwnerCache缓存，这样处理该资源的从资源时，就知道owner不存在了。
遍历该资源的从资源加到删除队列里；
如果从图表中发现 owner或者 owner的从资源正在被删除，则尝试将owner加入到attemptToDelete队列中，去尝试删除owner。

#### 整理流程

 - 当controllermanager重启时，会全量listwatch一遍所有对象，gc collector维护的uidToNode图表里各个资源对象node是不存在的，此时会走第一个switch case，构建完整关系图表，如果owner不存在则先构建虚拟owner节点，同时加入attemptToDelete队列，尝试去删除这个owner，其实即使加入到attemptToDelete队列，也不一定会被删除，还会进行一系列判断，这个下一节再分析；将正在删除的资源，同时Finalizer为Orphan的加入到attemptToOrphan队列；为foreground的资源以及其从资源加入到attemptToDelete队列，并将deletingDependents设置为true；
 - 添加或者更新事件时，且图表中存在item资源对象时，会走第二个switch case，对item的owner变化进行判断，并维护更新图表；同理将正在删除的资源，同时Finalizer为Orphan的加入到attemptToOrphan队列；Finalizer为foreground的资源以及其从资源加入到attemptToDelete队列，并将deletingDependents设置为true；
 - 如果是删除事件，则会更新图表，并处理和其相关的从资源和其owner加入到attemptToDelete队列。



### 终结器

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

### attemptToDelete队列

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

### attemptToOrphan队列

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

详解 Kubernetes 垃圾收集器的实现原理：

https://draveness.me/kubernetes-garbage-collector#

k8s官方文档garbage-collection英文版：
https://kubernetes.io/docs/concepts/workloads/controllers/garbage-collection/

依赖图标生成库gonum Api文档：
https://godoc.org/gonum.org/v1/gonum/graph

graphviz下载：
https://graphviz.gitlab.io/_pages/Download/Download_windows.html


