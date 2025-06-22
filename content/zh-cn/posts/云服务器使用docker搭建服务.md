title: 云服务器使用docker搭建服务
date: '2019-10-17 14:44:30'
updated: '2019-10-17 14:44:30'
tags: [docker]
permalink: /201910171444docker
---

**前提：亚马逊云已经配置好启动。**


安全组入站策略如下：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082029462.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
出站策略如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082044270.png)

登陆EC2后，默认只能用ec2-user用户登陆，然后切换到root：
```
sudo su
```
用yum执行安装docker提示No package docker avaible
```
yum install docker -y
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082141167.png)
**解决方法：**
在/etc/yum.repos.d/下加CentOS7-Base-163.repo文件：
```
vi CentOS7-Base-163.repo
```

```
# CentOS-Base.repo
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
name=CentOS-$releasever - Base - 163.com
baseurl=http://mirrors.163.com/centos/7/os/x86_64
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#released updates
[updates]
name=CentOS-$releasever - Updates - 163.com
baseurl=http://mirrors.163.com/centos/7/updates/x86_64
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras - 163.com
baseurl=http://mirrors.163.com/centos/7/extras/x86_64
gpgcheck=1
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$releasever - Plus - 163.com
baseurl=http://mirrors.163.com/centos/7/centosplus/x86_64
gpgcheck=1
enabled=0
gpgkey=http://mirrors.163.com/centos/RPM-GPG-KEY-CentOS-7
```
保存退出后，执行命令：
```
yum makecache
```
然后执行yum安装docker命令：
```
yum install docker -y
```
安装完后如下图：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082234248.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
启动docker：
```
## 启动 docker 服务
systemctl start docker
chkconfig docker on
```
查看docker版本：
```
docker version
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082306840.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
拉取 docker 镜像：

好了，现在让我们直接拉取别人做好的 docker 镜像。这里选择的是 github上的 shadowsock vpn docker 镜像，直接执行以下命令：
```
docker pull oddrationale/docker-shadowsocks
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082329678.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
运行 docker 镜像：

运行如下命令启动该 docker 镜像。
```
docker run -d -p 8001:8001 oddrationale/docker-shadowsocks -s 0.0.0.0 -p 8001 -k yourpassword-m aes-256-cfb
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/2019071508240372.png)
运行docker ps -a查看容器是否已成功运行起来了。
```
docker ps -a
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082427543.png)
linux上curl命令调：
```
curl -k localhost:8001
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082442965.png)
windows上curl命令调：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190715082452881.png)
回显如上说明已经部署好了，接下来你要干什么就是你的事了...


