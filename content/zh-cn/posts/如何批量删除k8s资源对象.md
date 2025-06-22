title: 如何批量删除k8s资源对象
date: '2019-10-17 14:38:49'
updated: '2019-10-17 14:38:49'
tags: [kubernetes]
permalink: /201910171438kube
---
![](https://img.hacpai.com/bing/20180630.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)

> 本文首发于公众号【我的小碗汤】扫描文末二维码关注，一起交流学习

**在云平台开发、中间件容器化时，经常会遇到批量删除k8s资源对象的需求，下面记录一下kubectl和golang发送删除pvc、pv、pod请求的例子，便于后续学习查阅**

## kubectl发送删除请求

根据label批量删除pod：
```shell
kubectl delete pod -n kube-system -l "harmonycloud.cn/statefulset=redis-ll-1010-a"
```
![(/img/2019-10-10-batch-delet-k8s-resources/batch-delete-pods.png)\]](https://img-blog.csdnimg.cn/2019101020392943.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

根据label批量删除pvc：
```shell
kubectl delete pvc -n kube-system -l "harmonycloud.cn/statefulset=redis-ll-1010-a"
```
![(/img/2019-10-10-batch-delet-k8s-resources/batch-delete-pvcs.png)\]](https://img-blog.csdnimg.cn/20191010203940437.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

根据label批量删除pv：
```shell
kubectl delete pv -l "harmonycloud.cn/statefulset=redis-ll-1010-a"
```
![(/img/2019-10-10-batch-delet-k8s-resources/batch-delete-pvs.png)\]](https://img-blog.csdnimg.cn/20191010203948989.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

## golang发送删除请求
根据label批量删除pvc、pod、pv

`注意：启动参数中加入以下参数：`
```shell
--kubeconfig=/root/.kube/config --v=5
```

```go
package operator

import (
	"flag"
	extensionsclient "k8s.io/apiextensions-apiserver/pkg/client/clientset/clientset"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apiserver/pkg/util/logs"
	clientset "k8s.io/client-go/kubernetes"
	restclient "k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/klog"
	"os"
	"testing"
)

type OperatorManagerServer struct {
	Master     string
	Kubeconfig string
}

func NewOMServer() *OperatorManagerServer {
	s := OperatorManagerServer{}
	return &s
}

var s *OperatorManagerServer

func init() {

	s = NewOMServer()
	flag.StringVar(&s.Master, "master", s.Master, "The address of the Kubernetes API server (overrides any value in kubeconfig)")
	flag.StringVar(&s.Kubeconfig, "kubeconfig", s.Kubeconfig, "Path to kubeconfig file with authorization and master location information.")
	//初始化klog等flag
	logs.InitLogs()
	flag.Parse()
}

func Test_DeleteCollection(t *testing.T) {
	if err := Run(s); err != nil {
		t.Fatalf("%v\n", err)
		os.Exit(1)
	}
}

func Run(s *OperatorManagerServer) error {

	var (
		generalLabelKey       = "harmonycloud.cn/statefulset"
		redisClusterName      = "redis-ll-1010"
		redisClusterNamespace = "kube-system"
	)

	kubeClient, _, _, err := createClients(s)

	if err != nil {
		return err
	}

	//根据label批量删除pod
	labelPod := labels.SelectorFromSet(labels.Set(map[string]string{generalLabelKey: redisClusterName}))
	listPodOptions := metav1.ListOptions{
		LabelSelector: labelPod.String(),
	}
	err = kubeClient.CoreV1().Pods(redisClusterNamespace).DeleteCollection(&metav1.DeleteOptions{}, listPodOptions)
	if err != nil {
		if !errors.IsNotFound(err) {
			klog.Errorf("Drop RedisCluster: %v/%v pod error: %v", redisClusterNamespace, redisClusterName, err)
			return err
		}
	}

	//根据label批量删除pvc
	labelPvc := labels.SelectorFromSet(labels.Set(map[string]string{"app": redisClusterName}))
	listPvcOptions := metav1.ListOptions{
		LabelSelector: labelPvc.String(),
	}
	err = kubeClient.CoreV1().PersistentVolumeClaims(redisClusterNamespace).DeleteCollection(&metav1.DeleteOptions{}, listPvcOptions)
	if err != nil {
		if !errors.IsNotFound(err) {
			klog.Errorf("Drop RedisCluster: %v/%v pvc error: %v", redisClusterNamespace, redisClusterName, err)
			return err
		}
	}

	//如果pv没有删除掉,则删除
	labelPv := labels.SelectorFromSet(labels.Set(map[string]string{generalLabelKey: redisClusterName}))
	listPvOptions := metav1.ListOptions{
		LabelSelector: labelPv.String(),
	}
	err = kubeClient.CoreV1().PersistentVolumes().DeleteCollection(&metav1.DeleteOptions{}, listPvOptions)

	if err != nil {
		if !errors.IsNotFound(err) {
			klog.Errorf("Drop RedisCluster: %v/%v pv error: %v", redisClusterNamespace, redisClusterName, err)
			return err
		}
	}

	return nil
}

//根据kubeconfig文件创建客户端
func createClients(s *OperatorManagerServer) (*clientset.Clientset, *extensionsclient.Clientset, *restclient.Config, error) {
	kubeconfig, err := clientcmd.BuildConfigFromFlags(s.Master, s.Kubeconfig)
	if err != nil {
		return nil, nil, nil, err
	}

	kubeconfig.QPS = 100
	kubeconfig.Burst = 100

	kubeClient, err := clientset.NewForConfig(restclient.AddUserAgent(kubeconfig, "operator-manager"))
	if err != nil {
		klog.Fatalf("Invalid API configuration: %v", err)
	}

	extensionClient, err := extensionsclient.NewForConfig(restclient.AddUserAgent(kubeconfig, "operator-manager"))
	if err != nil {
		klog.Fatalf("Invalid API configuration: %v", err)
	}

	return kubeClient, extensionClient, kubeconfig, nil
}

```
**client-go中提供的**

* Delete方法,只能删除单个资源对象,第一个参数往往是资源对象名称,第二个参数是删除选项，如：优雅终止时间GracePeriodSeconds、删除传播策略：Foreground前台删除、后台删除：Background、孤儿删除：Orphan

* DeleteCollection方法第一个参数是删除选项，第二个参数是删除条件，包括label Selector、field Selector等

```go
Delete(name string, options *metav1.DeleteOptions) error
DeleteCollection(options *metav1.DeleteOptions, listOptions metav1.ListOptions) error
```

## 参考
k8s官方API文档：

https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#delete-collection-524

--------
