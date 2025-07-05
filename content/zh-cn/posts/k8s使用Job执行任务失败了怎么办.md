---
title: k8s使用Job执行任务失败了怎么办
date: '2019-10-17 14:43:07'
updated: '2019-10-17 14:43:07'
tags: [kubernetes]
permalink: /201910171442kube
---
![](https://img.hacpai.com/bing/20180724.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


Kubernetes 中使用 Job 和 CronJob 两个资源分别提供了一次性任务和定时任务的特性，这两种对象也使用控制器模型来实现资源的管理，我们在这篇文章来介绍Job执行如果失败了会怎么样呢？

修改job-fail.yaml，故意引入一个错误：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/295a1bc43603dae60cffad532976590e.png)

## Never

如果将 `restartPolicy` 设置为 `Never` 会怎么样？下面我们实践一下，修改job-fail.yaml后重新启动。

运行 Job 并查看状态，可以看到Never策略的job，pod失败后，重新创建：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b693c88a667ac711fa916f0821ab1669.png)

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/945e045e555bc66d777b3ac983022a12.png)
直到重新创建7个（spec.backoffLimit默认为6，即重试6次，共7个pod）pod都失败后，认为失败，job的status里会更新为Failed
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/f8fb6a950e3977ea7f611a7e68d2192f.png)



当前 `Completion` 的数量为 `0`
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/512bee7eaa3f960af03afbfceebd4144.png)

查看 Pod 的状态：



可以看到有多个 Pod，状态均不正常。`kubectl describe pod` 查看某个 Pod 的启动日志：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/73c240791a44bdc6d29655fe66917a65.png)

日志显示没有可执行程序，符合我们的预期。

**为什么 `kubectl get pod` 会看到这么多个失败的 Pod？**

原因是：当第一个 Pod 启动时，容器失败退出，根据 `restartPolicy: Never`，此失败容器不会被重启，但 Job `DESIRED` 的 Pod 是 `1`，目前 `SUCCESSFUL` 为 `0`，不满足，所以 Job controller 会启动新的 Pod，直到 `SUCCESSFUL` 为 `1`。对于我们这个例子，`SUCCESSFUL` 永远也到不了 `1`，所以 Job controller 会一直创建新的 Pod，直到设置的数量，失败后pod不会自动被删除，为了终止这个行为，只能删除 Job，pod也会被同时删掉。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/15f7a05d3a4d54289236d3d78e5d1617.png)
## OnFailure

如果将 `restartPolicy` 设置为 `OnFailure` 会怎么样？下面我们实践一下，修改job-fail.yaml后重新启动。![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d6c33634e17a957f57ff6ab813c8c95b.png)

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/7e4800cdc3305cf95e3bcedd7b2bf661.png)


Job 的 `Completions` Pod 数量还是为 `0`，看看 Pod 的情况：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/8ed947e1c16c144b4224b00a48c99578.png)


这里只有一个 Pod，不过 `RESTARTS` 在不断增加，说明 `OnFailure` 生效，容器失败后会自动重启。
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/bb8550ad45e2d9b693115ccae6a2b2ff.png)

6次失败后，pod被删除：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0ac0d45ccf1cacf99191b30289c5b219.png)

同时更新job的status为失败，方便查看最终执行结果：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/bd852eae7c96b3a18ad01b5e516bfe5f.png)

