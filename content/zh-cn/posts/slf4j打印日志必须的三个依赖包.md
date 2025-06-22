title: slf4j打印日志必须的三个依赖包
date: '2019-10-17 15:22:03'
updated: '2019-10-17 15:22:03'
tags: [java, slf4j]
permalink: /201910171521java
---
![](https://img.hacpai.com/bing/20180329.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

日志相关包 slf4j打印日志必须的三个依赖包
slf4j假设使用log4j做为底层日志工具，运行以上程序需要三个包：
* log4j-1.2.xx.jar、
* slf4j-api-x.x.x.jar、
* slf4j-log4j12-x.x.x.jar

```maven
 <dependency>
	<groupId>log4j</groupId>
	<artifactId>log4j</artifactId>
	<version>1.2.17</version>
</dependency>
<dependency>
	<groupId>org.slf4j</groupId>
	<artifactId>slf4j-log4j12</artifactId>
	<version>1.7.21</version>
</dependency>

<dependency>
	<groupId>org.slf4j</groupId>
	<artifactId>slf4j-api</artifactId>
	<version>1.7.21</version>
</dependency>
```

log4j.properties文件配置：
```
### set log levels ###
log4j.rootLogger = INFO,root,stdout

log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.conversionPattern=%d{yyyy-MM-dd HH:mm:ss.SSSXXX} %-5p [%t] [%C %L] %m%n

log4j.appender.root.Append=true
log4j.appender.root.File=${scheduleProject}logs/root.log
log4j.appender.root.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss.SSSXXX} %-5p [%t] [%C %L] %m%n
log4j.appender.root.layout=org.apache.log4j.PatternLayout
log4j.appender.root.MaxBackupIndex=50
log4j.appender.root.MaxFileSize=20MB
log4j.appender.root=org.apache.log4j.RollingFileAppender
log4j.appender.root.zipPermission=400
log4j.appender.root.logPermission=600
```

web.xml配置：
```
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1" metadata-complete="true">

    <display-name>Archetype Created Web Application</display-name>

      <!-- 加载log4j的配置文件log4j.properties -->
      <context-param>
          <param-name>log4jConfigLocation</param-name>
          <param-value>classpath:config/log4j.properties</param-value>
      </context-param>

      <!-- 设定刷新日志配置文件的时间间隔，这里设置为10s -->
      <context-param>
          <param-name>log4jRefreshInterval</param-name>
          <param-value>10000</param-value>
      </context-param>

    <!--加载Spring框架中的log4j监听器Log4jConfigListener-->
    <listener>
        <listener-class>org.springframework.web.util.Log4jConfigListener</listener-class>
    </listener>

    <!-- 为避免项目间冲突，定义唯一的 webAppRootKey -->
       <context-param>
           <param-name>webAppRootKey</param-name>
           <param-value>scheduleProject</param-value>
       </context-param>

    <!-- 注册字符集过滤器 -->
    <filter>
        <filter-name>characterEncodingFilter</filter-name>
        <filter-class>org.springframework.web.filter.CharacterEncodingFilter</filter-class>
        <!-- 指定字符集编码 -->
        <init-param>
            <param-name>encoding</param-name>
            <param-value>utf-8</param-value>
        </init-param>
    </filter>
    <filter-mapping>
        <filter-name>characterEncodingFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>

    <!-- 注册前端控制器 -->
    <servlet>
        <servlet-name>springmvc</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>classpath*:config/spring-*.xml</param-value>
        </init-param>
    </servlet>
    <servlet-mapping>
        <servlet-name>springmvc</servlet-name>
        <!--默认匹配所有的请求-->
        <url-pattern>/</url-pattern>
    </servlet-mapping>

</web-app>


```

