title: 连上公司的vpn后，电脑上不了外网解决办法
date: '2019-10-18 13:30:29'
updated: '2019-11-05 15:21:24'
tags: [windows]
permalink: /201910181330vpn
---

## 正文

最近工作需要连接公司的vpn。连接前电脑可以上外网，微信、网页都可以访问，但是连接上vpn后，只能访问公司网络了，这就有点虐了。消息收不到很不方便，也查不了资料。以下来说道说道怎么解决，因为网上查到的一些资料，只有文字，无图导致理解的费劲儿，所以下文有很多图，也对比了vpn各种配置的图，可能会有点啰嗦，还望海涵！

**电脑操作系统：win10**

## 未连接vpn之前
未连接vpn之前cmd里执行route print结果如下：
![连接前cmd里执行route print结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWUzNmI3ZTU5ZTBhNzUzZmMucG5n?x-oss-process=image/format,png)

此时网页可以正常访问：
![baidu正常访问](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTFhNjFmZGU3YmQyMjQxMmIucG5n?x-oss-process=image/format,png)

来看看vpn是这连接和配置的，服务器地址为115.236.33.122，名称随便起了个WLAN1：
![vpn配置](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTEyOGVkM2I4YTkyNDk4ZDMucG5n?x-oss-process=image/format,png)

## 不勾选“在远程网关使用默认网关”
WLAN1的属性-->>IPV4-->>高级-->>在远程网关使用默认网关，不勾选的情况下，去连接该vpn：
![在远程网关使用默认网关不勾选](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTk4M2U3N2E3YTA2NzRjNzAucG5n?x-oss-process=image/format,png)

vpn连接后：
![vpn连接后](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTI1Y2M0OTIwOTljY2I0ZDUucG5n?x-oss-process=image/format,png)

xshell连接不上公司的IP：
![xshell连接不上公司的IP](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTczOGJmMzEwNGI4ZmZjZWIucG5n?x-oss-process=image/format,png)

此时的cmd里执行route print看到如下，多了一行路由项：
![多了一行路由项](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZjMjE2YzQ0OGI3Y2EyNjAucG5n?x-oss-process=image/format,png)

此时网页可以正常访问，无线网连接处也没有黄色感叹号：
![此时网页可以正常访问](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWJiZDBmMjM1MWRkYjIzYWQucG5n?x-oss-process=image/format,png)

可以发现不勾选“在远程网关使用默认网关”的情况下，无法连接公司网络，显然是不行的。

## 勾选上“在远程网关使用默认网关”
先断开vpn，然后修改：
WLAN1的属性-->>IPV4-->>高级-->>在远程网关使用默认网关，勾选上后：
![WLAN1的IPV4-->>在远程网关使用默认网关是勾选上的](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWYxOTlkZmRiYmEwMTg5ZWIucG5n?x-oss-process=image/format,png)

再连接vpn后，xshell可以连接公司的IP了。同时无线网上有了黄色感叹号，说明此时外网是上不了的，百度无法访问：
![可以连接公司IP，但外网连接不上](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTI4YmJiNDlkNGU1NWJhNTcucG5n?x-oss-process=image/format,png)



此时的路由表多了两条路由项：
![连上vpn后，路由表多了两条路由项](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTgzZTBiNTZkMDM2YmMyMmYucG5n?x-oss-process=image/format,png)

## 解决问题
那怎么既能连接公司网，又能上外网，连接百度查资料呢？

首先需要把WLAN1的属性-->>IPV4-->>高级-->>在远程网关使用默认网关的勾去掉：

![在远程网关使用默认网关的勾去掉](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTdhMjVhNmI1OWQ0ZGRlZDUucG5n?x-oss-process=image/format,png)

然后连接vpn，连上后，无线网上没有黄色感叹号，此时可以上外网，但连接不上公司的网，接下来解决该问题。

在cmd里执行ipconfig/all命令，结果如下，可以看到WLAN1的ip地址为172.20.1.85，子网掩码为：255.255.255.255；无线局域网的ip地址为192.168.68.131，子网掩码为：255.255.255.0，网关为192.168.68.1
![ipconfig/all看到的结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWEzYjc0YThkOTkxODJhNjgucG5n?x-oss-process=image/format,png)

再执行route print可以看到如下结果：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWE0MjczZjE5ZWZkYzFhZWQucG5n?x-oss-process=image/format,png)

我们要访问公司网络，需要加公司的网段到路由表，比如我要连接10.10.103.151 IP，子网掩码255.255.0.0，那么就需要加如下的路由，其中的172.20.1.85为上面查到的WLAN1的IP，下一跳55写不写没关系：
```sh
route add -p 10.10.0.0 mask 255.255.0.0 172.20.1.85 metric 55
```
此时的route print结果如下：
![此时路由表](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZjNWNhZTBmZThkMTdmOTUucG5n?x-oss-process=image/format,png)

然后再看看公司网络是否可以连接上，xshell成功连接公司的服务器：

![此时可以正常连接公司网络](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTJkZTVlMDE1MDI2ZTRkNjEucG5n?x-oss-process=image/format,png)

此时外网也可以正常访问，查资料，聊天也方便了。下一次连接vpn可能得修改路由里的WLAN1的IP，比如下一次连接vpn后WLAN1的IP为172.20.1.86，则修改命令如下：
```sh
route change -p 10.10.0.0 mask 255.255.0.0 172.20.1.86
```



---------
