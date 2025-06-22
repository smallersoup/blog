title: 学习openresty时，nginx的一个坑
date: '2019-10-18 13:34:48'
updated: '2019-10-18 13:34:48'
tags: [openresty, nginx]
permalink: /201910181334nginx
---

## 正文

#### 报错：
nginx: [error] CreateFile() "./logs/nginx.pid" failed (2: The system cannot find the file specified)

博主在执行了nginx -s stop后，再次启动nginx时报错：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWE0ZjJiZTBkNGRjYTA0OWUucG5n?x-oss-process=image/format,png)


这个坑主要原因就是没有nginx.pid这个文件，./logs/下找不到nginx.pid文件，看了确实找不到。

看了网上很多方案是 需要建立nginx.pid文件，也就是要指定nginx.conf这个配置文件，然后博主很傻的这样执行了一把：
```
nginx -c  conf/nginx.conf
```
还是直接说正解吧 ：开启你的cmd（命令列） 然后你需要以你nginx.exe所在路径的绝对路径，比如博主的路径在 D:\Program Files\openresty-1.13.6.2-win64

那么命令列就需要这样写
"d:\Program Files\openresty-1.13.6.2-win64\nginx.exe" -c  "d:\Program Files\openresty-1.13.6.2-win64\conf\nginx.conf"

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWZkZmQ0NTFkMmJhZGIwMzcucG5n?x-oss-process=image/format,png)

生成了nginx.pid文件：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWI0Y2QzOTA4NGU2YTA4N2MucG5n?x-oss-process=image/format,png)

里面只有一个PID号：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTMxYTRmZjljOWYwZDY3Y2YucG5n?x-oss-process=image/format,png)





---------
