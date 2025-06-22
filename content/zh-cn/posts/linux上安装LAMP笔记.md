title: linux上安装LAMP笔记
date: '2019-10-18 13:11:44'
updated: '2019-10-18 13:11:44'
tags: [linux, lamp]
permalink: /201910181311linux
---
B哥最近在参加比赛，需要把一个php项目部署到服务器上，故此在linux上安装LAMP环境，用于部署项目，第一次安装，做点儿笔记记录一下。

![image](https://img-blog.csdnimg.cn/20191017235607126.jpeg)

安装条件：

Redhat或者CentOS linux环境已装好，并配置了yum源。

用yum安装httpd、mariadb、php

安装httpd：

```
yum -y install httpd
```

安装mariadb：

```
yum -y install mariadb-server
```

安装php：

```
yum -y install php php-mysql
```

检查安装包

```
rpm -qa|grep -P "httpd|php|maria"
```

正常情况输出如下：

![image](https://img-blog.csdnimg.cn/20191017235607313.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

启动httpd：

```
systemctl start httpd
```

验证httpd启动是否正常：

在index.html文件里加入http running字符串：

```
echo “-----------------httpd running.-------------” > /var/www/html/index.html
```

然后用curl命令调接口：

```
curl -k http://localhost:80 -v
```

正常返回如下：

![image](https://img-blog.csdnimg.cn/20191017235607534.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

**问题解决：**

启动后用curl调返回403 Forbidden：

![image](https://img-blog.csdnimg.cn/20191017235607754.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

google查了资料也没有查到解决方法，然后无意间重启了一把竟然好了：

```
systemctl restart httpd
```

具体原因就不得而知了。重启以后在用curl命令调用就返回200OK了。

启动mariadb：

```
systemctl start mariadb
```

然后登陆数据库，执行mysql命令，结果报错如下：

```
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)
```

![image](https://img-blog.csdnimg.cn/20191017235607954.png)

这个谷哥上倒是有解决办法：

1、首先stop数据库服务mariadb.service

```
systemctl stop mariadb.service
```

2、使用mysqld_safe启动mysqld：

```
mysqld_safe --user=mysql --skip-grant-tables --skip-networking &
```

![image](https://img-blog.csdnimg.cn/20191017235608529.jpeg)

3、然后登陆数据库：

```
mysql -u root mysql
```

切换到mysql数据库：

```
use mysql;
```

给root用户设置新的密码，这里newpassword就是新密码：

```
UPDATE user SET PASSWORD=PASSWORD('newpassword') where USER='root';
```

更新权限：

```
FLUSH PRIVILEGES;
```

然后退出数据库：

```
quit
```

然后登陆数据库：

```
mysql -uroot -p
```

输入密码，登陆进去如下：

![image](https://img-blog.csdnimg.cn/20191017235608705.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

测试php：

在index.php文件中加入以下字符：

```
echo " The PHP is running. ?php phpinfo(); ?> ">/var/www/html/index.php
```

然后curl调接口：

```
curl -k http://localhost:80/index.php -v
```

正常情况返回200OK，以及刚才插入Index.php中的字符串：

![image](https://img-blog.csdnimg.cn/20191017235609648.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

至此LAMP已搭建完毕，小B哥准备部署项目喽。

------------
