title: java发送html模板的高逼格邮件
date: '2019-10-18 13:26:26'
updated: '2019-10-18 13:26:26'
tags: [java, email]
permalink: /201910181325java
---

## 正文


最近做了一个监测k8s服务pod水平伸缩发送邮件的功能（当pod的cpu/内存达到指定阈值后会水平扩展出多个pod、或者指定时间内pod数应扩展到指定数量），一开始写了个格式很low的邮件，像下面这样：
![简单邮件](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWNmY2JjMzM4MDBiMGExY2EucG5n?x-oss-process=image/format,png)

主流程打通，算个v1版本吧，程序员是个追求完美的人，再说这么低逼格的邮件，给客户看，客户也会不满意。那怎么提高邮件的逼格呢？下面写了个简单的demo，v2版本如下：
![带模板邮件](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTg5YmZkZTMyYTY5NWRjY2YucG5n?x-oss-process=image/format,png)

感兴趣的小伙伴可以参考，模板可以找你公司前端和美工小姐姐设计。

因为监测k8s服务pod水平伸缩是用go开发的，发送通知邮件提供了个接口，用springboot写的，以下也用springboot做demo

Springboot的pom.xml文件：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.1.2.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>email-demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>email-demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>1.8</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.8.1</version>
        </dependency>
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>fastjson</artifactId>
            <version>1.2.47</version>
        </dependency>
       <!--发送邮件的必要依赖-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-mail</artifactId>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```


pod-scale-alarm.html模板文件：
模板中的{0}、{1}这样的占位符后面java代码会替换掉
```html
<body style="color: #666; font-size: 14px; font-family: 'Open Sans',Helvetica,Arial,sans-serif;">
<div class="box-content" style="width: 80%; margin: 20px auto; max-width: 800px; min-width: 600px;">
    <div class="header-tip" style="font-size: 12px;
                                   color: #aaa;
                                   text-align: right;
                                   padding-right: 25px;
                                   padding-bottom: 10px;">
        Confidential - Scale Alarm Use Only
    </div>
    <div class="info-top" style="padding: 15px 25px;
                                 border-top-left-radius: 10px;
                                 border-top-right-radius: 10px;
                                 background: {0};
                                 color: #fff;
                                 overflow: hidden;
                                 line-height: 32px;">
        <img src="cid:icon-alarm" style="float: left; margin: 0 10px 0 0; width: 32px;" /><div style="color:#010e07"><strong>服务实例水平伸缩通知</strong></div>
    </div>
    <div class="info-wrap" style="border-bottom-left-radius: 10px;
                                  border-bottom-right-radius: 10px;
                                  border:1px solid #ddd;
                                  overflow: hidden;
                                  padding: 15px 15px 20px;">
        <div class="tips" style="padding:15px;">
            <p style=" list-style: 160%; margin: 10px 0;">Hi,</p>
            <p style=" list-style: 160%; margin: 10px 0;">{1}</p>
        </div>
        <div class="time" style="text-align: right; color: #999; padding: 0 15px 15px;">{2}</div>
        <br>
        <table class="list" style="width: 100%; border-collapse: collapse; border-top:1px solid #eee; font-size:12px;">
            <thead>
            <tr style=" background: #fafafa; color: #333; border-bottom: 1px solid #eee;">
                {3}
            </tr>
            </thead>
            <tbody>
            {4}
            </tbody>
        </table>
    </div>
</div>
</body>
```
success-alarm.png图标：
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTA2MWY4NjBmYWRkMWQ5YTUucG5n?x-oss-process=image/format,png)

java代码如下，简单的demo，优化可以自己在项目中去做。
```java
package com.example.emaildemo;

import org.apache.commons.lang3.time.DateFormatUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.mail.javamail.JavaMailSenderImpl;
import org.springframework.mail.javamail.MimeMessageHelper;

import javax.mail.MessagingException;
import javax.mail.internet.MimeMessage;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.MessageFormat;
import java.util.Date;
import java.util.Objects;
import java.util.Properties;

/**
 * @program: email-demo
 * @description:
 * @author: smallsoup
 * @create: 2019-01-27 16:44
 **/

public class SendEmailUtil {

    private static final Logger LOGGER = LoggerFactory.getLogger(SendEmailUtil.class);

    public static void main(String[] args) throws MessagingException, IOException {

        JavaMailSenderImpl javaMailSender = new JavaMailSenderImpl();
        javaMailSender.setUsername("你的邮箱地址");
        javaMailSender.setPassword("你的邮箱AUTH密码,不是登陆密码哦,在邮箱的设置里单独开启和设置");
        javaMailSender.setHost("smtp.exmail.qq.com");
        javaMailSender.setPort(587);
        javaMailSender.setDefaultEncoding("UTF-8");
        Properties props = new Properties();
        props.setProperty("mail.smtp.host", "smtp.exmail.qq.com");
        props.setProperty("mail.transport.protocol", "smtp");
        props.setProperty("mail.smtp.auth", "true");
        props.setProperty("mail.smtp.connectiontimeout", "20000");
        props.setProperty("mail.smtp.timeout", "20000");
        javaMailSender.setJavaMailProperties(props);

        MimeMessage message = javaMailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
        helper.setTo(new String[]{"收件人邮箱"});
        helper.setCc("抄送人邮箱");
        helper.setFrom("你的邮箱地址");
        helper.setSubject("liang subject");
        helper.setText(buildContent(), true);


        String alarmIconName = "success-alarm.png";
        ClassPathResource img = new ClassPathResource(alarmIconName);
        if (Objects.nonNull(img)) {
            helper.addInline("icon-alarm", img);
        }
        javaMailSender.send(message);
    }

    private static String buildContent() throws IOException {

        //加载邮件html模板
        String fileName = "pod-scale-alarm.html";
        InputStream inputStream = ClassLoader.getSystemResourceAsStream(fileName);
        BufferedReader fileReader = new BufferedReader(new InputStreamReader(inputStream));
        StringBuffer buffer = new StringBuffer();
        String line = "";
        try {
            while ((line = fileReader.readLine()) != null) {
                buffer.append(line);
            }
        } catch (Exception e) {
            LOGGER.error("读取文件失败，fileName:{}", fileName, e);
        } finally {
            inputStream.close();
            fileReader.close();
        }


        String contentText = "以下是服务实例伸缩信息, 敬请查看.<br>below is the information of service instance scale, please check. ";
        //邮件表格header
        String header = "<td>分区(Namespace)</td><td>服务(Service)</td><td>伸缩结果(Scale Result)</td><td>伸缩原因(Scale Reason)</td><td>当前实例数(Pod instance number)</td>";
        StringBuilder linesBuffer = new StringBuilder();
        linesBuffer.append("<tr><td>" + "myNamespace" + "</td><td>" + "myServiceName" + "</td><td>" + "myscaleResult" + "</td>" +
                "<td>" + "mReason" + "</td><td>" + "my4" + "</td></tr>");

        //绿色
        String emailHeadColor = "#10fa81";
        String date = DateFormatUtils.format(new Date(), "yyyy/MM/dd HH:mm:ss");
        //填充html模板中的五个参数
        String htmlText = MessageFormat.format(buffer.toString(), emailHeadColor, contentText, date, header, linesBuffer.toString());

        //改变表格样式
        htmlText = htmlText.replaceAll("<td>", "<td style=\"padding:6px 10px; line-height: 150%;\">");
        htmlText = htmlText.replaceAll("<tr>", "<tr style=\"border-bottom: 1px solid #eee; color:#666;\">");
        return htmlText;
    }
}
```


---------

