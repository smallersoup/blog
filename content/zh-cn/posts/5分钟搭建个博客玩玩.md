title: 5分钟搭建个博客玩玩
date: '2019-10-24 23:06:39'
updated: '2019-10-26 20:15:18'
tags: [blog]
permalink: /201910242306blog
---
大家都知道最近阿里云服务器很便宜火爆，于是小编也入手了一台3年的，配置：1核2G内存，40G硬盘。

今年比去年便宜，10.24~11.11购买是1年86元，3年229元，打开以下链接参与，也可以扫描文末的海报二维码，或点击文末阅读原文

[点我参与哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦哦](http://shorturl.at/gqCZ4)

买了不能闲置着，可以搭建自己的网站、博客、代码仓库等，用处广泛着呢！有很多朋友问怎么搭建网站，怎么用？应小伙伴们的需求，今天来学习一下最简单的网站搭建，只需要5分钟，就可以轻松搭建！
可以浏览查看我的博客:

[我的博客，点我我我我我我我我我我我我我我我我我我我我我我我](http://blog.liabio.cn)

## 主页效果
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195355771.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
​
后台管理发布文章界面：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195402161.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
自带管理功能，使用github账号登陆即可。
Solo是一款小而美Java编写的博客系统，功能丰富，插件化，皮肤可选可定制，管理方便，社区活跃。
![在这里插入图片描述](https://img-blog.csdnimg.cn/2019102419541369.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

本文章介绍利用Solo开源博客系统在云服务器上搭建自己的博客，让我开始吧。

前提，把需要公网IP访问的端口，需要在阿里云控制台加到安全组里放行。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024212209565.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
## docker搭建
第一步就是安装docker
```shell
yum install docker.x86_64 -y
```
安装完成后启动docker
```shell
systemctl start docker
```
### 安装mysql
参考历史文章：
[mysql镜像安装](https://liabio.blog.csdn.net/article/details/93625504)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195425321.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195434304.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
比如用上面几行命令部署mysql，把容器内3306端口映射到宿主机的3307端口。到时候就可以用{阿里云公网IP:3307访问数据库}，mysql部署好后，先手动建库（库名 solo，字符集使用 utf8mb4，排序规则 utf8mb4_general_ci）
### 启动solo容器
然后启动容器
```shell
docker run --detach --name solo --network=host \
    --env RUNTIME_DB="MYSQL" \
    --env JDBC_USERNAME="root" \
    --env JDBC_PASSWORD="123456" \
    --env JDBC_DRIVER="com.mysql.cj.jdbc.Driver" \
    --env JDBC_URL="jdbc:mysql://47.91.6.217:3307/solo?useUnicode=yes&characterEncoding=UTF-8&useSSL=false&serverTimezone=UTC" \
    b3log/solo --listen_port=8080 --server_scheme=http --server_host=47.91.6.217
 ```
* --detach即-d参数指定后台运行，
* --name指定容器名称，
* --env指定solo系统运行数据库参数，
* --listen_port：进程监听端口
* --server_scheme：最终访问协议，如果反代服务启用了 HTTPS 这里也需要改为 https
* --server_host：最终访问域名或公网 IP，不要带端口
* --server_port：最终访问端口，使用浏览器默认的 80 或者 443 的话值留空即可

使用的镜像是b3log/solo最新版，这里比如，47.91.6.217是我阿里云公网IP，用47.91.6.217:8080访问：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195443351.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
## k8s集群中部署
mysql和solo都使用pod方式部署，分别创建mysql deployment管理pod，mysql service提供service clusterIP供solo调用；创建solo deployment管理solo服务，solo service提供简单的服务发现，solo ingress提供域名配置，入口负载均衡。如果没有域名，可以直接通过NodePort service暴露端口。

mysql的deploy，这里注意要把配置文件和数据挂载到宿主机上，便于配置文件修改，以及数据在pod重启后保留，不丢失，注意mysql5.7中要在配置文件中加修改sql_mode的值为STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION 不能有ONLY_FULL_GROUP_BY，否则执行group by语句时会报错。
```，
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  template: 
    metadata:
      labels:
        name: mysql
    spec:
      containers:
      - name: mysql 
        image: mysql:5.7.28 
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password"
        volumeMounts:
        - name: mysql-config
          mountPath: /etc/mysql/mysql.conf.d
        - name: mysql-data
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-config
        hostPath:
          path: /data/blog-solo/mysql-config/
      - name: mysql-data
        hostPath:
          path: /data/blog-solo/mysql-data/
```
mysql的service：
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels: 
    name: mysql
spec:
  type: ClusterIP
  ports:
  - port: 3306
    protocol: TCP
    targetPort: 3306
    name: http
  selector:
    name: mysql
```
solo的deploy：
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: solo
spec:
  replicas: 1
  template: 
    metadata:
      labels:
        name: solo
    spec:
      containers:
      - name: solo
        image: b3log/solo 
        imagePullPolicy: IfNotPresent
        args: ["--server_scheme=http", "--server_host=blog.liabio.cn"]
        ports:
        - containerPort: 8080
        env:
        - name: RUNTIME_DB
          value: MYSQL
        - name: JDBC_USERNAME
          value: solo
        - name: JDBC_PASSWORD
          value: solo-liabio
        - name: JDBC_DRIVER
          value: "com.mysql.cj.jdbc.Driver"
        - name: JDBC_URL
          value: "jdbc:mysql://10.100.133.125:3306/solo?useUnicode=yes&characterEncoding=UTF-8&useSSL=false&serverTimezone=UTC"
```
solo的service：
```yaml
apiVersion: v1
kind: Service
metadata:
  name: solo
  labels: 
    name: solo
spec:
  type: ClusterIP
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 8080
    name: http
  selector:
    name: solo
```
这里我用到的是ClusterIP的service，没有用到NodePort的service，是因为准备用ingress-nginx做负载。

ingress-nginx的部署方式可以参考历史文章：
[k8s中负载均衡器【ingress-nginx】部署](https://liabio.blog.csdn.net/article/details/95937129)

solo的ingress：
```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: solo
spec:
  rules:
    - host: blog.liabio.cn
      http:
        paths:
          - backend:
              serviceName: solo
              servicePort: 8080
            path: /
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024195454356.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
由于ingress-nginx组件使用hostNetwork方式部署，所以可以通过公网IP:80端口访问。

**备注：如果要部署k8s，1核2G可能扛不住，至少得2核4G**

**需要参与本次阿里云购买的可以扫描下面的码**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191024212422900.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

-----

本文首发于公众号【我的小碗汤】**本公众号**免费**提供csdn下载服务，海量IT学习资源，**如果你准备入IT坑，励志成为优秀的程序猿，那么这些资源很适合你，包括但不限于java、go、python、springcloud、elk、嵌入式 、大数据、面试资料、前端 等资源。扫码关注：

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTYzZTRkMDc2OWM2MGUyODY)
-----------
