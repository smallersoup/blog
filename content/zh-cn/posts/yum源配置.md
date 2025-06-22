---
title: yum源配置
date: '2019-10-18 13:21:40'
updated: '2019-10-19 14:41:50'
tags: [linux, yum]
permalink: /201910181321linux
---
在配置yum前首先得说说rpm，在redhat和centos linux系统上，rpm作为软件包管理工具，可以方便的安装、查询、卸载软件包。常见命令如下：

```sh
#安装：
rpm -ivh jdk-7u25-linux-x64.rpm

#卸载：
rpm -e jdk-7u25-linux-x64.rpm

#升级：
rpm -Uvh jdk-7u25-linux-x64.rpm

#查询软件的安装路径：
rpm -ql yum-3.4.3-118.el7.noarch

#查询所有安装的包：
rpm -qa 

#查询某个文件是哪个rpm包产生：
rpm -qf /var/lib/yum/yumdb

```

但是在多个包组成的rpm包用rpm命令安装时，其依赖包问题是超级繁琐的。



yum是redhat和centos的软件包管理工具，安装软件包时可以在网上远程仓库或者本地自动下载所有依赖包，解决了rpm的痛点。今天主要学习下远程yum源配置。由于redhat 自带的 yum 源是需要注册收费才能更新下载软件的，如果没有注册就使用，则会报下面的错误：

```
This system is not registered to Red Hat Subscription Management. You can use subscription-manager to register.
```

所以我们需要把yum源修改为centos的源。



查看自带yum：

```sh
rpm -qa | grep yum
```

卸载自带yum：
```sh
rpm -qa | grep yum | xargs rpm -e --nodeps
```
![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMmNjN2M0Y2U4ODk2NTQyOA?x-oss-process=image/format,png)

查看系统版本：

```
cat /etc/redhat-release
```

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtYWZhNzg3NzBiYTZkYTZiMw?x-oss-process=image/format,png)

下载安装软件包：

```
#下载链接
http://mirrors.163.com/centos/7/os/x86_64/Packages/

#需要下载以下三个rpm包：
yum-metadata-parser-1.1.4-10.el7.x86_64.rpm  
yum-3.4.3-158.el7.centos.noarch.rpm
yum-plugin-fastestmirror-1.1.31-45.el7.noarch.rpm
```

执行以下安装命令报错，依赖包的版本不符：

```
#执行yum安装
rpm -ivh yum*
```
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWUyYTI2YTEwYzU2YjlkOTMucG5n?x-oss-process=image/format,png)


这里升级python-urlgrabber和rpm包版本：

```
#升级rpm包到：
rpm-4.11.3-32.el7.x86_64.rpm  
python-urlgrabber-3.10-8.el7.noarch.rpm  

#下载
wget http://mirrors.163.com/centos/7/os/x86_64/Packages/rpm-4.11.3-32.el7.x86_64.rpm
wget http://mirrors.163.com/centos/7/os/x86_64/Packages/python-urlgrabber-3.10-8.el7.noarch.rpm

#升级
rpm -Uvh rpm-4.11.3-32.el7.x86_64.rpm --nodeps
rpm -Uvh python-urlgrabber-3.10-8.el7.noarch.rpm --nodeps
```

然后安装：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRkMjkwMDA3Njg0MmYzODkucG5n?x-oss-process=image/format,png)


新建配置文件：

```
vim /etc/yum.repos.d/CentOS-Base.repo
```

加入以下配置：

```
#CentOS-Base.repo
#
# The mirror system uses the connecting IP address of the client and the
# update status of each mirror to pick mirrors that are updated to and
# geographically close to the client.  You should use this for CentOS updates
# unless you are manually picking other mirrors.
#
# If the mirrorlist= does not work for you, as a fall back you can try the
# remarked out baseurl= line instead.
#
#
[base]
name=CentOS-$7 - Base - 163.com
#mirrorlist=http://mirrorlist.centos.org/?release=$7&arch=$basearch&repo=os
baseurl=http://mirrors.163.com/centos/7/os/$basearch/
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#released updates
[updates]
name=CentOS-$7 - Updates - 163.com
#mirrorlist=http://mirrorlist.centos.org/?release=$7&arch=$basearch&repo=updates
baseurl=http://mirrors.163.com/centos/7/updates/$basearch/
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that may be useful
[extras]
name=CentOS-$7 - Extras - 163.com
#mirrorlist=http://mirrorlist.centos.org/?release=$7&arch=$basearch&repo=extras
baseurl=http://mirrors.163.com/centos/7/extras/$basearch/
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$7 - Plus - 163.com
baseurl=http://mirrors.163.com/centos/7/centosplus/$basearch/
gpgcheck=1
enabled=0
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7
```

然后清理缓存：

```
yum clean all
```

生成缓存：

```
yum makecache
```

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtY2VlMjVlN2E4MzRjYjYyYQ?x-oss-process=image/format,png)

测试源：

```
yum update -y --skip-broken
```

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMDBlZWFkNzM0NzJlODgxNA?x-oss-process=image/format,png)

可以看到已经可以通过yum安装相关软件包更新。

-----
