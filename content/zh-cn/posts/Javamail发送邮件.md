---
title: Javamail发送邮件
date: '2019-10-18 13:27:45'
updated: '2019-10-18 13:27:45'
tags: [java, email]
permalink: /201910181327java
---

## 正文

这几篇文章写的就挺好了，传送过去看看吧：

1、 [使用JavaMail创建邮件和发送邮件](https://www.cnblogs.com/xdp-gacl/p/4216311.html)

可能遇到的问题：
1、因为端口号问题导致的错误：
```sh
javax.mail.MessagingException: Exception reading response;
  nested exception is:
        java.net.SocketTimeoutException: Read timed out
javax.mail.MessagingException: Exception reading response;
  nested exception is:
        java.net.SocketTimeoutException: Read timed out
        at com.sun.mail.smtp.SMTPTransport.readServerResponse(SMTPTransport.java:2210)
        at com.sun.mail.smtp.SMTPTransport.openServer(SMTPTransport.java:1950)
        at com.sun.mail.smtp.SMTPTransport.protocolConnect(SMTPTransport.java:642)
        at javax.mail.Service.connect(Service.java:317)
        at javax.mail.Service.connect(Service.java:176)
        at javax.mail.Service.connect(Service.java:125)
        at javax.mail.Transport.send0(Transport.java:194)
        at javax.mail.Transport.send(Transport.java:124)
```
问题和解决这里可以看到，把port configuration from 465 to 587(把端口从465改成587)
https://stackoverflow.com/questions/31535863/error-when-sending-email-via-java-mail-api

2、[使用javamail发送内嵌图片的html格式邮件](http://outofmemory.cn/code-snippet/1194/usage-javamail-send-neiqian-tupian-html-format-email)

要在邮件中包含图片简单办法是使用image标签，src指向服务器上图片的位置。
```java
 package com.example.emaildemo;

import javax.mail.Message;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import java.util.Properties;

/**
 * @program: email-demo
 * @description:
 * @author: smallsoup
 * @create: 2019-01-27 16:44
 **/

public class SendEmailUtil {
    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.setProperty("mail.transport.protocol", "smtp");
        props.setProperty("mail.host", "smtp.exmail.qq.com");
        props.setProperty("mail.smtp.auth", "true");

        //使用JavaMail发送邮件的5个步骤
        //1、创建session
        Session mailSession = Session.getInstance(props);
        //开启Session的debug模式，这样就可以查看到程序发送Email的运行状态
        mailSession.setDebug(true);
        //2、通过session得到transport对象
        Transport transport = mailSession.getTransport();

        //3、使用邮箱的用户名和密码连上邮件服务器,这里有多个构造器,可传入host、端口、user、password
        transport.connect( "你的邮箱地址", "你的邮箱AUTH密码,不是登陆密码哦,在邮箱的设置里单独开启和设置");

        MimeMessage message = new MimeMessage(mailSession);
        message.setSubject("HTML mail Hello");
        message.setFrom(new InternetAddress("你的邮箱地址"));
        //4、创建邮件
        message.setContent("<h1>This is a test</h1>" + "<img src=\"http://www.rgagnon.com/images/jht.gif\">",
                "text/html");
        message.addRecipient(Message.RecipientType.TO, new InternetAddress("接收人邮箱地址"));

        //5、发送邮件
//        transport.sendMessage(message, message.getRecipients(Message.RecipientType.TO));
        transport.sendMessage(message, message.getAllRecipients());
        transport.close();
    }
}
```
上面发送带图片邮件的方法很简单，但是有些邮件客户端会把是否包含有服务器端图片作为垃圾邮件的判断机制。我们可以将图片内嵌到邮件中，然后用cid加content-id引用内嵌的图片。
```java
package com.example.emaildemo;

import javax.activation.DataHandler;
import javax.activation.DataSource;
import javax.activation.FileDataSource;
import javax.mail.BodyPart;
import javax.mail.Message;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeBodyPart;
import javax.mail.internet.MimeMessage;
import javax.mail.internet.MimeMultipart;
import java.util.Properties;

/**
 * @program: email-demo
 * @description:
 * @author: smallsoup
 * @create: 2019-01-27 16:44
 **/

public class SendEmailUtil {
    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.setProperty("mail.transport.protocol", "smtp");
        props.setProperty("mail.host", "smtp.exmail.qq.com");
        props.setProperty("mail.smtp.auth", "true");

        //使用JavaMail发送邮件的5个步骤
        //1、创建session
        Session mailSession = Session.getInstance(props);
        //开启Session的debug模式，这样就可以查看到程序发送Email的运行状态
        mailSession.setDebug(true);
        //2、通过session得到transport对象
        Transport transport = mailSession.getTransport();

        //3、使用邮箱的用户名和密码连上邮件服务器,这里有多个构造器,可传入host、端口、user、password
        transport.connect( "你的邮箱地址", "你的邮箱AUTH密码,不是登陆密码哦,在邮箱的设置里单独开启和设置");

        MimeMessage message = new MimeMessage(mailSession);
        message.setSubject("HTML mail Hello");
        message.setFrom(new InternetAddress("你的邮箱地址"));
        message.addRecipient(Message.RecipientType.TO, new InternetAddress("接收人邮箱地址"));

        //4、创建邮件
        //This HTML mail have to 2 part, the BODY and the embedded image
        MimeMultipart multipart = new MimeMultipart("related");

        // first part  (the html)
        BodyPart messageBodyPart = new MimeBodyPart();
        String htmlText = "<H1>Hello</H1><img src=\"cid:image\">";
        messageBodyPart.setContent(htmlText, "text/html");

        // add it
        multipart.addBodyPart(messageBodyPart);

        // second part (the image)
        messageBodyPart = new MimeBodyPart();
        DataSource fds = new FileDataSource("C:\\images\\jht.gif");
        messageBodyPart.setDataHandler(new DataHandler(fds));
        messageBodyPart.setHeader("Content-ID","image");

        // add it
        multipart.addBodyPart(messageBodyPart);

        // put everything together
        message.setContent(multipart);
        //5、发送邮件
        transport.sendMessage(message, message.getAllRecipients());
        transport.close();
    }
}
```
SpringBoot发送邮件需要加依赖：
```xml
  <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-mail</artifactId>
  </dependency>
```
具体可参考：
[java发送html模板的高逼格邮件](https://www.jianshu.com/p/0e2dc4662f00)






---------
