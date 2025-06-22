---
title: Go语言及Beego框架环境搭建
date: '2019-10-18 13:00:25'
updated: '2019-10-18 13:00:25'
tags: [golang, beego]
permalink: /201910181300golang
---
在开始环境搭建之前，我们先一起来看看：

**Go有什么优势：**

*   不用虚拟机，它可直接编译成机器码，除了glibc外没有其他外部依赖，部署十分方便，就是扔一个文件就完成了。

*   天生支持并发，可以充分的利用多核，很容易实现并发。

*   25个关键字，但是表达能力很强大，几乎支持大多数你在其他语言见过的特性：继承、重载、对象等。

*   内置强大的工具，Go语言里面内置了很多工具链，最好的应该是gofmt工具，自动化格式化代码，能够让团队review变得更加简单。

*   跨平台编译，如果你在windows上想生成linux上的可执行文件，只需要一条命令(set GOOS=linux)，即可以做到windows系统编译linux的应用。

**Go适合做什么**

*   服务器编程，用Go来做很合适，例如处理日志、数据打包、虚拟机处理、文件系统等

*   分布式系统，数据库代理器等

*   网络编程，这一块目前应用最广，包括Web应用、API应用、下载应用

**Go成功的项目**

*   nsq：bitly开源的消息队列系统，性能非常高，目前他们每天处理数十亿条的消息

*   docker:基于lxc的一个虚拟打包工具，能够实现PAAS平台的组建

*   packer:用来生成不同平台的镜像文件，例如VM、vbox、AWS等，作者是vagrant的作者

*   skynet：分布式调度框架

*   doozer：分布式同步工具，类似ZooKeeper

*   heka：mazila开源的日志处理系统

*   cbfs：couchbase开源的分布式文件系统

*   tsuru：开源的PAAS平台，和SAE实现的功能一模一样

*   groupcache：memcahe作者写的用于Google下载系统的缓存系统

*   god：类似redis的缓存系统，但是支持分布式和扩展性

如果你觉得Go语言很强大，也想去学习它，那么现在可以跟我一起来学习环境搭建过程。

**1、 相关软件准备：**

![image](https://img-blog.csdnimg.cn/20191018003906966.png)

*   Git：一个开源的分布式版本控制系统，可以有效、高速的处理从很小到非常大的项目版本管理，分为32和64位安装包。

*   Go：go语言安装包，分为32和64位。

*   liteIde：国人开发的一款简单、开源、跨平台的 Go 语言IDE。

**2、 安装go安装包：**

1、根据操作系统是32位或64位选择对应的go1.8.3.windows-XXX.msi文件，双击开始安装，一路下一步，即可完成安装。安装到选择目标文件夹时，可以选D盘。

![image](https://img-blog.csdnimg.cn/20191018003907164.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

2、配置环境变量。选择计算机 -> 属性 -> 高级系统设置 -> 环境变量，看系统环境变量里是否有GOROOT（默认刚才安装好后GOROOT是设置好了的，即刚才的安装目录）。为了后续工作的方便，这里配置一下GOPATH，在环境变量里新增一个GOPATH系统变量，如下图所示：

![image](https://img-blog.csdnimg.cn/20191018003907396.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

最后在Path中在添加上” %GOPATH%bin”(默认go安装包安好，这个也是设置好的)如下图所示：

![image](https://img-blog.csdnimg.cn/20191018003907701.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后确定就行。

3、在控制台中查看Go语言环境是否安装完成，windows中，用快捷键

win   R，输入cmd，打开命令提示符，输入“go”，出现下图即可：

![image](https://img-blog.csdnimg.cn/201910180039083.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

顺带说一句，Go程序的目录结构是在GOPATH文件夹下的，分为bin, pkg, 和src三个子文件夹 。

*   bin文件夹：Go的每个项目生成的二进制可执行程序。windows下会生成.exe文件，linux下会生成可执行文件。Go的最大特色之一就是可移植性，就是说，当生成一个demo.exe之后，将这个exe文件放在任意一台windows系统上（即使没有安装go安装包），也是可以执行的。这是让PHP，Python等脚本语言望成莫及的。

*   pkg文件夹：第三方库。里面存放你的项目中引用的第三方库（非官方已经提供的库）

*   src文件夹：每个次级文件夹就是代表一个go项目，里面存放源程序。

**3、 Go语言开发IDE工具LiteIDE的使用：**

解压我们下载好的 liteidex32.1.windows-qt5 ，把liteide文件夹放在你喜欢的位置，找到\LiteIDE\bin路径下的liteide.exe，非常帅气的一个太极图标，双击运行即可。

对于LiteIDE，有一些简单的设置：（以windows10的64位版本为例）

1、如下，选择win64，这个选项决定编译后生成哪个平台的可执行文件。这里选择win64，编译后将生成exe文件。

![image](https://img-blog.csdnimg.cn/20191018003908225.png)

2、点击如下图标，查看GOROOT的路径是否为Go的安装路径。

![image](https://img-blog.csdnimg.cn/20191018003908611.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

3、点击如下图标查看GOPATH，确定系统GOPATH是否为刚才环境变量里设置的GOPATH，点击确定。

![image](https://img-blog.csdnimg.cn/20191018003908827.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

然后重启liteIDE即可。

国人大牛Visualfc制作的这个IDE真的很帅气，智能提示、各种调试都有，速度也很快。

**4、 Git工具安装：**

双击安装我们下载的Git-2.15.1.2-XX-bit.exe，一路下一步安装。安装完成后，鼠标右键可以看到如下图标即可：

![image](https://img-blog.csdnimg.cn/2019101800390934.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

**5、 Beego**框架**环境搭建：**

Beego这个框架是国人大牛谢孟军写的轻量级应用框架，在他的书《Go Web编程》中就有对这个框架的说明，各种写的好。

项目地址如下:

https://github.com/astaxie/beego

在前面我们安装好了Git，这下要发挥作用了。

1、安装beego

右键点击“Git Bash”，输入go get -u -v github.com/astaxie/beego 如下图：

![image](https://img-blog.csdnimg.cn/20191018003909208.png)

等一会儿即可。安装完成后，在GOPATH路径下（我这里GOPATH的路径是
D:\SoftwareAndProgram\program\Go\Development）在D:\SoftwareAndProgram\program\Go\Development\pkg\windows_amd64\github.com\和D:\SoftwareAndProgram\program\Go\Development\src\github.com\路径下能看到astaxie文件夹，还有下级beego文件夹。

2、安装bee工具（框架生成工具）

为了方便的生成框架，右键点击“Git Bash”，输入go get -u -v github.com/beego/bee，如下图：

![image](https://img-blog.csdnimg.cn/20191018003909807.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

同样也是等一会儿即可。完成后，在D:\SoftwareAndProgram\program\Go\Development\src\github.com\beego路径下能看到bee文件夹。

同时，在GOPATH路径下的src同级的bin中，有“bee.exe”文件。

3、使用bee工具生成框架工程代码

在“开始”中找到“命令提示符”，右键“以管理员身份运行”，先进入到GOPATH的bin路径下，再输入“bee new 工程名”，如下图所示:

![image](https://img-blog.csdnimg.cn/20191018003910632.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

在GOPATH的src目录下会生成以刚才的工程名命名的文件夹。这样一个Beego框架的工程就生成成功了。

4、使用LiteIDE打开运行。

LiteIDE的“文件”中找到“打开目录”，找到刚才生成的工程文件夹，如下图：

![image](https://img-blog.csdnimg.cn/20191018003910352.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

点击“选择文件夹”，加载整个工程。

![image](https://img-blog.csdnimg.cn/20191018003910610.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

清晰的MVC一目了然。Ctrl R编译并执行。当然你也可以各种设置断点各种调试。

打开浏览器，输入“http://127.0.0.1:8080”就看到了运行的结果。

![image](https://img-blog.csdnimg.cn/20191018003911731.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

要结束运行，点击LiteIDE上的“编译输出”后面的红色小按钮即可。

![image](https://img-blog.csdnimg.cn/20191018003911959.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

**本文用到的软件，可以关注公众号后，后台回复：go环境搭建 ，获得。**

参考自：http://www.cnblogs.com/iflytek/p/3366282.html

并加以修正。


------------
