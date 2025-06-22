---
title: LAMP环境部署物联网项目
date: '2019-10-18 13:12:36'
updated: '2019-10-18 13:12:36'
tags: [linux, lamp, 物联网]
permalink: /201910181312lamp
---
今天来在LAMP环境下搭建一个PHP项目，开始之前，先来普及下物联网常识：

> 物联网，即Internet of Things，简写IOT。让所有能行使独立功能的普通物体实现互联互通的网络，通过物联网可以用中心计算机对机器、设备、人员进行集中管理、控制，实现物物相连。近几年物联网在运输、物流、健康医疗、智能环境（家庭、办公、工厂）等领域都在迅速发展，前景打好。

B哥最近研究一个物联网项目：基本功能就是要在web网站和手机app端实时监控硬件上发来的数据，用于分析、集中管理与控制，硬件是基于ARM的，web端是用php开发的，基本功能可以跑起来，现在主要在这基础上实现自己的功能。上一节B哥已经在云服务器上搭建好LAMP环境（[linux上安装LAMP笔记](http://mp.weixin.qq.com/s?__biz=MjM5MzU5NDYwNA==&mid=2247484056&idx=1&sn=2789eab2d8558be71a97f1d687aa5008&chksm=a695ef1b91e2660dcf3c6e3f596130adc5244fe2592a52d4f5353001f7c30de159b1236cff15&scene=21#wechat_redirect)），接下来就要把web项目部署好服务器上。遇到了很多问题，在此一一记录。

![image](https://img-blog.csdnimg.cn/2019101800024395.jpeg)

其中项目代码结构如下：

![image](https://img-blog.csdnimg.cn/20191018000243311.png)


先把项目传到服务器上，然后解压：

```
cd /var/www/html
unzip AdminIOT
#先把目录下文件权限改为777
chmod -R 777 AdminIOT
```

用以下命令查看httpd、php、mariadb的版本：

```
rpm -qa|grep -P "httpd|php|maria"
```

分别为2.4.6、5.4.16、5.5.56

![image](https://img-blog.csdnimg.cn/20191018000243556.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

配置apache服务器的时候httpd-vhosts.conf文件在/usr/share/doc/httpd-2.4.6目录下

(windows上好像直接在conf/extra/下)，

于是在/etc/httpd/conf/httpd.conf中加入：

include /usr/share/doc/httpd-2.4.6/httpd-vhosts.conf，

结果启动时报错了。于是就把

/usr/share/doc/httpd-2.4.6/httpd-vhosts.conf文件复制到/etc/httpd/conf/extra目录下：

```
#创建目录
mkdir -p /etc/httpd/conf/extra
#复制
cp /usr/share/doc/httpd-2.4.6/httpd-vhosts.conf /etc/httpd/conf/extra
```

然后在extra下的httpd-vhosts.conf中添加如下配置：

*   DocumentRoot 为项目代码路径；

*   ServerName 服务别名，这里设置为域名，但是得在host文件里配置对应的IP，IP即为当前节点IP；

```
<VirtualHost *:80>
   ServerName www.mysmallsoup.com
   DocumentRoot "/var/www/html/AdminIOT/public"
   DirectoryIndex index.php
   <Directory "/var/www/html/AdminIOT/public">
       AllowOverride All
       Require all granted
       Options all
   </Directory>
   ErrorLog "/var/log/httpd/dummy-host2.example.com-error_log"
   CustomLog "/var/log/httpd/dummy-host2.example.com-access_log" common
</VirtualHost>
```

![image](https://img-blog.csdnimg.cn/20191018000243812.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后在http.conf配置文件中包含httpd-vhosts.conf文件：

```
cd /etc/httpd/conf
vim httpd.conf
#打开文件后在文件末尾加入以下配置：
Include conf/extra/httpd-vhosts.conf
```

![image](https://img-blog.csdnimg.cn/2019101800024418.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后将域名绑定IP：

```
vim /etc/hosts
```

加入IP 域名，如下：

```
120.79.147.88 www.mysmallsoup.com
```

然后重新启动httpd服务器：

```
systemctl restart httpd
```

**注：**如果直接在windows上用域名访问，得在windows的host里加IP 域名对应关系，但是加了以后访问会报如下错，因为域名得先备案才能用。所以下面都用IP访问。

![image](https://img-blog.csdnimg.cn/20191018000244563.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


然后在本地windows浏览器里访问http://120.79.147.88:80地址，报错：
```shell
date(): It is not safe to rely on the system's timezone settings：
```
![image](https://img-blog.csdnimg.cn/20191018000244782.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


然后在查到：

> 实际上，从 PHP 5.1.0 ，当对使用date()等函数时，如果timezone设置不正确，在每一次调用时间函数时,都会产生E_NOTICE 或者 E_WARNING 信息。而又在php5.1.0中，date.timezone这个选项，默认情况下是关闭的，无论用什么php命令都是格林威治标准时间，但是PHP5.3中好像如果没有设置也会强行抛出了这个错误的,解决此问题，只要本地化一下，就行了。

而我们使用的是PHP5.4版本，然后在php.ini文件中加入时区的配置：

```
vim /etc/php.ini#加入如下配置：date.timezone = "Asia/Shanghai"
```

![image](https://img-blog.csdnimg.cn/20191018000244953.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

加入以后，保存退出，重新启动apache服务，刷新页面，错误就解决了。

![image](https://img-blog.csdnimg.cn/20191018000245157.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

到这一步，说明项目部署流程已经打通，但是现在需要登录，那么肯定要在数据库里面先存入用户名密码等一些数据。接下来，先给数据库里导入些初始化数据。

**数据库导入数据：**

先重新启动数据库：

```
systemctl restart mariadb
```

然后试着在本地windows上用Navicat数据库管理工具导入sql脚本，用于数据库的初始化（建库、数据插入等），我习惯性的把端口写为3306（数据库默认端口），然后去连接，发现报错了：

![image](https://img-blog.csdnimg.cn/20191018000245364.png)

然后去查看3306端口是否监听：

```
netstat -anp | grep 3306
```

查不到东西，说明3306端口没有监听，这就奇怪了。然后登陆数据库：

```
mysql -uroot -p数据库密码
```

登陆进去查看数据库端口：

```
show variables like 'port';
```

![image](https://img-blog.csdnimg.cn/20191018000245543.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

发现查到的端口竟然是0，然后又查了资料，发现是启动数据库的时候加了skip-networking导致的，启动时用了如下命令：

```
mysqld_safe --user=mysql --skip-grant-tables --skip-networking &
```

--skip-networking=0表示监听配置端口，默认监听3306，等于1或者--skip-networking不赋值表示跳过端口监听，此时监听0，网络不可访问数据库，只能数据库节点访问。可以通过以下命令查看：

```
show variables like 'skip_networking';
```

![image](https://img-blog.csdnimg.cn/20191018000245722.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

发现是ON，说明开启了skip_networking，接下来我们要关掉它。

查看mysql进程：

```
ps -ef | grep mysql
```

[图片上传中...(image-3ac06c-1571321042895-17)]

然后杀掉进程，重新启动数据库：

```
kill 12080
mysqld_safe --user=mysql --skip-grant-tables --skip-networking=0 &
```

然后再来查看3306端口是否监听：

```
netstat -anp | grep 3306
```

![image](https://img-blog.csdnimg.cn/20191018000245936.png)

发现端口正常监听，然后登陆数据库，查看：

![image](https://img-blog.csdnimg.cn/20191018000246106.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

发现port为3306，skip_networking为OFF，此时再在windows上连接数据库，就ok了。

连接上数据库后，就可以导入sql文件了：

![image](https://img-blog.csdnimg.cn/20191018000246300.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


导入以后，打开刚才的web登陆页面，输入用户名和密码，发现验证码图片看不见：

![image](https://img-blog.csdnimg.cn/20191018000246489.png)


然后去看运行日志：

```
cd /var/www/html/AdminIOT/runtime/log/201806
tailf 10.log
```

然后刷新验证码，报错Call to undefined function Think\imagecreate()

![image](https://img-blog.csdnimg.cn/20191018000246681.jpeg)

然后查看如下的说法：

> 在php中imagecreate函数是一个图形处理函数，主要用于新建一个基于调色板的图像了，然后在这个基础上我们可以创建一些图形数字字符之类的，但这个函数需要GD库支持，如果没有开启GD库使用时会提示Call to undefined function imagecreate()错误。

那就试着安装一下GD库吧，执行yum安装gd命令，然后重新启动apachce服务以使安装后的GD库生效。

```
yum -y install php-gd
systemctl restart httpd
```

然后刷新页面，验证码就可以正常显示了。登陆进去以后，又报错了：Call to undefined function think\mb_strlen()。

![image](https://img-blog.csdnimg.cn/20191018000246889.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

网上有人说，遇到上述错误，是未开启php_mbstring拓展，即找到php.ini里的

;extension=php_mbstring.dll把前面的；去掉，但是找了发现没有这个扩展配置，可能是因为版本较高的原因。在/etc/php.d目录下也没找到此扩展，然后就用yum安装一个吧，然后重启apache服务：

```shell
yum install -y php-mbstring
systemctl restart httpd
```

重启以后登录页面后这个错误就没了，但是又报另一个错误：

could not find driver

![image](https://img-blog.csdnimg.cn/2019101800024780.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后安装php-mysql，安装好后，重启apache服务：

```shell
yum install php-mysql.x86_64
systemctl restart httpd
```

重新登录页面，这个错误也过去了。又报另一个错误：

SQLSTATE[28000] [1045] Access denied for user 'iotadmin'@'localhost' (using password: YES)。

![image](https://img-blog.csdnimg.cn/20191018000247283.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


然后登陆数据库，授权iotadmin用户访问权限：

```
grant all privileges on adminiot.* to 'iotadmin'@'localhost' identified by 'iotadmin';
flush privileges;
```

执行完以后，再次刷新页面，报错就过去了。接下来的又是另一个错，错误如下图：

![image](https://img-blog.csdnimg.cn/20191018000246566.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


进后台去看运行日志10.log，报错如下：

```
cd /var/www/html/AdminIOT/runtime/log/201806/
tailf 10.log
```

![image](https://img-blog.csdnimg.cn/20191018000246773.jpeg)

找到代码Base.php的198行，如下：

![image](https://img-blog.csdnimg.cn/20191018000247884.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

代码报错：Arbitrary expressions in empty are allowed in PHP 5.5 only less，

大概意思就是说“不同类型的表达式用empty判空只有PHP5.5才”，而服务器上安装的是PHP5.4版本，所以就报这个错。这里不妨换一种方式写，只要逻辑是一样的。那就改成了这样，原来的写法先注释掉。

![image](https://img-blog.csdnimg.cn/2019101800024850.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后把文件替换到服务器对应路径下，重启apache服务，刷新页面，一切OK。

![image](https://img-blog.csdnimg.cn/20191018000248294.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

到这里web项目就正常跑起来了。一路走下来，步步是坑啊，做一下笔记，记录一下坑，以后肯定会用到的。


------------
