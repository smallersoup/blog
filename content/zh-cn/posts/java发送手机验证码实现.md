---
title: java发送手机验证码实现
date: '2019-10-17 18:01:34'
updated: '2019-10-17 18:01:34'
tags: [java, 短信]
permalink: /201910171801java
---
![](https://img.hacpai.com/bing/20180526.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文
今天来用java实现手机验证码的发送。



短信平台有很多，中国网建提供的SMS短信通，注册免费5条短信，3条彩信，

http://sms.webchinese.cn/



但是刚才试了，第一次用官方提供的demo发送成功，然后整合到自己项目中，调试时由于参数配置错误导致发送了几次失败后，5次就用完了。按理说成功才能算一次，果断放弃。



然后试了一下腾讯云SMS平台，每月可以免费发送100条国内短信

https://cloud.tencent.com/product/sms

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZTQyZWI1YmIwMDY1MjYxZg?x-oss-process=image/format,png)

首先需要注册腾讯云账号，注册时可以微信认证，认证时支付1分钱验证是人为操作，这一分钱注册成功后会放到账户中。

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMDU4NjM5YzEwMjFmYTI3NQ?x-oss-process=image/format,png)

注册后，需要添加一个应用，这个随便写，创建好后点击 -> 应用名称，然看AppID和AppKey，这个比较重要，调用短信API接口时需要提供。

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtYmM5OGY4NjZiOTAyNzYzMw?x-oss-process=image/format,png)

然后需要在 -> 国内短信 -> 短信内容配置 -> 短信签名中创建签名和短信正文中创建正文模板。

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZGY5ODdlZWY0YzZmZTA0NA?x-oss-process=image/format,png)

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZjgxNTBiZGE4YzczZDkyNQ?x-oss-process=image/format,png)

一个完整的短信由短信签名和短信正文内容两部分组成，您可以根据业务需求分别设置不同的短信正文内容模板，然后进行组合形成最终展示。短信签名+短信正文内容=最终显示内容

审核可能得需要花一段时间，我创建后，审核只花了2小时不到。这些步骤做完之后，就可以根据官方提供的API接口发送短信了。

***https://cloud.tencent.com/document/product/382/5808***

官方提供了java、python、c#、node.js的SDK，这里用java的SDK调用，这里有详细说明：

***https://github.com/qcloudsms/qcloudsms_java***

首先加入maven依赖：

```xml
<dependency>
     <groupId>com.github.qcloudsms</groupId>
     <artifactId>qcloudsms</artifactId>
     <version>1.0.4</version>
</dependency>
```

编写调用SDK的代码：

```java
/**
    * 腾讯云短信,100条一个月
    * 方法说明
    *
    * @param phone
    * @return void
    * @Discription:扩展说明
    * @throws HTTPException  http status exception
    * @throws IOException    network problem
    */
   public static void sendMsgByTxPlatform(String phone) throws Exception {

       // 短信应用SDK AppID
       // 1400开头
       int appId = 1402126548;

       // 短信应用SDK AppKey
       String appKey = "b67d0bf7876c1d42121ca561953532";

       // 需要发送短信的手机号码
   // String[] phoneNumbers = {"15212111830"};

       // 短信模板ID，需要在短信应用中申请
       //NOTE: 这里的模板ID`7839`只是一个示例，真实的模板ID需要在短信控制台中申请
       int templateId = 148464;

       // 签名
       // NOTE: 这里的签名"腾讯云"只是一个示例，真实的签名需要在短信控制台中申请，另外签名参数使用的是`签名内容`，而不是`签名ID`
       String smsSign = "我的小碗汤";

       SmsSingleSender sSender = new SmsSingleSender(appId, appKey);
       //第一个参数0表示普通短信,1表示营销短信
       SmsSingleSenderResult result = sSender.send(0, "86",
               phone,
               RandomCodeUtils.getSixValidationCode() + "为您的登录验证码，请于" + 10 + "分钟内填写。如非本人操作，请忽略本短信。", "", "");

       if (result.result != 0) {
           throw new Exception("send phone validateCode is error" + result.errMsg);
       }
   }
```

参数说明：

```java
@param type 短信类型，0 为普通短信，1 营销短信,需要和刚才页面上提交的短信正文下的类型一致
@param nationCode 国家码，如 86 为中国
@param phoneNumber 不带国家码的手机号
@param msg 信息内容，必须与申请的模板格式一致，否则将返回错误，{1}占位符可在代码中用实际需要发送的值替换
@param extend 扩展码，可填空
@param ext 服务端原样返回的参数，可填空
```

编写好以后用测试类测试时，返回错误码1014，可以点击错误描述中的链接去查看可能的原因。我是由于正文内容和刚才页面上提交的正文不一样导致的。

https://cloud.tencent.com/document/product/382/3771

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZDhlNzhkOTQyMzY3MmQyNw?x-oss-process=image/format,png)

以下有很多错误码，可以供排查问题参考：

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNzBiZDUzNzAxZjRkNTZiMQ?x-oss-process=image/format,png)

正常情况下，返回的result为0时表示发送成功，这也是100条次数减1的参考。按照接口要求修改参数后，发送短信成功。

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtOGJkY2Q1YWM1MTBjMDYwNA?x-oss-process=image/format,png)

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtYmIyY2JkYmFhZDIxZDA4MA?x-oss-process=image/format,png)

也有很多其他平台提供的短信服务，比如阿里云可以参考以下文章：

***https://blog.csdn.net/u014520797/article/details/54411392***
