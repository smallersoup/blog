---
title: java发邮件，这个坑你能填吗？
date: '2019-10-17 17:53:49'
updated: '2019-10-17 17:53:49'
tags: [email, java]
permalink: /201910171753java
---
![](https://img.hacpai.com/bing/20190601.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

今天利用java发邮件，本地windows上测试时发送ok的，部署到服务器上却报异常，让我们走进异常，探索到底坑在哪里，并填之。



利用outlook发邮件代码如下：

```java

package com.website.service.impl;

import com.alibaba.fastjson.JSON;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.mail.javamail.MimeMessageHelper;

import javax.mail.internet.MimeMessage;
import java.util.Properties;

/**
* @program: WebSite
* @description: SpringMvc实现的发送email
* @author: smallsoup
* @create: 2018-06-30 20:29
**/
public class EmailServiceImpl {

   private static final Logger LOGGER = LoggerFactory.getLogger(Test.class);

   @Autowired
   @Qualifier("javaMailSender")
   private JavaMailSenderImpl sender;

   /**
    * @方法名: sendMail
    * @参数名：@param subject  邮件主题
    * @参数名：@param content 邮件内容
    * @参数名：@param to     收件人Email地址
    * @描述语: 发送邮件
    */
   public void sendMailHtml(String to, String subject, String content) throws Exception {

       sender.setUsername("yourusername@outlook.com");
       sender.setPassword("your_password");
       sender.setPort(587);

       Properties props = new Properties();
       props.setProperty("mail.transport.protocol", "smtp");
       props.setProperty("mail.smtp.host", "smtp-mail.outlook.com");
       props.setProperty("mail.smtp.starttls.enable", "true");
       props.setProperty("mail.smtp.auth", "true");
       props.setProperty("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
       props.setProperty("mail.smtp.socketFactory.port", "587");
       props.setProperty("mail.smtp.socketFactory.fallback", "true");
       props.setProperty("mail.smtp.auth.ntlm.domain", "THING");

       sender.setJavaMailProperties(props);

       //建立邮件消息,发送简单邮件和html邮件的区别
       MimeMessage mailMessage = sender.createMimeMessage();
       MimeMessageHelper messageHelper = new MimeMessageHelper(mailMessage);

       messageHelper.setFrom("smallsoup@outlook.com");

       //用于接收邮件的邮箱
       messageHelper.setTo(to);
       //邮件的主题
       messageHelper.setSubject(subject);
       //邮件的正文，第二个boolean类型的参数代表html格式
       messageHelper.setText(content, true);

       LOGGER.info("----------sendMailHtml-----------------");
       LOGGER.info("----------mailMessage is------------FROM:{}, Subject:{}, content:{}, AllRecipients:{}", mailMessage.getFrom(), mailMessage.getSubject(), mailMessage.getContent(), JSON.toJSONString(mailMessage.getAllRecipients()));
       //发送
       sender.send(mailMessage);
   }
}
```

上面的代码打包在本地tomcat上运行，可以发送邮件成功。但是将war包部署到亚马逊云服务器上发送邮件报错：

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWE1NGMwYzM2NWE0YTk0YzkucG5n?x-oss-process=image/format,png)

网上说是由于用户名和密码不正确导致验证失败。但是这不能解释本地能发出去邮件的事实。继续排查、google，实在找不到解决办法。那就试着登陆下outlook邮件看能不能登进去，登陆正常，有一封最近的一次登录存在某些异常的邮件。
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTBmMGVhYWUxZWMzYjllNzgucG5n?x-oss-process=image/format,png)  



然后点击查看最新活动状态。异常显示最近一次登陆在美国。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTVjNDQ5NDA3MmIzZDM4NjMucG5n?x-oss-process=image/format,png)


这么一来就知道问题了，由于亚马逊云实际位置在美国，所以发邮件时相当于在异地登陆被拒绝。当点击了“是我本人”之后，重新发邮件，就发出去了。

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTcwZGIwMGI0ODdiNzYxYjIucG5n?x-oss-process=image/format,png)

之所以不用163发邮件，是因为本地部署也可以发出去，放到服务器上也发不出，报554 DT:SPM 163 smtp3，网上说是因为邮件主题和正文中又非法字符导致，目前还没解决，之后再填此坑。

