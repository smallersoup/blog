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

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNTdlYzllMjYzYTZhOWQ0Zg?x-oss-process=image/format,png)

2、选择虚拟机兼容版本，选择最高的就好

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNmU5N2ViYzViZjAxNmQ2YQ?x-oss-process=image/format,png)

3、选择安装系统的方式，我们选择稍后安装

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWY0NzUzMWE4YjZlMTQxY2UucG5n?x-oss-process=image/format,png)


4、选择安装的系统类型，系统为32位的就选32位的（redhat enterprise linux 7），系统为64位的就安装64位的

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM2MTdmMjMxY2ZjMWI0ZTAucG5n?x-oss-process=image/format,png)


5、设置安装的虚拟机系统名称以及安装的虚拟机存放路径，路径自己定义（建议不要放到C盘）

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTQxOGExZDUzZmM5MjBjYTUucG5n?x-oss-process=image/format,png)


6、为虚拟机分配处理器（cpu）个数和每个cpu核数

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRmNWFmYjAwMjVjOWRiOWMucG5n?x-oss-process=image/format,png)




7、为虚拟机分配内存大小

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWI4NmY3NzYwNmY3ZGM4MDAucG5n?x-oss-process=image/format,png)


8、选择网络类型，这里使用桥接模式，安装好后会利用该方式上网

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTM2ODkyODhiMGQyZDMxMjAucG5n?x-oss-process=image/format,png)


9、选择使用网络类型选择I/O设备接口的控制器类型，我们选择默认

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTYyOTIwNzRjYTdhNzg0NTIucG5n?x-oss-process=image/format,png)


10、选择虚拟磁盘类型，我们选择scsi磁盘（服务器常用磁盘类型SCSI和SAS）

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWQ4MzUwYzM5NGQ5ZjNhZTMucG5n?x-oss-process=image/format,png)


11、选择新建一块新的虚拟磁盘

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWVmNzkwNzAyMzA2N2Y0Y2EucG5n?x-oss-process=image/format,png)


12、定义虚拟磁盘大小，磁盘分配25G，并不是说一定占用25G的磁盘空间，是随着使用时间增加，会慢慢增加，这里选择存储为单文件

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTNkNDMwOTc1MmQ0MDUzM2MucG5n?x-oss-process=image/format,png)


13、点击下一步，然后点击完成。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWQ0NzZjMmQ1YWQ1NmY2YjgucG5n?x-oss-process=image/format,png)


14、设置刚才新建的虚拟机，编辑虚拟机设置，cd/dvd选项，使用光盘镜像安装，选择光盘路径点击确定：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZhNDk5ZDc1YmRiNGY1ZmEucG5n?x-oss-process=image/format,png)


15、然后开启虚拟机

如果提示以下报错：

已将该虚拟机配置为使用 64 位客户机操作系统。但是，无法执行 64 位操作。

此主机支持 Intel VT-x，但 Intel VT-x 处于禁用状态。

如果已在 BIOS/固件设置中禁用 Intel VT-x，或主机自更改此设置后从未重新启动，则 Intel VT-x 可能被禁用。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWVjNjJiNjA0NDliNzY2NGEucG5n?x-oss-process=image/format,png)


报以上的错，说明BIOS中的Intel Virtual Technology不是Enable状态，需要重启电脑，然后按F2进入BIOS设置Intel Virtual Technology为Enable，如图：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWJkYzFiNjY0NGU2NjAyNmUucG5n?x-oss-process=image/format,png)


电脑重启后重新打开虚拟机。

16、打开虚拟机后，如果提示如下图，选择不再提示，确定。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTJiZmMwMTc3NmFlY2U0MzAucG5n?x-oss-process=image/format,png)


17、加电进入安装选项，选择第一个选项

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTdmMGMyYWRkYzkwZDNkYmEucG5n?x-oss-process=image/format,png)


开始安装，下一步

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWUyM2VkYzJkM2M1ZGRkYzQucG5n?x-oss-process=image/format,png)


选择语言，这里是安装时候的语言，不是安装完成后的系统语言

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTgxMDk1NTMxOTJkNmEzNmMucG5n?x-oss-process=image/format,png)


软件选择

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTM4MTU1N2UxN2RmMjI3MzUucG5n?x-oss-process=image/format,png)


这里如果安装后是带图形化的，可以选择“带GUI的服务器” -> KDE，这种方式比较耗内存和占硬盘；

如果需要安装后不带图形化的（即安装完只有黑框框，看着逼格很高），可以选择“最小安装”。

这里选择带图形化的。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWNhNzBhYjUzMjkwNWVlOGEucG5n?x-oss-process=image/format,png)


选择安装位置，选择“我要配置分区”，点击完成

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTQ2YmJkZmI4NzdlYzdlNjkucG5n?x-oss-process=image/format,png)


![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWIwMmUxYjhkZGEwNDEwNTMucG5n?x-oss-process=image/format,png)


LVM改成标准分区，点击加号，挂载点 / 容量20G；点击添加挂载点。同理加swap为4G，/boot为2G

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTc4N2M5MmU0NmExMzg1YTEucG5n?x-oss-process=image/format,png)


点击完成，接受更改

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTU5MTk2YzViNDgwNDAzZDcucG5n?x-oss-process=image/format,png)


点击开始安装：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTU1YTA3NWQ1YzQyNDBmYzcucG5n?x-oss-process=image/format,png)


然后修改ROOT用户的密码，大概过10几分钟后，安装完成，点击重启。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWFlOGJkZTM2M2VhNTc1YmUucG5n?x-oss-process=image/format,png)


同意协议

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTFlNTBhOTdkNmIyMTA4YTgucG5n?x-oss-process=image/format,png)


不进行kdump备份

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWU2YjQwNDNlYzhhMGU4MjMucG5n?x-oss-process=image/format,png)


点击完成后，选择确定重启。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTk3YzBiZTJmYTMwMjhmM2QucG5n?x-oss-process=image/format,png)


重启后选择系统语言，输入法，创建本地账号，位置选择上海

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTIwZmEzNDJlYTUzOWNjMGEucG5n?x-oss-process=image/format,png)


安装好了，看看效果：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTc4YjA3YmFiMzE0OGZlMjEucG5n?x-oss-process=image/format,png)



18、接下来配置桥接模式上网

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTIwYmY3YTAyMDJiZTk0YjgucG5n?x-oss-process=image/format,png)


点击仅主机 -> 更改设置

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWZlMTA2YzQzMzg5ZjYwNDgucG5n?x-oss-process=image/format,png)


点桥接模式，选择网卡

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWNmZTA4M2JkZmFlNmYxYTEucG5n?x-oss-process=image/format,png)


配置Redhat7的虚拟机设置 -> 网络适配器 -> 网络连接设置为桥接模式。

（这个在安装时候我们就选择了此模式）

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTExZDA2ZDg0MzdmN2JiNjEucG5n?x-oss-process=image/format,png)


查看本地主机IP：

打开终端，ipconfig：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWRkOTkxODEzMzNmNTcwZmUucG5n?x-oss-process=image/format,png)


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

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWJmZjE2MzE3NjZkZjg3MWIucG5n?x-oss-process=image/format,png)


修改完后，保存退出。执行：

systemctl restart  network重启网络。

然后用ifconfig命令查看配置：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTY0YWQwMmExNTNhODYwYWUucG5n?x-oss-process=image/format,png)


然后测试网络， 在本地ping  linux的IP，这里即：ping 192.168.43.5，然后在linux上ping本地：这里即ping  192.168.43.16，如果本地可以ping通linux，但linux不能ping通本地，说明windows开了防火墙，请关闭防火墙后重试。

在linux上ping淘宝网址：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWFkNDQyYjVmZWRjMzM2YzYucG5n?x-oss-process=image/format,png)


利用Firefox浏览器成功访问淘宝。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTkzZDY1ZDc3ODdhODQ2MzYucG5n?x-oss-process=image/format,png)

-----

**以上使用到的软件：VMware12、RedHat7、Xshell等软件，可以关注文末公众号，回复：【1】获取。**

----
