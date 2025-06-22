---
title: go语言正则表达式
date: '2019-10-18 12:55:32'
updated: '2019-10-18 12:57:45'
tags: [golang, 爬虫]
permalink: /201910181255golang
---
我们前两节课爬取珍爱网的时候，用到了很多正则表达式去匹配城市列表、城市、用户信息，其实除了正则表达式去匹配，还可以利用goquery和xpath第三方库匹配有用信息。而我利用了更优雅的正则表达式匹配。下来大概介绍下正则表达式。

比如我们匹配城市列表的时候，会取匹配所有城市的url，如下：

![image](https://img-blog.csdnimg.cn/20191018003712497.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)


可以看到图片后是小写字母加数字，那么就可以用以下方式提取：

```html
<a href="(http://www.zhenai.com/zhenghun/[0-9a-z] )"[^>]*>([^<] )</a>
```

[0-9a-z] 表示匹配小写字母或者数字至少一次，[^>]*表示匹配非>的字符任意次，然后[^<] 表示匹配非<字符至少一次。我们要取到城市的url和城市名，所以对进行了分组。

通过以下方式就可以拿到url和city

```go
const (
   cityListReg = `<a href="(http://www.zhenai.com/zhenghun/[0-9a-z] )"[^>]*>([^<] )</a>`
 )

 compile := regexp.MustCompile(cityListReg)

 submatch := compile.FindAllSubmatch(contents, -1)

 for _, m := range submatch {
   fmt.Println("url:" , string(m[1]), "city:", string(m[2]))
 }
```

匹配包含g g,且gg中间至少一个小写字母：

```go
//匹配包含g g,且gg中间至少一个小写字母
 match, _ := regexp.MatchString("g([a-z] )g", "11golang11")
 //true
 fmt.Println(match)
```

上面我们直接使用了字符串匹配的正则表达式，但是对于其他的正则匹配任务，需要使用一个优化过的正则对象：

```go
compile, err := regexp.Compile("smallsoup@gmail.com")

 if err != nil {
   //....正则语法错误，需要处理错误
   fmt.Println(err)
 }

 //smallsoup@gmail.com
 fmt.Println(compile.FindString(text))
```

compile, err :=regexp.Compile("smallsoup@gmail.com")

函数返回一个正则表达式匹配器和错误，当参数正则表达式不符合正则语法时返回error，比如说regexp.Compile("[smallsoup@gmail.com")就会报错missing closing ]

一般正则表达式是用户输入的才需要处理错误，而自己写的一般是不会有错的，所以可以使用compile:= regexp.MustCompile("smallsoup@gmail.com")，如果语法错误，就会发生panic。

```go
text1 := `my email is aa@qq.com
  aa email is aa@gmail.com
  bb email is bb@qq.com
  cc email is cc@qq.com.cn
  `
 //如果要提取A@B.C中的A、B、C，需要用到正则表达式的提取功能。
 comp := regexp.MustCompile(`([a-zA-Z0-9] )@([a-zA-Z0-9.] )\.([a-zA-Z0-9] )`)

 //利用自匹配获取正则表达式里括号中的匹配内容
 submatchs := comp.FindAllStringSubmatch(text1, -1)

 //submatchs其实是一个二维数组
 fmt.Println(submatchs)

 //去除每个匹配,submatch其实还是个slice
 for _, submatch := range submatchs {
   fmt.Println(submatch)
 }
```

结果输出如下：

```shell
[[aa@qq.com aa qq com] [aa@gmail.com aa gmail com] [bb@qq.com bb qq com] [cc@qq.com.cn cc qq.com cn]]
[aa@qq.com aa qq com]
[aa@gmail.com aa gmail com]
[bb@qq.com bb qq com]
[cc@qq.com.cn cc qq.com cn]
```

```go
r := regexp.MustCompile("p([a-z] )ch")
 fmt.Println(r) //----->p([a-z] )ch
 //regexp 包也可以用来替换部分字符串为其他值。
 fmt.Println(r.ReplaceAllString("a peach", "<smallsoup>")) //----->a <smallsoup>
 //Func 变量允许传递匹配内容到一个给定的函数中，
 in := []byte("a smallsoup")
 out := r.ReplaceAllFunc(in, bytes.ToUpper)
 fmt.Println(string(out)) //----->a PEACH
 /*#######################常见表达式###########################*/
 // 查找汉字
 testText := "Hello 你好吗, I like golang!"
 reg := regexp.MustCompile(`[\p{Han}] `)
 fmt.Println(reg.FindAllString(testText, -1)) // ----->[你好]
 reg = regexp.MustCompile(`[\P{Han}] `)
 fmt.Println(reg.FindAllString(testText, -1))        // ----->["Hello " ", I li golang!"]
 fmt.Printf("%q\n", reg.FindAllString(testText, -1)) // ----->["Hello " ", I lm golang!"]
 //Email
 reg = regexp.MustCompile(`\w ([- .]\w )*@\w ([-.]\w )*\.\w ([-.]\w )*`)
 fmt.Println(reg.MatchString("smallsoup@qq.com"))
 //用户名密码：
 reg = regexp.MustCompile(`[a-zA-Z]|\w{6,18}`)
 fmt.Println(reg.MatchString("w_dy_246"))
```

运行结果如下：

```go
p([a-z] )ch
a <smallsoup>
a smallsoup
[你好吗]
[Hello  , I like golang!]
["Hello " ", I like golang!"]
true
true

Process finished with exit code 0

```

