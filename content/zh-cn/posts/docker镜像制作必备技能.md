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
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWRhODQ4M2IyMTc1NDM2ZjUucG5n?x-oss-process=image/format,png)
如果我们修改了其源码，并编译生成nginx-ingress-controller二进制文件，可以用以下方式进行制作新镜像。



首先用命令：
```sh
docker run -ti --rm k8s-deploy/nginx-ingress-controller:0.24.1 bash
```


将镜像运行起来。其中-ti表示打开一个交互输入终端；--rm表示运行停止后自动清理。



运行后可以看到默认用户为www-data，a298fe62a4f9表示容器id
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM2ZTQzZGYzOWQxOTRlOTUucG5n?x-oss-process=image/format,png)

我们可以在容器里创建目录：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWFkZDg0MDYwYjk1M2E1NTAucG5n?x-oss-process=image/format,png)

重新打开一个shell窗口，用于给容器内复制一个测试文件：
```sh
docker cp ingressgroup-upstream.tmpl a298fe62a4f9:/etc/nginx/conf.d/include-server-map/
```
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTliZDBhNmU1ZGU1YmI0MTEucG5n?x-oss-process=image/format,png)

复制进去后，当要将其移动到其他位置时，报Permission denied权限不足，因为默认为www-data用户，复制到容器内的ingressgroup-upstream.tmpl属主:属组也是root，如果不把root修改为www-data，肯定会报没权限的错。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRjYzFhNTE1MTk0ZDNmZGUucG5n?x-oss-process=image/format,png)

通过以下命令重新运行镜像：
```sh
docker run -ti --rm -u 0 k8s-deploy/nginx-ingress-controller:0.24.1 bash
```


-u 0代表用root用户运行容器，而不是dockerfile里指定的用户，这样运行后可以看到用户为root，记录容器id:ffdc80f3cce7

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTQyODVjMjdmNTNkMGFiZTcucG5n?x-oss-process=image/format,png)

重新执行复制操作：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWQ2N2FiOTUyMDc5NjE3ZmU?x-oss-process=image/format,png)

此时就可以随意移动和修改文件的权限、属组、属主了。

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWEyMjg3MDg0ZTBmYmNjZjg?x-oss-process=image/format,png)

修改完毕后，执行以下命令将镜像commit到本地仓库：

```
docker commit ffdc80f3cce7 k8s-deploy/nginx-ingress-controller:0.24.1-temp
```

commit后跟的是容器id，最后跟的是新镜像名称。push命令将新镜像推到远程harbor仓库。

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTFmMTM0ODNjNjdiZTU1ZWE?x-oss-process=image/format,png)

运行新制作的镜像，可以看到我们修改的文件。

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTdhY2RiNGMxZDNhZTkzNmU?x-oss-process=image/format,png)

**这种方式一般用于测试，弊端是可能会导致镜像越来越大。**
