---
title: beego与curl三件事
date: '2019-10-17 15:23:44'
updated: '2019-10-17 15:23:44'
tags: [beego, golang, curl]
permalink: /201910171522beego
---
![](https://img.hacpai.com/bing/20190706.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

今天来看三件事：

#### **1、beego的两个重要参数：**

**beego.BConfig.CopyRequestBody：**

是否允许在HTTP请求时，返回原始请求体数据字节，默认为false（GET or HEAD or 上传文件请求除外）。

beego.BConfig.CopyRequestBody = false

在controller中this.Ctx.Input.RequestBody取body体时，需要注意必须把app.conf中的CopyRequestBody属性设置为true，并保证配置文件能被读取到。只有在非GET请求，this.Ctx.Input.RequestBody才能取到请求中的body体。

**beego.BConfig.RecoverPanic：**

是否异常恢复，默认值为 true，即当应用出现异常的情况，通过 recover 恢复回来，而不会导致应用异常退出。

beego.BConfig.RecoverPanic = true

在这里有一点需要说明，利用beego搭建的web工程最好用bee工具运行，因为在beego1.6.1版本，用go run运行，程序运行过程中出现了

**slice bounds out of range：**切片下标越界；

或者

**invalid memory address or nil pointer dereference：**没有初始化的地址，即空指针。

都不会打印日志，加大问题定位难度。

当使用beego1.8.3版本时，可以正常读到app.conf配置：

```go
CopyRequestBody = true
HTTPPort = 8081
```

![beego1.8.3启动](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTZkYjU4YzkwYzQ0OGY0YmIucG5n?x-oss-process=image/format,png)


同样的app.conf配置，用beego1.6.1启动后：

![beego1.6.1启动](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWY5M2YzOGVhOTk2MzBiOGIucG5n?x-oss-process=image/format,png)


但用bee工具启动时加载正常：

![bee工具启动](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM4MWE3MzRkNDU2OGJhODYucG5n?x-oss-process=image/format,png)


经查阅资料，发现这是beego1.6.1版本的bug，issue见：

***https://github.com/astaxie/beego/issues/1831***

有兴趣可以看看各位大佬激烈的讨论。

**2、beego参数接收：**

**第一种：路径参数 (Path Parameters)：**

就是用 URL 路径的一部分来作为我们获取参数值的一种方式。

如：

```go
beego.Router("/:ak/:sk", &SayHelloController, "POST:SayHello")

或者

beego.Router("/?:ak/?:sk", &SayHelloController, "GET:SayHello")
```

接收方法如下：

```go
方法一：

fmt.Println("---ak is --- ", this.GetString(":ak"))
fmt.Println("---sk is --- ", this.GetString(":sk"))



方法二：

sk1 := this.Ctx.Input.Param(":sk")
ak1 := this.Ctx.Input.Param(":ak")
```


**第二种：查询参数 (Query string)**

在 beego 中获取查询参数是十分方便的, 使用 beego.Controller.GetString() 便可以方便的获取查询参数（这个方法同样可以获取 request body 中的以 POST 方式发送的表单参数）。

在url中?之后，以&分隔的键值对。从某种意义上将这些键值对与表单是起到相同作用的，只是一个放在URL中，一个放在body中（当然表单get方式提交也是放到url中）它们都可以用不带 : 的方式获取。

```go
方法一：
//获取?后面&分隔的参数
name2 := this.Input()["name"]
age2 := this.Input()["age"]

fmt.Printf("Name2:%s Age2:%s\n", name2, age2)


方法二：

//获取?后面的参数 key不能加:
name3 := this.GetString("name")
age3 :=  this.GetString("age")

fmt.Printf("Name3:%s Age3:%s\n", name3, age3)
```

**第三种：Web 表单 (Web form)：**

可以利用 beego.Controller.GetString() 获取；如果是post的请求方式，也可以定义和表单对应的struct，然后将this.Ctx.Input.RequestBody转换为结构体对象：

```go
type MyStruct struct {
    Name string `json:"name"`
    Age int `json:"age"`
}

myStruct := MyStruct{}

json.Unmarshal(this.Ctx.Input.RequestBody, &myStruct)
```

**3、执行curl命令：**

执行curl命令调接口时，参数传递需要注意：

如：

```sh
curl -X GET http://10.119.155.114:8081/jgjgjg/sqasdasda?name=jingge&age=21 -v
```

如果直接发送，& 会被系统解析（空格等字符也会被系统解析）

需对特殊字符进行转义。上面的命令可以修改为：

```sh
curl -X GET http://10.119.155.114:8081/jgjgjg/sqasdasda?name=jingge&age=21 -v
```

在 & 前加转义符 \ （ 空格可用+或者%20取代 ）

或者给 url 加双引号，如：

```sh
curl -X GET "http://10.119.155.114:8081/jgjgjg/sqasdasda?name=jingge&age=21" -v
```

**注意：**

我测试过，在windows上用%26代替&，都会导致name取到jingge&age=21整体，而age取不到值，用 \ 转义会导致name取到jingge\，而age取不到值，如下图：

![%26代替&，\转义&](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWU4MTk5ZDhiODcyZmI5MzYucG5n?x-oss-process=image/format,png)


**%26代替&：**

![%26代替&结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWZhNDU1ZTg5OTU3MGE1ODEucG5n?x-oss-process=image/format,png)


**\ 转义&：**

![\ 转义&结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTIwMTNkNWY3ZTM4YzI4Y2QucG5n?x-oss-process=image/format,png)


唯一可行的是在url上加双引号；

在linux上用%26也会导致name取到jingge&age=21整体，而age取不到值，但是用 \ 转义和加双引号都可以。     


