---
title: 一个神秘现象引发对beego框架的思考
date: '2019-10-18 12:57:23'
updated: '2019-10-18 12:57:23'
tags: [golang, beego]
permalink: /201910181257beego
---
小强最近在项目中遇到了一个很奇怪的问题：在整改日志规范时，为了避免影响现有的代码结构以及改动尽可能小的前提下，在调用记日志的SDK处将某一个字段值首字母改为大写，代码示例如下：

```go
fmt.Println("--------SayHello begin------------")
 //项目中这里的a实际是作为参数传入,只是可能为空串,不为空串,这样写肯定没问题
 a := ""
 b := strings.ToUpper(a[:1])   a[1:]
 fmt.Println("b is ", b)
 fmt.Println("--------SayHello end------------")

 this.Ctx.Output.Body(this.Ctx.Input.RequestBody)
```

项目中这里的a变量其实是作为参数传入，只是可能为空串。a变量不为空串时，这样写肯定没问题。但是当为空串时，即""时，就会出问题，在java中，运行的时候肯定会报一个“数组下表越界”的异常。小强将工程编译后生成二进制文件，放到服务器上跑，测试修改后的日志是否符合规范，验了一遍，没有问题，然后就将代码提交了。

之后版本出来测试时发现，有个奇怪的现象：接口不返回任何东西，状态码依然是 200 OK。这让小强很纳闷儿，还好，我们的小强经验丰富，还是解决过大bug的人，然后就根据接口走了一遍代码流程，眉头一皱，就知道问题所在了。原来就是a变量有时候传进来是空字符串，导致出现了slice下标越界的panic，说干就干，小强赶紧做了空串的判断逻辑，重新验了一把，问题就解决了。

小强是爱思考的孩子，不止要解决问题，也要知其所以然。小强在想，出现了panic咋日志里面啥都不打呢，而且还返回200，甚是疑惑。然后就在网上查资料，然后自己又看了beego的源码，就明白了。不得不说，开源就是好啊。

原来问题是这样，小强项目中使用的beego版本是1.6.1版。

小强查到了beego的错误处理流程：beego通过beego.App.Server.Handler处理所有的HTTP请求，在beego.Run()函数中，这个Handler就被设置为app.Handlers，可以参见beego1.6.1版本app.go的第95行：

```go
app.Server.Handler = app.Handlers
```

而app在一开始就被初始化，可以看app.go中的init()函数，其中调用了NewApp()函数：

```go
// NewApp returns a new beego application.
func NewApp() *App {
 cr := NewControllerRegister()
 app := &App{Handlers: cr, Server: &http.Server{}}
 return app
}
```

可以看出，把cr赋值给Handler，其实cr是ControllerRegister类型，ControllerRegister类型实现了http.Handler接口，具体实现可以看router.go的第600行ServeHTTP方法。该方法中（第612行）有如下语句：

```go
defer p.recoverPanic(context)
```

> golang语言的错误处理机制是，当在某处调用panic(string)后，panic之后的语句将不再执行，而是通过调用关系逐级退出，在每一级调用处都通过defer处理函数检查是否panic被recover()函数捕获处理，如果没有则继续往上扔panic信息，如果已经被捕获则结束此次panic过程，由捕获panic的函数处继续往下执行。

出现异常会执行recoverPanic方法，该方法中（第864行）有这样的代码段：

```go
if BConfig.RunMode == DEV {
       showErr(err, context, stack)
}
```

showErr函数中会对错误进行模板渲染，而小强项目早在现网中投入使用，RunMode为prod，而非dev，所以recover()后不会有错误提示。

当RunMode为prod时：

![image](https://img-blog.csdnimg.cn/20191018004343115.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

当RunMode为prod时：

![image](https://img-blog.csdnimg.cn/20191018004343411.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

dev模式好歹会返回错误信息：slice bounds out of range

prod模式没有任何提示。下标越界这种问题看似简单，但是真正遇到了有时候也会摸不着头脑。
