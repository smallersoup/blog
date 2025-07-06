---
title: 浅谈json web token及应用
date: '2019-10-18 13:02:25'
updated: '2019-10-18 13:02:25'
tags: [golang, jwt]
permalink: /201910181302jwt
---
> Json Web Token (JWT)，是一个非常轻巧的规范，这个规范允许在网络应用环境间客户端和服务器间较安全的传递信息。该token被设计为紧凑且安全的，特别适用于分布式站点的单点登录（SSO）场景。JWT一般被用来在身份提供者和服务提供者间传递被认证的用户身份信息，以便于从资源服务器获取资源。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018004607695.gif)

在web应用中，我们提供的API接口，通过GET或者POST方式调用，在调用过程中，就存在着接口认证及数据的安全性问题。例如如下问题：

1、请求来自哪里，身份是否合法？

2、请求参数是否被篡改？

3、客户端请求的唯一性，是否为重复请求攻击（RepeatAttack）？

## 传统的Session认证方式

在传统的web应用中，服务端成功相应请求者，返回正常的response依赖于服务端通过一种存储机制把每个用户经过认证之后的会话信息（session）记录服务器端，一般记录到内存、磁盘、数据库中，这种方式在请求量和用户量增多的时候无疑会增大服务端的开销；如果是记录在内存中，那每次请求都分发登到该机器上才能授权获取资源，那在分布式系统中就存在着问题；因为是基于Cookie的，如果Cookie被截获，攻击者会盗用身份信息进行发送恶意请求，也就是“跨站请求伪造”（CSRF）。

## 基于token的认证方式

客户端用用户名和密码经过服务器认证之后，服务器会签发一个token返回给客户端，客户端存储token（一般存在请求头里），并且在之后的请求里附带此token，服务器每次会解签名token，验证通过则返回资源。另外服务端要支持CORS跨来源资源共享）策略，服务器处理完请求之后，会再返回结果中加上Access-Control-Allow-Origin。

## jwt的生成

token是接口的令牌，好比去衙门办事，“衙门口朝南开，有理无钱莫进来”。没有令牌就别想办事。token的验证方法很多，也生成了很多标准，jwt就是一种基于json的RFC 7519。该标准由三部分组成：

*   header

*   payload

*   signature

header和payload经过base64编码后用点拼接起来。signature是把header和payload编码和拼接后经过加密算法加密，加密时还要一个密码，这个密码保存在服务器端。大致示意图如下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018004607894.png)

**Header：**

head由两部分组成，一个是token类型，一个是使用的算法，如下类型为jwt，使用的算法是HS256。当然，还有HS384、HS512算法。

```
{
 "typ": "JWT",
 "alg": "HS256"
}
```

将以上json进行base64编码，当然编码前将json去格式化，如图：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/2019101800460836.png)

生成的编码为：

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9
```

用go语言实现：

```
package main

import (
 "fmt"
 "encoding/base64"
)

func main() {

 head1 := `{"typ":"JWT","alg":"HS256"}`

 fmt.Println(base64.StdEncoding.EncodeToString([]byte(head1)))
}
```

**Payload：**

payload 里面是 token 的具体内容，这些内容里面有一些是标准字段，我们也可以添加自定义内容。如下：

```
{
   "iss": "smallsoup",
   "iat": 1528902195,
   "exp": 1528988638,
   "aud": "www.smallsoup.com",
   "sub": "smallsoup@qq.com",
   "userId": "0418"
}
```

这里面的前五个字段都是由JWT的标准所定义的，在jwt标准中都可以找到。

*   iss: 该JWT的签发者

*   sub: 该JWT所面向的用户

*   aud: 接收该JWT的一方

*   exp(expires): 什么时候过期，这里是一个Unix时间戳

*   iat(issued at): 在什么时候签发的

最后一个userId表示了用户信息，为自定义字段，我们也可以定义角色等其他字段。以上的json去格式化后的base64编码如下：

```
eyJpc3MiOiJzbWFsbHNvdXAiLCJpYXQiOjE1Mjg5MDIxOTUsImV4cCI6MTUyODk4ODYzOCwiYXVkIjoid3d3LnNtYWxsc291cC5jb20iLCJzdWIiOiJzbWFsbHNvdXBAcXEuY29tIiwidXNlcklkIjoiMDQxOCJ9
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018004608288.png)

**Signature：**

JWT 的最后一部分是 Signature ，这部分内容有三个部分，先是用 Base64 编码的 header.payload ，再用加密算法加密一下，加密的时候要放进去一个 Secret ，这个相当于是一个密码，这个密码秘密地存储在服务端。

*   header

*   payload

*   secret

假设这里secret为mysecret，则用go语言实现代码如下：

```go
package main

import (
 "fmt"
 "encoding/base64"
 "crypto/hmac"
 "crypto/sha256"
 "strings"
)

func main() {

 head1 := `{"typ":"JWT","alg":"HS256"}`

 head1Base64 := base64.StdEncoding.EncodeToString([]byte(head1))

 payload1 := `{"iss":"smallsoup","iat":1528902195,"exp":1528988638,"aud":"www.smallsoup.com","sub":"smallsoup@qq.com","userId":"0418"}`

 payload1Base64 := base64.StdEncoding.EncodeToString([]byte(payload1))

 encodedstring := head1Base64   "."   payload1Base64

 hash := hmac.New(sha256.New, []byte("mysecret"))
 hash.Write([]byte(encodedstring))

 signature := strings.TrimRight(base64.URLEncoding.EncodeToString(hash.Sum(nil)), "=")

 fmt.Printf(signature)
}
```

运行结果为：

```
fjjbA93FTcE71hz_cyIzCUFYdTdyl9hA0w7Pa0ltduc
```

最后这个在服务端生成并且要发送给客户端的 Token 看起来像这样：

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzbWFsbHNvdXAiLCJpYXQiOjE1Mjg5MDIxOTUsImV4cCI6MTUyODk4ODYzOCwiYXVkIjoid3d3LnNtYWxsc291cC5jb20iLCJzdWIiOiJzbWFsbHNvdXBAcXEuY29tIiwidXNlcklkIjoiMDQxOCJ9.fjjbA93FTcE71hz_cyIzCUFYdTdyl9hA0w7Pa0ltduc
```

实际上https://jwt.io/这个网站提供了这个能力，以及各种语言的生成token和解密token的库。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018004608695.jpeg)

go语言生成token和解析token：

下面是go语言版的生成token和解析token的案例：

```go
package main

import (
 "github.com/dgrijalva/jwt-go"
 "fmt"
)

func main() {

 hmacSampleSecret := []byte("mysecret")

 // Create a new token object, specifying signing method and the claims
 // you would like it to contain.
 token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
     "iss": "smallsoup",
     "iat": 1528902195,
     "exp": 1528988638,
     "aud": "www.smallsoup.com",
     "sub": "smallsoup@qq.com",
     "userId": "0418",
 })

 // Sign and get the complete encoded token as a string using the secret
 tokenString, err := token.SignedString(hmacSampleSecret)

 fmt.Println(tokenString, err)

 token, err = jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
   // Don't forget to validate the alg is what you expect:
   if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
     return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
   }

   // hmacSampleSecret is a []byte containing your secret, e.g. []byte("my_secret_key")
   return hmacSampleSecret, nil
 })

 if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
   fmt.Println(claims)
 } else {
   fmt.Println(err)
 }
}
```

具体可以了解github上以下代码的实现。

```shell
go get github.com/dgrijalva/jwt-go
```

------------

