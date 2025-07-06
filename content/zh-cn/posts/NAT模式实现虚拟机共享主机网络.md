---
title: NAT模式实现虚拟机共享主机网络
date: '2019-10-18 13:20:47'
updated: '2019-10-18 13:20:47'
tags: [linux]
permalink: /201910181320linux
---
上一节我们在虚拟机上搭建了linux系统，并利用桥接模式访问互联网，这一节，我们来配置一下通过NAT模式访问互联网。说到这里有些小伙伴可能要问了，NAT模式和桥接模式有什么区别呢？

**桥接模式：**

虚拟机虚拟出来的系统和局域网内的独立主机属于同等地位，它可以访问局域网内任何一台机器，该模式下，我们得为虚拟主机——linux配置IP地址，子网掩码，而且该IP要和宿主机的IP是同一网段。如果我们需要在局域网内建立一个虚拟服务器，并为局域网用户提供服务，那就得选择该模式。

**NAT模式：**

Nat模式，虚拟机通过宿主机所在的网络来访问internet，即虚拟机把宿主机作为路由器来访问互联网。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018001916330.jpeg)

开始配置

1、VM8 使用固定IP：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018001916557.jpeg)

2、 这里使用NAT模式：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018001916793.jpeg)

3、VM中依次：编辑——>虚拟网络编辑器，点VMnet8 把使用本
地DHCP的勾去掉，子网IP和主机VM8的IP同网段，然后点NAT设置。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/2019101800191723.jpeg)

#### **网关IP和刚才的IP也是同一个网段。**

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018001917237.jpeg)

4. 修改网络配置

```shell
vim /etc/sysconfig/network-scripts/ifcfg-eno16777736
```

增加这些：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018001917447.png)

```shell
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

5. 修改完以后重启network

```shell
systemctl restart network
```

或者用:

```shell
service network restart
```

### **注意：**

想要上网，即ping www.baidu.com不通时，要将/etc/sysconfig/network-scripts/ifcfg-eno16777736中的DNS1和GATEWAY1设置为一样的地址。

------------
