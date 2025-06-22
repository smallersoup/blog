title: 采坑指南——k8s域名解析coredns问题排查过程
date: '2019-10-17 14:40:05'
updated: '2019-10-17 14:40:05'
tags: [kubernetes]
permalink: /201910171439kube
---
![](https://img.hacpai.com/bing/20180826.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文
前几天，在ucloud上搭建的k8s集群（搭建教程后续会发出）。今天发现域名解析不了。

**组件版本：k8s 1.15.0，coredns：1.3.1**

### 过程是这样的：

首先用以下yaml文件创建了一个nginx服务
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc-old
  labels:
    app: nginx-svc
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
---
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: nginx-old
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
```
创建好之后：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRjYTk3NjgyODBhMTBhMDEucG5n)
因只部署了一个master节点。在master宿主机上直接执行以下命令：
```yaml
nslookup nginx-svc-old.default.svc
```
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWQ0YmNmMWU3NGNlMmEwZjcucG5n)
发现不能解析域名。事先也在宿主机上/etc/resolv.conf里配置了nameserver {coredns的podIP}
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWRhMTVjYmRjNmZhYTU1ZjEucG5n)
这样一来，就以为可能是coredns有问题。。



然后用以下yaml创建了一个busybox作为调试工具：
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: busybox-deployment
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: busybox
    spec:
      restartPolicy: Always
      containers:
      - name: busybox
        command:
        - sleep
        - "3600"
        image: busybox
```
这里用的是截止2019/07/20，busybox的最新镜像。创建好之后，exec进入容器，执行测试命令
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRmMTE2MDk5ZGI2NWViYmQucG5n)
发现解析不了:
```yaml
/ # nslookup nginx-svc-old.default.svc
Server:    10.96.0.10
Address:  10.96.0.10:53

** server can't find nginx-svc-old.default.svc: NXDOMAIN

*** Can't find nginx-svc-old.default.svc: No answer
```
根据coredns解析集群内域名原理可知：



服务 a 访问服务 b，对于同一个 Namespace下，可以直接在 pod 中，通过 curl b 来访问。对于跨 Namespace 的情况，服务名后边对应 Namespace即可，比如 curl b.default。DNS 如何解析，依赖容器内 resolv 文件的配置。



查看busybox容器内的resolve.conf文件：
```yaml

[root@liabio nginx]# kubectl exec -ti busybox-deployment-59755c8c6d-rmrfq sh
/ # nslookup nginx-svc-old.default.svc
Server:    10.96.0.10
Address:  10.96.0.10:53

** server can't find nginx-svc-old.default.svc: NXDOMAIN

*** Can't find nginx-svc-old.default.svc: No answer

/ # cat /etc/resolv.conf 
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
/ #
```
这个文件中，配置的 DNS Server，一般就是 K8S 中，kubedns 的 Service 的 ClusterIP，这个IP是虚拟IP，无法ping，但可以访问。
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTEyYWViMjg3MTA2ZmMxMWMucG5n)
在容器内发请求时，会根据 /etc/resolv.conf 进行解析流程。选择 nameserver 10.96.0.10 进行解析，然后用nginx-svc-old ，依次带入 /etc/resolve.conf 中的 search 域，进行DNS查找，分别是：



search 内容类似如下（不同的pod，第一个域会有所不同）
```yaml
search default.svc.cluster.local svc.cluster.local cluster.local
```
```yaml
nginx-svc-old.default.svc.cluster.local -> nginx-svc-old.svc.cluster.local -> nginx-svc-old.cluster.local 
```
直到找到为止。所以，我们执行 ping nginx-svc-old，或者执行 ping nginx-svc-old.default，都可以完成DNS请求，这2个不同的操作，会分别进行不同的DNS查找步骤。





根据以上原理，查看到busybox内的域名/etc/resolv.conf没有问题，nameserver指向正确的kube-dns的service clusterIP。



这下更加怀疑core-dns有问题了。



但查看coredns日志，可以看到并没有报错：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM1MTVmYThlMjYzNWMxOTMucG5n)
那就说明不是coredns问题了。。



把busybox里报的错误，进行搜索google
```yaml
*** Can't find nginx-svc-old.default.svc: No answer
```
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWY3ZTE4MDBmYmMxYjA0ZmUucG5n)

查到了以下两个issue：



#### issues1：
https://github.com/kubernetes/kubernetes/issues/66924
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTVlMzJhZDVhZmY2ZmM2NjMucG5n)


#### issues2：

https://github.com/easzlab/kubeasz/issues/260
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWU4Yzk5NTQzNTA1ZjVkMDQucG5n)
发现都说是busybox镜像的问题，从1.28.4以后的镜像都存在这问题。把镜像换成1.28.4试试？修改yaml版本号：
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: busybox-deployment
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: busybox
    spec:
      restartPolicy: Always
      containers:
      - name: busybox
        command:
        - sleep
        - "3600"
        image: busybox:1.28.4
```
重新apply后，进入容器：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTc3MmZiODRmNjMxYmQxNzUucG5n)

确实可以成功解析域名了。



那为什么宿主机上直接执行测试命令，域名不能解析呢？
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWY4Y2UxZGQ3ODk0YmMwNGQucG5n)

继续google，知道resolver域名解析器：

nameserver关键字，如果没指定nameserver就找不到DNS服务器，其它关键字是可选的。nameserver表示解析域名时使用该地址指定的主机为域名服务器。其中域名服务器是按照文件中出现的顺序来查询的，且只有当第一个nameserver没有反应时才查询下面的nameserver，一般不要指定超过3个服务器。
而我在宿主上/etc/resolv.conf中nameserver如下：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWEzNmFiNDBjNTA4YzY1YjAucG5n)
且前三个域名解析服务器后可以通。



现在试着把coredns的其中一个podIP：192.168.155.73放到第一个nameserver：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTVmZTU3ODNmNTQ0ZDQzN2UucG5n)
可以看到现在可以解析了。



其实最好把kube-dns service的clusterIP放到/etc/resolv.conf中，这样pod重启后也可以解析。
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZiYjU0NDkzNTM1Mjc3YzMucG5n)

## 参考

Linux中/etc/resolv.conf文件简析
https://blog.csdn.net/lcr_happy/article/details/54867510

CoreDNS系列1：Kubernetes内部域名解析原理、弊端及优化方式

https://hansedong.github.io/2018/11/20/9/



