---
title: 用go语言爬取珍爱网 | 第一回
date: '2019-10-18 10:24:14'
updated: '2019-10-18 10:24:14'
tags: [golang, 爬虫]
permalink: /2019101623181024golang
---
![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/csdnimg/20191018002129589.jpeg)

我们来用go语言爬取“珍爱网”用户信息。

首先分析到请求url为：

http://www.zhenai.com/zhenghun

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/csdnimg/20191018002129914.jpeg)

接下来用go请求该url，代码如下：

```
package main

import (
 "fmt"
 "io/ioutil"
 "net/http"
)

func main() {

 //返送请求获取返回结果
 resp, err := http.Get("http://www.zhenai.com/zhenghun")

 if err != nil {
   panic(fmt.Errorf("Error: http Get, err is %v\n", err))
 }

 //关闭response body
 defer resp.Body.Close()

 if resp.StatusCode != http.StatusOK {
   fmt.Println("Error: statuscode is ", resp.StatusCode)
   return
 }

 body, err := ioutil.ReadAll(resp.Body)

 if err != nil {
   fmt.Println("Error read body, error is ", err)
 }

 //打印返回值
 fmt.Println("body is ", string(body))
}
```

运行后会发现返回体里有很多乱码：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/csdnimg/20191018002130138.jpeg)

在返回体里可以找到<meta charset="gbk" /> 即编码为gbk，而go默认编码为utf-8，所以就会出现乱码。接下来用第三方库将其编码格式转为utf-8。

由于访问golang.org/x/text需要梯子，不然报错：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/csdnimg/20191018002130356.jpeg)

所以在github上下载：

```
mkdir -p $GOPATH/src/golang.org/x
cd $GOPATH/src/golang.org/x
git clone https://github.com/golang/text.git
```

然后将gbk编码转换为utf-8，需要修改代码如下：

```
utf8Reader := transform.NewReader(resp.Body, simplifiedchinese.GBK.NewDecoder())
body, err := ioutil.ReadAll(utf8Reader)
```

考虑到通用性，返回的编码格式不一定是gbk，所以需要对实际编码做判断，然后将判断结果转为utf-8，需要用到第三方库golang.org/x/net/html，同样的在github上下载：

```
mkdir -p $GOPATH/src/golang.org/x
cd $GOPATH/src/golang.org/x
git clone https://github.com/golang/net
```

那么代码就变成这样：

```
package main

import (
 "fmt"
 "io/ioutil"
 "net/http"
 "golang.org/x/text/transform"
 //"golang.org/x/text/encoding/simplifiedchinese"
 "io"
 "golang.org/x/text/encoding"
 "bufio"
 "golang.org/x/net/html/charset"
)

func main() {

 //返送请求获取返回结果
 resp, err := http.Get("http://www.zhenai.com/zhenghun")

 if err != nil {
   panic(fmt.Errorf("Error: http Get, err is %v\n", err))
 }

 //关闭response body
 defer resp.Body.Close()

 if resp.StatusCode != http.StatusOK {
   fmt.Println("Error: statuscode is ", resp.StatusCode)
   return
 }

 //utf8Reader := transform.NewReader(resp.Body, simplifiedchinese.GBK.NewDecoder())
 utf8Reader := transform.NewReader(resp.Body, determinEncoding(resp.Body).NewDecoder())
 body, err := ioutil.ReadAll(utf8Reader)

 if err != nil {
   fmt.Println("Error read body, error is ", err)
 }

 //打印返回值
 fmt.Println("body is ", string(body))
}

func determinEncoding(r io.Reader) encoding.Encoding {

 //这里的r读取完得保证resp.Body还可读
 body, err := bufio.NewReader(r).Peek(1024)

 if err != nil {
   fmt.Println("Error: peek 1024 byte of body err is ", err)
 }

 //这里简化,不取是否确认
 e, _, _ := charset.DetermineEncoding(body, "")
 return e
}
```

运行后就看不到乱码了：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/csdnimg/20191018002130554.jpeg)

今天先爬到这里，明天将提取返回体中的地址URL和城市，下一节见。

------------

