title: 用go语言爬取珍爱网 | 第二回
date: '2019-10-18 10:23:11'
updated: '2019-10-18 10:23:11'
tags: [golang, 爬虫]
permalink: /201910181023golang
---
![image](https://img-blog.csdnimg.cn/20191018002356226.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


![image](https://img-blog.csdnimg.cn/20191018002355495.gif)


昨天我们一起爬取珍爱网首页，拿到了城市列表页面，接下来在返回体城市列表中提取城市和url，即下图中的a标签里的href的值和innerText值。

![image](https://img-blog.csdnimg.cn/20191018002403470.gif)


提取a标签，可以通过CSS选择器来选择，如下：

$('#cityList>dd>a');就可以获取到470个a标签：

![image](https://img-blog.csdnimg.cn/20191018002405127.gif)


这里只提供一个思路，go语言标准库里没有CSS解析库，通过第三方库可以实现。具体可以参考文章：

https://my.oschina.net/2xixi/blog/488811

http://liyangliang.me/posts/2016/03/zhihu-go-insight-parsing-html-with-goquery/

这两篇文章都是用goquery解析 HTML，用到了库：

https://github.com/PuerkitoBio/goquery

也可以用xpath去解析html，可以参考：

https://github.com/antchfx/xquery

xpath和goquery相比还是比较麻烦的，通过以下这张图可以看出来goquery要活跃的多：

![image](https://img-blog.csdnimg.cn/20191018002405351.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


我们这里不用xpath，也不用goquery提取，用更加通用的正则表达式来提取。

![image](https://img-blog.csdnimg.cn/2019101800240944.gif)


从上图可以看出，返回体中的a标签里都是这种形式，XXX表示城市拼音，XX表示城市中文，其他的都一样。

```
<a href="http://www.zhenai.com/zhenghun/XXX"
                      class="">XX</a>
```

所以可以写出以下的正则表达式来匹配：

```
compile := regexp.MustCompile(`<a href="http://www.zhenai.com/zhenghun/[0-9a-z] "[^>]*>[^<] </a>`)
```

正则表达式说明：

```
1、href的值都类似http://www.zhenai.com/zhenghun/XX
2、XX可以是数字和小写字母,所以[0-9a-z], 表示至少有一个
3、[^>]*表示匹配不是>的其他字符任意次
4、[^<] 表示匹配不是<的其他字符至少一次
```

然后利用分组获取url和城市，代码如下：

```
func printAllCityInfo(body []byte){

 //href的值都类似http://www.zhenai.com/zhenghun/XX
 //XX可以是数字和小写字母,所以[0-9a-z], 表示至少有一个
 //[^>]*表示匹配不是>的其他字符任意次
 //[^<] 表示匹配不是<的其他字符至少一次
 compile := regexp.MustCompile(`<a href="(http://www.zhenai.com/zhenghun/[0-9a-z] )"[^>]*>([^<] )</a>`)

 submatch := compile.FindAllSubmatch(body, -1)

 for _, matches := range submatch {
   //打印
   fmt.Printf("City:%s URL:%s\n", matches[2], matches[1])
 }

 //可以看到匹配个数为470个
 fmt.Printf("Matches count: %d\n", len(submatch))
}
```

那么提取URL和City的完整代码如下：

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
 "regexp"
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

 printAllCityInfo(body)
 //打印返回值
 //fmt.Println("body is ", string(body))
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

func printAllCityInfo(body []byte){

 //href的值都类似http://www.zhenai.com/zhenghun/XX
 //XX可以是数字和小写字母,所以[0-9a-z], 表示至少有一个
 //[^>]*表示匹配不是>的其他字符任意次
 //[^<] 表示匹配不是<的其他字符至少一次
 compile := regexp.MustCompile(`<a href="(http://www.zhenai.com/zhenghun/[0-9a-z] )"[^>]*>([^<] )</a>`)

 /*matches := compile.FindAll(body, -1)

 //matches是二维数组[][]byte
 for _, m := range matches {
   fmt.Printf("%s\n", m)
 }
 */

 submatch := compile.FindAllSubmatch(body, -1)

 //submatch是三维数组[][][]byte
/*  for _, matches := range submatch {

   //[][]byte
   for _, m := range matches {
     fmt.Printf("%s ", m)
   }

   fmt.Println()
 }*/

 for _, matches := range submatch {

   //打印
   fmt.Printf("City:%s URL:%s\n", matches[2], matches[1])

 }

 //可以看到匹配个数为470个
 fmt.Printf("Matches count: %d\n", len(submatch))

 //打印abc
 //fmt.Printf("%s\n", []byte{97,98,99})
}
```

运行后，可以看到输出了URL和City：

![image](https://img-blog.csdnimg.cn/2019101800241098.gif)


今天我们完成了URL和城市的提取，明天我们将利用URL，来进一步分析城市的男女性个人信息。

------------
