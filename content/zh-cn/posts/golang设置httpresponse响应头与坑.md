---
title: golang 设置 http response 响应头与坑
date: '2019-10-17 18:02:26'
updated: '2019-10-17 18:02:26'
tags: [golang]
permalink: /201910171802golang
---

## 正文

**1、 设置WriteHeader的顺序问题**


之前遇到个问题，在一段代码中这样设置WriteHeader,最后在header中取Name时怎么也取不到。

```go
w.WriteHeader(201)
w.Header().Set("Name", "my name is smallsoup")
```

 用 golang 写 http server 时，可以很方便可通过 w.Header.Set(k, v) 来设置 http response 中 header 的内容。但是需要特别注意的是：某些时候不仅要修改 response的header ，还要修改 response的StatusCode。修改response的StatusCode 可以通过：w.WriteHeader(code) 来实现，例如：

```
w.WriteHeader(404)
```

如果这两种修改一起做，就必须让 w.WriteHeader 在所有的 w.Header.Set 之后，因为 w.WriteHeader 后 Set Header 是无效的。

而且必须是在 w.Write([]byte("HelloWorld")) 之前，否则会报 http: multiple response.WriteHeader calls 因为其实调用w.Write的时候也会调用WriteHeader()方法，然后将w.wroteHeader置为true，再次调WriteHeader()则会判断wroteHeader，如果是true则会报错，而且本次调用不生效。



可以看以下源码说明WriteHeader必须在Write之前调用。

```go
func (w *response) WriteHeader(code int) {
 if w.conn.hijacked() {
   w.conn.server.logf("http: response.WriteHeader on hijacked connection")
   return
 }
//第二次WriteHeader()进来满足if条件就报错直接return
 if w.wroteHeader {
   w.conn.server.logf("http: multiple response.WriteHeader calls")
   return
 }
//第一次write()进来这里会将w.wroteHeader置为true
 w.wroteHeader = true
 w.status = code

 if w.calledHeader && w.cw.header == nil {
   w.cw.header = w.handlerHeader.clone()
 }

 if cl := w.handlerHeader.get("Content-Length"); cl != "" {
   v, err := strconv.ParseInt(cl, 10, 64)
   if err == nil && v >= 0 {
     w.contentLength = v
   } else {
     w.conn.server.logf("http: invalid Content-Length of %q", cl)
     w.handlerHeader.Del("Content-Length")
   }
 }
}
```

**2、 go会对Header中的key进行规范化处理**

go会对Header中的key进行规范化处理，所以在获取response的Header中的K,V值时一定要小心。



reader.go中非导出方法canonicalMIMEHeaderKey中有这样一段，会将header的key进行规范化处理。



1）reader.go中定义了isTokenTable数组，如果key的长度大于127或者包含不在isTokenTable中的字符，则该key不会被处理。

2）将key的首字母大写，字符 - 后的单词的首字母也大写。


分析如下源码，可以解释对key的大写处理：

```go
for i, c := range a {
  // 规范化:首字母大写
  // - 之后单子的首字母大写
  // 如:(Host, User-Agent, If-Modified-Since).
  if upper && 'a' <= c && c <= 'z' {
    //大写转小写
    c -= toLower
  } else if !upper && 'A' <= c && c <= 'Z' {
    //小写转大写
    c += toLower
  }
  //重新给key数组赋值
  a[i] = c
  //设置大小写标志位
  upper = c == '-' // for next time
}
```


正确的调用方式：



服务器：myServer.go

```go
package main

import (
 "net/http"
)

func main() {

 http.HandleFunc("/", func (w http.ResponseWriter, r *http.Request){


   w.Header().Set("name", "my name is smallsoup")
   w.WriteHeader(500)
   w.Write([]byte("hello world\n"))

 })

 http.ListenAndServe(":8080", nil)
}
```

客户端：

myHttp.go：

```go
package main

import (
 "fmt"
 "io/ioutil"
 "net/http"
)

func main() {

 myHttpGet()

}

func myHttpGet() {

 rsp, err := http.Get("http://localhost:8080")
 if err != nil {
   fmt.Println("myHttpGet error is ", err)
   return
 }

 defer rsp.Body.Close()
 body, err := ioutil.ReadAll(rsp.Body)
 if err != nil {
   fmt.Println("myHttpGet error is ", err)
   return
 }

 fmt.Println("response statuscode is ", rsp.StatusCode, 
         "\nhead[name]=", rsp.Header["Name"], 
           "\nbody is ", string(body))
}
```
1.运行服务器



go run myServer.go



2.运行客户端

   

 go run myHttp.go



输出如下：statuscode是我们设置的500，Name也取到了值。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/7ab39226fab9af8628f3ecbf23913ae0.png)

