---
title: shell脚本批量调用接口
date: '2019-10-17 14:50:11'
updated: '2019-10-17 14:50:11'
tags: [shell]
permalink: /201910171449shell
---
![](https://img.hacpai.com/bing/20190405.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

**&emsp;&emsp;要求在页面查询到5000条数据，为了方便插入，用shell脚本写curl命令调用自己写的代码接口；**  

**脚本如下：**
```shell
#!/bin/bash
a=0
while [ $a -le 10 ]; do
 
  # length of ts is 13 required,Through the following way like this
  ts=`date +%s%N`      
  ts=${ts:0:13}
  
  json='{"name" : "'$1$a'", "age" : '$2', "ts" : '$ts'}'
  
  a=$((a+1))
  
  curl -k -H 'Content-Type:application/json;charset=utf-8' http://192.168.2.5:8080 -X POST -d "'$json'"

done
```
![批量curl脚本](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTcyYzgyODJjYWQxODJmZTcucG5n?x-oss-process=image/format,png)

**执行脚本**

```sh batch_curl.sh  gege  21```

**执行结果**
![10次curl执行结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTBjZGZjZGQ3Y2M2NDg0MGYucG5n?x-oss-process=image/format,png)

**该接口是用go语言提供的demo接口：如下：**

* 目录结构：
![目录结构](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTA1MjZhNDU4MGQ4Zjc1YmMucG5n?x-oss-process=image/format,png)
* app.conf
```go
copyrequestbody = true
```
* controller.go
```go
package controller

import (
	"github.com/astaxie/beego"
	"fmt"
)

type SayHelloController struct {
	beego.Controller
}

func (this *SayHelloController) SayHello(){

	fmt.Println("RequestBody is ", string(this.Ctx.Input.RequestBody))

	this.Ctx.Output.Header("Content-type", "application/json;charset=utf-8")
	this.Ctx.Output.SetStatus(200)
	this.Ctx.Output.Body(this.Ctx.Input.RequestBody)
}
```
* router.go
```go
package router

import (
	"github.com/astaxie/beego"
	"sayHello/controller"
)

var hello = controller.SayHelloController{}

func init() {

	beego.Router("/", &hello, "POST:SayHello")
}
```
* main.go
```go
package main

import (
	"github.com/astaxie/beego"
	_ "sayHello/router"
	"fmt"
)

func main() {
	fmt.Println(beego.BConfig.CopyRequestBody)
	beego.Run()
}
```








