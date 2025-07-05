---
title: vmware上安装linux过程记录
date: '2019-10-18 13:20:03'
updated: '2019-10-19 14:47:11'
tags: [linux, vmware]
permalink: /201910181319linux
---

## 正文

以前的电脑上安装过vmware+redhat，但是奈何电脑太老，配置太低，打开的时候超级卡，没法用。换了电脑后，再装上玩玩，故此记录一下安装过程。需要安装的小伙伴可以在此获取包然后按此步骤安装。



1、创建新的虚拟机 -> 自定义安装

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/19d8ec39fef5ede08b0a6a96f901d5b6.png)

2、选择虚拟机兼容版本，选择最高的就好

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/565476d615d8f15bb5ee01640ffb51e0.png)

3、选择安装系统的方式，我们选择稍后安装

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/3be36fe28bdbae30a0a8ceac134a6d57.png)


4、选择安装的系统类型，系统为32位的就选32位的（redhat enterprise linux 7），系统为64位的就安装64位的

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0bf3cb189380fd005471b286abdd7cb0.png)


5、设置安装的虚拟机系统名称以及安装的虚拟机存放路径，路径自己定义（建议不要放到C盘）

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/4e702060660af94dc30de809729ef1cd.png)


6、为虚拟机分配处理器（cpu）个数和每个cpu核数

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/262d3d6ac6fea122221fa1274cb3046e.png)




7、为虚拟机分配内存大小

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d05e814b060c6c2049aaa6c990455724.png)


8、选择网络类型，这里使用桥接模式，安装好后会利用该方式上网

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/64a8e9502809cadaf7c2b1572071650b.png)


9、选择使用网络类型选择I/O设备接口的控制器类型，我们选择默认

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/f887e8390d3fda729ac1d84b094ecb47.png)


10、选择虚拟磁盘类型，我们选择scsi磁盘（服务器常用磁盘类型SCSI和SAS）

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0d93959ae85b5d5a1d225a7d42d79495.png)


11、选择新建一块新的虚拟磁盘

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/f7413e23506c4bafd0c9e742b4cddf08.png)


12、定义虚拟磁盘大小，磁盘分配25G，并不是说一定占用25G的磁盘空间，是随着使用时间增加，会慢慢增加，这里选择存储为单文件

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/c6d17f1d07cdafdeeda3c073e6b54b28.png)


13、点击下一步，然后点击完成。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/1431e07b96e3929c256bcb9218297ab2.png)


14、设置刚才新建的虚拟机，编辑虚拟机设置，cd/dvd选项，使用光盘镜像安装，选择光盘路径点击确定：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/2b65a7e72b892f5f05a1c80f329d37f9.png)


15、然后开启虚拟机

如果提示以下报错：

已将该虚拟机配置为使用 64 位客户机操作系统。但是，无法执行 64 位操作。

此主机支持 Intel VT-x，但 Intel VT-x 处于禁用状态。

如果已在 BIOS/固件设置中禁用 Intel VT-x，或主机自更改此设置后从未重新启动，则 Intel VT-x 可能被禁用。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0f83a6df49a955abcfb7a5a74d4abf9f.png)


报以上的错，说明BIOS中的Intel Virtual Technology不是Enable状态，需要重启电脑，然后按F2进入BIOS设置Intel Virtual Technology为Enable，如图：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/9b2699c3f2763ecb8db682b0a1b8c9db.png)


电脑重启后重新打开虚拟机。

16、打开虚拟机后，如果提示如下图，选择不再提示，确定。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b8863bec0eb086f82bc8d3d32c2cd838.png)


17、加电进入安装选项，选择第一个选项

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/126c9f5a0730bb82cc2e16d085bd5ad2.png)


开始安装，下一步

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b9a88ccdb4549698a0371d22a10d7de0.png)


选择语言，这里是安装时候的语言，不是安装完成后的系统语言

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/c72f8d3497cc58a4045838235fb84175.png)


软件选择

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/c4131fe10c3c84268f9af0d7f81bca15.png)


这里如果安装后是带图形化的，可以选择“带GUI的服务器” -> KDE，这种方式比较耗内存和占硬盘；

如果需要安装后不带图形化的（即安装完只有黑框框，看着逼格很高），可以选择“最小安装”。

这里选择带图形化的。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/c7a7427b212394de7b98558391920b14.png)


选择安装位置，选择“我要配置分区”，点击完成

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/a5c8ad9e9af413d8d78a24b52a6136b0.png)


![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/9c2b1f2e63ebc3ef545a8c6ee3e28be2.png)


LVM改成标准分区，点击加号，挂载点 / 容量20G；点击添加挂载点。同理加swap为4G，/boot为2G

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/3a60a199cf1263edc245a0b48881cf7c.png)


点击完成，接受更改

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b4db4f9d0ee89403e038f4d6b45d344d.png)


点击开始安装：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b548e52c8277f8422498e6eef3065008.png)


然后修改ROOT用户的密码，大概过10几分钟后，安装完成，点击重启。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0addc35c7e9b1833f070c66ce72b03d1.png)


同意协议

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/7bebf6fa8c88672fb2cef43ed59ea9a5.png)


不进行kdump备份

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/cc194047e93558bdafa3191426efa85b.png)


点击完成后，选择确定重启。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/2222fa651348c4f0b3e6e1d5d283997b.png)


重启后选择系统语言，输入法，创建本地账号，位置选择上海

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/4a3a9fdb098b70e11a37e4f94e9b89b1.png)


安装好了，看看效果：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/c33772e22e66a620cae8d86ff3102eab.png)



18、接下来配置桥接模式上网

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/664d26c6d893b187b4e6e8e468eda359.png)


点击仅主机 -> 更改设置

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/a2152f63d8ce7a9907e4ca3c2f8ffdcc.png)


点桥接模式，选择网卡

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/66d402afcafd0692424bc1d1fdf0c537.png)


配置Redhat7的虚拟机设置 -> 网络适配器 -> 网络连接设置为桥接模式。

（这个在安装时候我们就选择了此模式）

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/dcbc76b0b74be62eac5c0b894d9cf38b.png)


查看本地主机IP：

打开终端，ipconfig：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/7a4d061d75cbec4c22ee6bfaab03a85e.png)


然后编辑网络配置：

```
vim /etc/sysconfig/network-scripts/ifcfg-eno16777736
```

```
BOOTPROTO=static    #static，静态ip，而不是dhcp，自动获取ip地址。
IPADDR=192.168.43.5  #设置我想用的静态ip地址，要和物理主机在同一网段，但又不能相同。
NETMASK=255.255.255.0  #子网掩码，和物理主机一样就可以了。
GATEWAY=192.168.43.1 #和物理主机一样
DNS1=114.114.114.114  #DNS服务地址，写114.114.114.114
ONBOOT=yes   #开机启用网络配置。
```

如下图所示：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d7cb5b5595f985efc18f3a33df093c94.png)


修改完后，保存退出。执行：

systemctl restart  network重启网络。

然后用ifconfig命令查看配置：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/014930f2397628eda9aa870b0c7d3227.png)


然后测试网络， 在本地ping  linux的IP，这里即：ping 192.168.43.5，然后在linux上ping本地：这里即ping  192.168.43.16，如果本地可以ping通linux，但linux不能ping通本地，说明windows开了防火墙，请关闭防火墙后重试。

在linux上ping淘宝网址：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d53692803bb0d7347837703cb068b7fa.png)


利用Firefox浏览器成功访问淘宝。

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d1fadf0d451e9444484bc2e328dfb559.png)

-----

**以上使用到的软件：VMware12、RedHat7、Xshell等软件，可以关注文末公众号，回复：【1】获取。**

----
