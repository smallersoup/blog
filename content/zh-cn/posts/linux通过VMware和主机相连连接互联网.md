---
title: linux通过VMware和主机相连连接互联网
date: '2019-10-17 14:48:20'
updated: '2019-10-17 14:48:20'
tags: [linux]
permalink: /201910171448linux
---
![](https://img.hacpai.com/bing/20181014.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

 **1.&emsp;VM8 使用固定IP：**
![VMnet8 IP设置](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/0c5b7b8d8f09e1491ce01376a868beda.png)

**2.&emsp; 这里使用NAT模式：**

![VM网络适配器设置NAT模式](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/38b8f2933d51dc140a96c39ee3b08d81.png)

**3.&emsp;VM中依次：编辑——>虚拟网络编辑器，点VMnet8 把使用本 
 地DHCP的勾去掉，子网IP和主机VM8的IP同网段，然后点NAT设置。**

![虚拟网络编辑器设置](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/74d7496b7d442fb524af73de78579c0d.png)

#### *网关IP和刚才的IP也是同一个网段。*

![NAT设置网关](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/fe2160f5829d6345d5cd93e8ad1109f7.png)

**4.&emsp;vim  /etc/sysconfig/network-scripts/ifcfg-eno16777736**

* 增加这些：

![ifcfg-eno16777736中配置](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/e570a4f7afec3fd2ef9e7eb4e7c9962b.png)
```
TYPE=Ethernet
BOOTPROTO=static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
NAME=eno16777736
UUID=0e2e0e3d-eaaf-4810-9c6a-dda5ebe0ac9c
ONBOOT=yes
IPADDR0=192.168.2.5
GATEWAY0=192.168.2.2
PREFIX0=24
DNS1=192.168.2.2
HWADDR=00:0C:29:1D:3A:DF
PEERDNS=yes
PEERROUTES=yes
IPV6_PEERDNS=yes
IPV6_PEERROUTES=yes
```
**5.&emsp;修改完以后重启network**  

systemctl restart network

或者用:
service network restart

###*注意：*

想要上网，即ping www.baidu.com不通时，

要将/etc/sysconfig/network-scripts/ifcfg-eno16777736中的DNS1和GATEWAY1设置为一样的。


