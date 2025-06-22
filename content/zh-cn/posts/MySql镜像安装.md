---
title: MySql镜像安装
date: '2019-10-17 15:21:00'
updated: '2019-10-17 15:21:00'
tags: [mysql, docker]
permalink: /201910171520mysql
---
![](https://img.hacpai.com/bing/20181021.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文



* * *

## 安装MySql镜像

```
> docker search mysql #查找MySql镜像版本
> docker pull mysql:tag #安装指定版本的mysql镜像，tag为版本号

```

例如：

```
> docker pull mysql:5.6 #安装MySql 5.6版本镜像

```

## 启动MySql容器

```
> docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag

```

例如：

```
> docker run --name test-mysql -e MYSQL_ROOT_PASSWORD=123456 -d  -p 3306:3306 mysql:5.6 
#启动mysql 5.6版本镜像容器，通过--name取名test-mysql，设置root用户密码为123456，映射host的3306端口访问mysql

```

## 从host连接上述启动的container

```
> ifconfig #查看下docker虚拟出的ip地址
> docker ps -a #查看下容器的运行状态
> mysql -h {ip} -P {port} -u root -p #从host连接docker中的MySql

```

例如：

```
> mysql -h 192.168.0.1 -P 3306 -u root -p

```

如果可以进入mysql命令终端，则表示一切安装配置成功。

**如果要用远程用Navicat连接mysql：**

创建honey用户，密码也为honey
```
create user'honey'@'%'identified by'honey';
```
查看用户honey的权限
```
show grants for 'honey'@'%';
```

创建数据库，honey用户只有操作museum_of_art数据库的权限。
```
create database museum_of_art;
```

允许用户honey操作museum_of_art表
```
grant all on museum_of_art.* to'honey'@'%';
```

开最大权限：
```
GRANT ALL PRIVILEGES ON *.* TO 'honey'@'localhost' IDENTIFIED BY 'honey';
GRANT ALL PRIVILEGES ON *.* TO 'honey'@'%' IDENTIFIED BY 'honey';
```


**但这里有个问题如果要公网访问的话要注意几个点。首先是docker版本问题，我这里安装的是1.13.1 docker ，那么不需要再去开启http远程访问，默认是可以访问的。**

现在如果用在公网上用Navicat 是链接不上的。

原因如下：

首先需要登陆阿里云后台，添加阿里云安全组策略   具体位置--网络和安全--安全组--配置规则

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZjRkYTk2NjRiZDIxYjA5ZQ?x-oss-process=image/format,png) 

可以选择多配置你需要的端口。

下面我们需要配置阿里云防火墙

*   查看下防火墙的状态：

```
systemctl status firewalld
```

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMzk2ZTEzMGY3ZTUwMmNjZg?x-oss-process=image/format,png)

*   关闭防火墙：

```
systemctl stop firewalld
```

其实这样就可以使用了，但是这样是很不安全，我们可以将**firewall**服务禁用，应用**iptables**服务（网上大部分启用端口的资料都是基于**iptables**服务）。

## 安装iptables

由于没有防火墙会造成不安全，所以给服务器安装一应用更广的防火墙**iptables**，首先要禁用**firewall**，通过**yum**安装**iptables**：

```
systemctil disable firewalld
yum install -y iptables-services
```

## 启动iptables

```
systemctl start iptables
```

启动后可以通过systemctl status iptables查看状态。

## 更改iptables规则

*   将iptables文件备份下：

```
cp -a /etc/sysconfig/iptables /etc/sysconfig/iptables.bak
```

*   设置 INPUT 方向所有的请求都拒绝

```
iptables -P INPUT DROP
```

*   放开所需端口

```
iptables -I INPUT -p tcp --dport 3306 -m state --state NEW -j ACCEPT
```

*   保存规则

```
iptables-save > /etc/sysconfig/iptables
```

*   设置为开机启动并且重启

```
systemctl enable iptables.service
systemctl reboot
```

好了，系统到这里我们需要重新去启动docker 
```
systemctl start docker #运行Docker守护进程
```

这里如果直接启动镜像的话会报这个错误

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNWNhNGNhZTgwMzZjMWRjNw?x-oss-process=image/format,png)

那么我们只需要重启下docker  ,再去开启你的容器就OK了 
```
systemctl restart docker
```

那么到这里我们外网就可以正常的去使用阿里云这里的mysql服务

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtYTEzMjJhNDMwYWVkYTM5Yg?x-oss-process=image/format,png)



