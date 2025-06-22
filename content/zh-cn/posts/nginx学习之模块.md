title: nginx学习之模块
date: '2019-10-18 13:09:03'
updated: '2019-10-18 13:09:03'
tags: [nginx]
permalink: /201910181308nginx
---
***1、***

**stub_status模块：**

用于展示nginx处理连接时的状态。

配置语法如下：

```shell
Syntax：stub_status;
Default：默认没有配置
Context：server、location
```

可以编辑default.conf，加上如下配置：

```shell
vim /etc/nginx/conf.d/default.conf
```

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTRkNWViMjJjYWQ3M2NlODU?x-oss-process=image/format,png)

然后检查配置的正确性：

```shell
#-t 表示检查配置文件；-c表示检查指定的配置文件，默认为/etc/nginx/nginx.conf
nginx -t -c /etc/nginx/nginx.conf
```

这里注意了，虽然修改的是default.conf，但是检查的时候始终还是加载nginx.conf，否则报错：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTlhMTE3NjUyYTJiNjBjNTk?x-oss-process=image/format,png)


因为nginx.conf中include了conf.d目录下的所有.conf文件。

然后重新加载配置文件：

```shell
#-s表示给master进程发送信号：stop、quit、reopen、reload；-c指定配置文件目录
nginx -s reload -c /etc/nginx/nginx.conf
```

![image.gif](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTk1Yjc2MDU1NjEwYjFlNjEuZ2lm)

**Active connections**: 对后端发起的活动连接数；

**Server accepts handled requests**: Nginx总共处理了13个连接,成功创建13次握手（证明中间没有失败的），总共处理了7个请求；

**Reading**: Nginx 读取到客户端的Header信息数；

**Writing**: Nginx 返回给客户端的Header信息数；

**Waiting**: 开启keep-alive的情况下,这个值等于 active – (reading + writing),意思就是Nginx已经处理完成,正在等候下一次请求指令的驻留连接。

所以，在访问效率高,请求很快被处理完毕的情况下，Waiting数比较多是正常的。如果reading +writing数较多，则说明并发访问量非常大，正在处理过程中。

***2、***

**random_index模块：**

指定目录中选择一个随机主页。

配置语法：

```shell
Syntax：random_index on | off;
Default：random_index off;默认是关闭的
Context：location  在location下配置
```


在配置文件default.conf中加random_index on;并修改很目录为自定义的指定目录。

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM3MjViNmY5ZjczZWIwZmM?x-oss-process=image/format,png)

在指定目录里放显示三种颜色的html页面：

```shell
black.html   green.html   red.html
```
```shell
<html>
<head>
      <meta charset="utf-8"/>
      <title>nginx-test</title>
</head>

<body style="background-color:red;">
</body>

</html>
```

然后reload nginx服务：

```shell
systemctl reload nginx.service
```

用浏览器访问随着刷新会显示不同颜色的页面。值得注意的是，nginx是不会加载指定目录下隐藏文件的.

***3、***

**sub_module模块：**

主要用于HTTP内容替换。

语法如下：
```shell
1、
Syntax：sub_filter old_string new_string; 把old_string替换为new_string
Default：没有配置
Context：http、server、location下配置
把old_string替换为new_string

2、
Syntax：sub_filter_last_modified on|off;
Default：sub_filter_last_modified off;
Context：http、server、location下配置
表示客户端和服务端交互时，nginx校验服务端内容是否有变更，主要用于缓存场景。

3、
Syntax：sub_filter_once on|off;  
Default：sub_filter_once on;  
Context：http、server、location下配置
表示默认匹配字符串个数；默认状态下是匹配第一个。
```

在指定目录下建一个submodule.html文件：
```html
<html>
<head>
       <meta charset="utf-8"/>
       <title>nginx-test</title>
</head>
<body>
       <h2>smallsoup test tomcat test tomcat </h2>
</body>
</html>
```

然后在default.conf中配置这个目录为根目录，并配置sub_filter：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWViNDNhODRmNDA1NGRkZGQ?x-oss-process=image/format,png)

用于把html中的tomcat修改为nginx，reload nginx后可以看到页面：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZlOTFmMjVlYTZlMDczZjQ?x-oss-process=image/format,png)


但是只修改了第一个tomcat，第二个没有修改；如果要全部替换，需要配置：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTkwMGQ4NDE1NWNhYTYwNzM?x-oss-process=image/format,png)

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTc3ODQ3NDM4NmMyNTAxOTg?x-oss-process=image/format,png)

如果遇到页面上没有替换的情况，可能是浏览器缓存导致，需要强制刷新或者清理缓存后刷新。


