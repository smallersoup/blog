title: nginx请求连接限制笔记
date: '2019-10-18 13:09:48'
updated: '2019-10-18 13:09:48'
tags: [nginx]
permalink: /201910181309nginx
---
之前也有写过有关于爬虫的实战练习：[go语言爬取珍爱网](http://mp.weixin.qq.com/s?__biz=MjM5MzU5NDYwNA==&mid=2247484158&idx=1&sn=20d37b629a9ae2ae47fa08ae8c9b8c7d&chksm=a695ef7d91e2666b6547fa4cecbc9032cb520a5466eb107b24ab43f48e12d89dbd1d6ea01441&scene=21#wechat_redirect)

当时爬取时当并发过大的时候，请求就会出现卡死的情况。其实这可能就是珍爱网对请求和连接进行了限制。

爬虫和反爬是个“一边攻，一边守”的技术，但我们亲爱的爬虫工程师们也一直遵守着“只攻不破”的原则。网站服务器对爬虫一直在做限制，避免服务器流量异常，负载过大，防止恶意的攻击带来带宽和资源的浪费，甚至影响业务正常运行。往往办法是限制对同一个IP的连接数和并发数进行限制。今天我们就来看看nginx的连接频率limit_conn_module和请求频率limit_req_module 限制模块。

> HTTP请求建立在一次TCP连接基础上，一次TCP请求至少产生一次HTTP请求。

**连接限制：**

**语法如下：**

```shell
Syntax:limit_conn_zone key zone=name:size;  
Default: -
Context:http
```

limit_conn_zone：一块空间，用于存放被限制连接的状态；

key：键，可以说是一个规则，就是对客服端连接的一个标识，比如可以用内置变量 — 客户端的ip；

zone：就是这块空间的名字，这个需要和location的配置相对应；

size：就是申请空间的大小。

### **limit_conn指令：**

```shell
Syntax: limit_conn zone number;
Default: -
Context: http, server, location
```

### 这里有个前提必须在http下先定义好limit_conn_zone才可以在这里引用。

这里的zone就是上面zone的名字，number就是同一时间连接的限制数。

**请求频率限制：**

```shell
Syntax: limit_req_zone key zone=name:size rate=rate;
Default: -
Context: http
```

语法和上面类似，rate为速率限制,以秒为单位多少个。

**limit_req指令：**

```shell
Syntax: limit_req zone=name [burst=number] [nodelay]
Default: -
Context: http,server,location
```

burst=number，重点说明一下这个配置，burst爆发的意思，这个配置的意思是设置一个大小为number的缓冲区当有大量请求（爆发）过来时，超过了访问频次限制的请求可以先放到这个缓冲区内，起到访问限速的作用

nodelay，如果设置，超过访问频次而且缓冲区也满了的时候就会直接返回503（Service Temporarily Unavailable）服务暂时不可用，如果没有设置，则所有请求会等待排队。

这两个默认是不需要配置的。

---

**配置示例如下：**

![image](https://upload-images.jianshu.io/upload_images/9134763-c4d22c6cfbad6533?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

\$binary_remote_addr表示二进制的IP地址，一个二进制的ip地址在32位机器上占用32个字节，那么1M可以存放多少呢，计算一下，1x1024x1024/32 = 32768，意思就是可以存放32678个ip地址，在一个会话中，比$remote_addr要节约10空间； 

rate=1r/s表示每秒只能有一个请求；

***1、***

把location下的limit配置都注释掉，用ab工具（压力测试工具）测试：

```shell
ab -n10000 -c1000 http://192.168.1.6/index.html
```

这里-n表示请求总数，-c表示同一时间的请求数。

请求之后所有请求都成功：

![image](https://upload-images.jianshu.io/upload_images/9134763-cd35a4a4f7ad66a7?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

***2、***

当只放开limit_req zone=req_zone;注释后，用压测工具ab发起同样的命令后：

![image](https://upload-images.jianshu.io/upload_images/9134763-d3b3275b24243828?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

可以看到只成功请求3个，因为req_zone配置的rate为每秒一个请求。

***3、***

当只放开location下limit_req zone=req_zone burst=3 nodelay;注释时，继续发起请求：

![image](https://upload-images.jianshu.io/upload_images/9134763-1b9dcc736a48dd8a?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

可以看到，成功了6个，比上一次多了3个。burst=3将3个请求放到缓冲区等下一秒执行。

***4、***

当只放开limit_conn conn_zone 1;注释时，使用ab进行测试。此时一个ip只能同一时刻只能建立一个连接。

