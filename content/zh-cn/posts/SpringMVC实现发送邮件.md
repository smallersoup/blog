---
title: SpringMVC实现发送邮件
date: '2019-10-17 18:03:34'
updated: '2019-10-17 18:03:34'
tags: [java, springmvc, email]
permalink: /201910171803java
---

## 正文

今天来试着用SpringMVC发送邮件，主要需要依赖以下两个包；

```xml
<!--spring发送邮件依赖spring.version=4.3.8.RELEASE-->
<dependency>
<groupId>org.springframework</groupId>
<artifactId>spring-context-support</artifactId>
<version>${spring.version}</version>
</dependency>

<!-- Javamail API -->
<dependency>
<groupId>javax.mail</groupId>
<artifactId>mail</artifactId>
<version>1.4.5</version>
</dependency>
```

spring-mail.xml配置文件如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
      xmlns:context="http://www.springframework.org/schema/context"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans-4.2.xsd
   http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context-4.2.xsd">

<!-- 引入属性文件 -->
   <context:property-placeholder location="classpath:config/email.properties" ignore-unresolvable="true"/>

  <!-- <bean id="local" class="org.springframework.beans.factory.config.PropertyPlaceholderConfigurer">
       <property name="location" value="classpath:config/email.properties" />
       <property name="ignoreUnresolvablePlaceholders" value="true" />
   </bean>-->
   <!--
       下面列出网易的SMTP服务器名和端口号:
        网易邮箱          SMTP服务器     SMTP端口     POP3服务器       POP3端口
        @126.com        smtp.126.com      25          pop3.126.com      110
        @163.com        smtp.163.com      25          pop3.163.com      110
        @yeah.net       smtp.yeah.net      25          pop3.yeah.net     110
    -->
   <bean id="javaMailSender"
         class="org.springframework.mail.javamail.JavaMailSenderImpl">
       <property name="protocol" value="${email.protocol}"/>
       <property name="host" value="${email.host}"/>
       <property name="port" value="${email.port}"/>
       <property name="username" value="${email.username}"/>
       <property name="password" value="${email.password}"/>
       <property name="defaultEncoding" value="UTF-8"></property>
       <property name="javaMailProperties">
           <props>
               <prop key="mail.auth">${email.auth}</prop>
               <prop key="mail.smtp.timeout">${email.timout}</prop>
           </props>
       </property>

   </bean>

   <bean id="simpleMailMessage" class="org.springframework.mail.SimpleMailMessage">
       <!-- 发件人email -->
       <property name="from" value="${email.username}" />
        <!--收件人email-->
       <property name="to" value="${email.default.to}" />
       <!--email主题(标题)-->
       <property name="subject" value="${email.default.subject}" />
       <!--email主题内容-->
       <property name="text">
         <value>${email.default.text}</value>
       </property>
   </bean>

   <bean id="emailService"
         class="com.website.service.impl.EmailServiceImpl">
       <property name="javaMailSender" ref="javaMailSender"/>
       <property name="simpleMailMessage" ref="simpleMailMessage"/>
   </bean>
</beans>
```

这里加载了发送邮件相关的配置文件email.properties：

```
email.protocol=smtp
email.host=smtp.163.com
email.port=25
email.username=132312312@163.com
email.password=yourpassword
email.default.to=123121@126.com
email.default.subject=Hello
email.default.text=how are you
email.auth=true
email.timout=25000
```

发送简单邮件代码：

```java

public class EmailServiceImpl implements EmailService {

   private static final Logger LOGGER = LoggerFactory.getLogger(EmailServiceImpl.class);

   private JavaMailSender javaMailSender;

   private SimpleMailMessage simpleMailMessage;

   /**
    * @方法名: sendMailSimple
    * @参数名：@param subject  邮件主题
    * @参数名：@param content 邮件内容
    * @参数名：@param to     收件人Email地址
    * @描述语: 发送邮件
    */
   @Override
   public void sendMailSimple(String to, String subject, String content) throws Exception {

       try {
           //用于接收邮件的邮箱
           simpleMailMessage.setTo(to);
           //邮件的主题
           simpleMailMessage.setSubject(subject);
           //邮件的正文，第二个boolean类型的参数代表html格式
           simpleMailMessage.setText(content);

           LOGGER.info("---------------------------{}", simpleMailMessage);
           //发送
           javaMailSender.send(simpleMailMessage);

       } catch (Exception e) {
           throw new MessagingException("failed to send mail!", e);
       }
   }

   public void setJavaMailSender(JavaMailSender javaMailSender) {
       this.javaMailSender = javaMailSender;
   }

   public void setSimpleMailMessage(SimpleMailMessage simpleMailMessage) {
       this.simpleMailMessage = simpleMailMessage;
   }
}
```

跑单元测试的时候报：Could not resolve placeholder异常，不可以解析email.protocol

```
Caused by: org.springframework.beans.factory.BeanDefinitionStoreException: Invalid bean definition with name 'javaMailSender' defined in class path resource [config/spring-mail.xml]: Could not resolve placeholder 'email.protocol' in value "${email.protocol}"; nested exception is java.lang.IllegalArgumentException: Could not resolve placeholder 'email.protocol' in value "${email.protocol}"
```

可能的原因：

1、location中的属性文件配置错误；

2、location中定义的配置文件里面没有对应的placeholder值；

3、Spring容器的配置问题，很有可能是使用了多个PropertyPlaceholderConfigurer或者多个<context:property-placeholder>的原因。



排查以后发现，

applicationContext.xml和spring-mail.xml两个文件都使用了<context:property-placeholder>，前者加载数据库连接配置，后者加载发送邮件相关配置。

```xml
<context:property-placeholder location="classpath:config/db.properties"/>
```

```xml
<context:property-placeholder location="classpath:config/email.properties"/>
```

这个是Spring容器采用反射扫描的发现机制决定的，在Spring 3.0中，可以加ignore-unresolvable="true"解决。

```xml
<context:property-placeholder location="classpath:config/db.properties" ignore-unresolvable="true"/>
```

```xml
<context:property-placeholder location="classpath:config/email.properties" ignore-unresolvable="true"/>
```

**注意**：必须两个都要加，加一个也不行。



在Spring 2.5中，<context:property-placeholder>没有ignore-unresolvable属性，此时可以改用PropertyPlaceholderConfigurer。其实<context:property-placeholder location="xxx.properties" ignore-unresolvable="true" />与下面的配置是等价的。

```xml
<bean id="local" class="org.springframework.beans.factory.config.PropertyPlaceholderConfigurer">
       <property name="location" value="classpath:config/email.properties" />
       <property name="ignoreUnresolvablePlaceholders" value="true" />
   </bean>
```

修改以后，测试用类运行成功：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0b21cf07634d1f09a7ac21eb7009ae74.png)

发送邮件成功：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/035997cc140f3aafb42f630511334efc.png)

其实发送邮件还可以用JavaMail实现，需要依赖两个包：

activation-1.1.jar

mail-1.4.2.jar

