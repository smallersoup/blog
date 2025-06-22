title: linux通过VMware和主机相连连接互联网
date: '2019-10-17 14:48:20'
updated: '2019-10-17 14:48:20'
tags: [linux]
permalink: /201910171448linux
---
![](https://img.hacpai.com/bing/20181014.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

 **1.&emsp;VM8 使用固定IP：**
![VMnet8 IP设置](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWUzMzA0OGM5ZWU3Njg2ODEucG5n?x-oss-process=image/format,png)

**2.&emsp; 这里使用NAT模式：**

![VM网络适配器设置NAT模式](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRkZmU0ZGRhN2M3NzBjMDgucG5n?x-oss-process=image/format,png)

**3.&emsp;VM中依次：编辑——>虚拟网络编辑器，点VMnet8 把使用本 
 地DHCP的勾去掉，子网IP和主机VM8的IP同网段，然后点NAT设置。**

![虚拟网络编辑器设置](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWU5ZTgzMDk2NzQ2MjhlZGQucG5n?x-oss-process=image/format,png)

#### *网关IP和刚才的IP也是同一个网段。*

![NAT设置网关](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWZmYjZiOTc2NTJkZDRjYmIucG5n?x-oss-process=image/format,png)

**4.&emsp;vim  /etc/sysconfig/network-scripts/ifcfg-eno16777736**

* 增加这些：

![ifcfg-eno16777736中配置](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWZlOWQ1YzM0YzljZGFiZDkucG5n?x-oss-process=image/format,png)
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


