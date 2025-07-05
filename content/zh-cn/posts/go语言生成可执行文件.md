---
title: go语言生成可执行文件
date: '2019-10-17 14:49:10'
updated: '2019-10-17 14:49:10'
tags: [golang]
permalink: /201910171448golang
---

## 正文
安装go后，我们一般会设置好GOROOT和GOPATH环境变量，但是有时候因为实际工作中项目结构复杂，设置的GOPATH不能满足需要时，可以在cmd设置临时的GOPATH；很多IDE，比如IDEA也可以设置全局的GOPATH和临时的GOPATH，但是编译可执行文件可能有些复杂或者通过IDE编译或者运行会出现app.conf配置文件加载不到的情况，这个坑我遇到过。请看https://github.com/astaxie/beego/issues/1831 
故通过命令的方式生成go的可执行文件。

* 比如项目结构是这样：
![项目结构](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/a049ea484a448fd7ce2cf520f4fb4269.png)

由于依赖了github.com里的beego，所以要加github.com的上级目录到GOPATH。
#### 1. 打开cmd命令窗口，用命令设置要编译包以及依赖包所在路径的环境变量，即GOPATH(该设置只对该窗口生效):
> set GOPATH=E:\ProgrammerRoute\Go\Development\

#### 2.然后设置操作系统：
* 生成windows的可执行文件:
> set GOOS=windows
* 生成linux的可执行文件:
>set GOOS=linux
#### 3.然后在src目录下执行go install
>go install sayHello
没有报错的话，会在GOPATH下生成bin和pkg目录，可执行文件在bin目录下，如图：
![可执行文件](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/4fb53dde193070823748a8671e80842d.png)

**注：**
beego1.7.0前的版本app.conf里的配置加载不到，以下的github有issue可寻：
https://github.com/astaxie/beego/issues/1831

利用beego1.7.0之后的版本，用IDE运行go工程也加载不到app.conf的配置，利用go install也加载不到；
用go run main.go可以加载app.conf，用bee工具也可以加载到。



