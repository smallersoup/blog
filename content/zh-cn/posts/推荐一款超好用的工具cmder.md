title: 推荐一款超好用的工具cmder
date: '2019-10-18 13:13:44'
updated: '2019-10-18 13:13:44'
tags: [工具, cmder]
permalink: /201910181313cmder
---
今天来推荐一个超级好用的命令行工具：cmder

一款Windows环境下非常简洁美观易用的cmd替代者，它支持了大部分的Linux命令。支持ssh连接linux，使用起来非常方便。比起cmd、powershell、conEmu，其界面美观简洁，功能强大。下面来看看效果：

![image](https://img-blog.csdnimg.cn/20191018001448994.gif)

上面演示了linux下的ls -l、vi，以及vi编辑中的删除行，复制、粘贴，跳到行首、行尾。等基本命令，通过设置别名可以让操作起来更加方便。

1、   把解压后的目录加到系统环境变量，然后win  R，输入cmder即可快捷打开：

如下：

![image](https://img-blog.csdnimg.cn/20191018001449186.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

2、  通过ctrl 鼠标滚轮调整字体大小；

![image](https://img-blog.csdnimg.cn/20191018001450780.gif)

3、  添加cmder到右键菜单

打开cmder命令窗口，输入：

```shell
$ cmder.exe /REGISTER ALL
```

效果如下：

![image](https://img-blog.csdnimg.cn/20191018001451442.gif)

4、   解决中文乱码：

在Settings ->Startup -> Environment中添加一行：
```shell
set LC_ALL=zh_CN.UTF-8
```
如下：记得加后面的分号哦！

![image](https://img-blog.csdnimg.cn/20191018001451625.png)

5、  修改命令提示符号：

cmder默认的命令提示符是λ，如果想改成常见的$ ,具体操作如下：

打开cmder安装目录下的\vendor\clink.lua文件，

找到42行的"{lamb}'' 改为想要的符号，然后重启cmder即可。

![image](https://img-blog.csdnimg.cn/20191018001451826.png)

6、  设置别名：

cmder原生没有** ll **命令，但可以通过设置别名来实现：

打开cmder安装目录下的\config\user-aliases.cmd文件，添加以下别名设置：

```shell
l=ls --show-control-chars -F --color $*
la=ls -aF --show-control-chars -F --color $*
ll=ls -alF --show-control-chars -F --color $*
```

如下：

![image](https://img-blog.csdnimg.cn/2019101800145231.png)

7、  快捷键：

另外还可以利用快捷键

ctrl u：删除当前命令行内容；

ctrl l：清屏；

鼠标选中复制，右键粘贴~~~

![image](https://img-blog.csdnimg.cn/20191018001453772.gif)

其他功能请移步google查看。


------------
