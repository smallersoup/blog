---
title: nginx学习笔记
date: '2019-10-18 13:08:21'
updated: '2019-10-18 13:08:21'
tags: [nginx]
permalink: /201910181307nginx
---
> 中间件位于客户机/ 服务器的操作系统之上，管理计算机资源和网络通讯。 是连接两个独立应用程序或独立系统的软件。

web请求通过中间件可以直接调用操作系统，也可以经过中间件把请求分发到多个应用上进行逻辑处理。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005844801.jpeg)

因为有了中间件，使得大型网站在规划有了更好的层次性，维护上更加方便。也可以实现负载均衡、安全防护等。

Nginx是一个开源高性能、可靠的HTTP中间件、代理服务，在目前企业中得到了很大的利用。

今天主要学习下nginx的安装配置，以便于后续学习。 

**以下在本地虚拟机上搭建学习。**

linux环境搭建可以参考：

[vmware上安装linux过程记录](http://mp.weixin.qq.com/s?__biz=MjM5MzU5NDYwNA==&mid=2247484370&idx=1&sn=f701fa2a8477143327d24b33eb175652&chksm=a695ee5191e26747c37132dca65bc6cefb1abd4b3b5e5361e4b00b7cc1680bdff7da1140f6f7&scene=21#wechat_redirect)

***1、***

检查系统网络是否能连通公网：
```shell
ping www.taobao.com
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005845129.png)

***2、***

确认yum源是否配置好，用于下载安装环境基础包：

yum源配置可以参考：

[yum源配置](http://mp.weixin.qq.com/s?__biz=MjM5MzU5NDYwNA==&mid=2247484406&idx=1&sn=53f2bbba1c7ff515646e51dc574d5ebd&chksm=a695ee7591e26763bbaaf8e7af6ec85f6853646398626f082f562466ffe63a6db27783465853&scene=21#wechat_redirect)

用以下命令测试：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005845421.jpeg)

***3、***

确定iptables是否关闭，避免对后续学习验证造成影响，当然也可以设置好对应规则：

执行命令：

```shell
iptables -F
iptables -t nat -F
```

***4、***

确认关闭selinux，避免对服务和请求造成影响，建议关闭。

**查看**SELinux状态：

```shell
/usr/sbin/sestatus -v      ##如果SELinux status参数为enabled即为开启状态

SELinux status:            enabled

getenforce                 ##也可以用这个命令检查
```

**关闭**SELinux：

临时关闭（不用重启机器）：

```shell
setenforce 0      ##设置SELinux 成为permissive模式

              ##setenforce 1 设置SELinux 成为enforcing模式
```

修改配置文件（需要重启机器）：

修改/etc/selinux/config 文件，将SELINUX=enforcing改为SELINUX=disabled

***5、***

配置nginx的yum源：

```shell
vim /etc/yum.repos.d/nginx.repo
```

```shell
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1
```

***6、***

然后执行命令测试：

```shell
yum list | grep nginx
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005845791.jpeg)

***7、***

利用yum安装nginx：
```shell
yum install nginx
```
安装完毕验证：


我这里装的是1.14.0版。

可以用命令查看nginx安装目录：

```shell
rpm -ql nginx
```

***8、***

下面对主要目录做说明：

```shell
/etc/logrotate.d/nginx
```

Nginx日志轮转，用于logrotate服务的日志切割，相当于java中的log4j和logback；

```shell
/etc/nginx                         
/etc/nginx/conf.d
/etc/nginx/conf.d/default.conf
/etc/nginx/nginx.conf
```

为Nginx主配置文件；

```shell
/etc/nginx/koi-utf              
/etc/nginx/koi-win
/etc/nginx/win-utf
```

用于nginx编码转换的配置文件；

```shell
/var/log/nginx
```

为nginx的访问和错误日志目录；

```shell
/var/cache/nginx/
```

为nginx的缓存目录；

```shell
/usr/share/nginx/html
```

其下放了首页index.html，为nginx的默认首页。

***9、***

利用以下命令启动nginx：

```shell
systemctl start nginx
```

然后访问页面：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/201910180058468.jpeg)

默认利用的是/usr/share/nginx/html目录下的index.html

之后将对nginx做进一步深入学习。

------------
