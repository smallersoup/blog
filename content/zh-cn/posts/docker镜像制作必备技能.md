---
title: docker镜像制作必备技能
date: '2019-10-17 14:18:17'
updated: '2019-10-17 14:21:27'
tags: [docker]
permalink: /articles/2019/10/17/1571293096948.html
---
![](https://img.hacpai.com/bing/20180416.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文
使用过docker的都知道dockerfile，其用于定义制作镜像的流程，由一系列命令和参数构成的脚本，这些命令应用于基础镜像并最终创建一个新的镜像。可参考往期文章学习：[docker基础知识整理](https://mp.weixin.qq.com/s/lzFL4eWU8h23sTbFbHEZkg)

有时候，我们想在原有镜像基础上修改、增加文件，由于国内网络原因，重新制作镜像会很慢，甚至失败；或者根本不知道镜像的dockerfile长什么样。改动很小情况下，可以用以下方式制作镜像。

拿k8s负载均衡器组件ingress-nginx:0.24.1版本为例：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/50f9a1f7b798a13677b892fb6ce8d4d5.png)
如果我们修改了其源码，并编译生成nginx-ingress-controller二进制文件，可以用以下方式进行制作新镜像。



首先用命令：
```sh
docker run -ti --rm k8s-deploy/nginx-ingress-controller:0.24.1 bash
```


将镜像运行起来。其中-ti表示打开一个交互输入终端；--rm表示运行停止后自动清理。



运行后可以看到默认用户为www-data，a298fe62a4f9表示容器id
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/bf307293782df4fb733f6c343531720f.png)

我们可以在容器里创建目录：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b79d5af298d10677e05f5aafdf17cebd.png)

重新打开一个shell窗口，用于给容器内复制一个测试文件：
```sh
docker cp ingressgroup-upstream.tmpl a298fe62a4f9:/etc/nginx/conf.d/include-server-map/
```
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/f21b10b2fb37aad3af0bc03cd40a1557.png)

复制进去后，当要将其移动到其他位置时，报Permission denied权限不足，因为默认为www-data用户，复制到容器内的ingressgroup-upstream.tmpl属主:属组也是root，如果不把root修改为www-data，肯定会报没权限的错。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/ad45fe54ef9b218e748a29d66be36b4e.png)

通过以下命令重新运行镜像：
```sh
docker run -ti --rm -u 0 k8s-deploy/nginx-ingress-controller:0.24.1 bash
```


-u 0代表用root用户运行容器，而不是dockerfile里指定的用户，这样运行后可以看到用户为root，记录容器id:ffdc80f3cce7

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/4def90be51904fc44bc94496689b6c5a.png)

重新执行复制操作：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/66b32d1f28b10178d96157c3a8100bb7.png)

此时就可以随意移动和修改文件的权限、属组、属主了。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/a1d6ada8eaa35fed01579dc3781973c8.png)

修改完毕后，执行以下命令将镜像commit到本地仓库：

```
docker commit ffdc80f3cce7 k8s-deploy/nginx-ingress-controller:0.24.1-temp
```

commit后跟的是容器id，最后跟的是新镜像名称。push命令将新镜像推到远程harbor仓库。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/4158676a1335fc23a011deb7e3716944.png)

运行新制作的镜像，可以看到我们修改的文件。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/3799ec75377110c84c4f2797ab5f92fb.png)

**这种方式一般用于测试，弊端是可能会导致镜像越来越大。**
