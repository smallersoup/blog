---
title: java这个404你能解决吗？
date: '2019-10-17 17:57:03'
updated: '2019-10-17 17:57:03'
tags: [java, springmvc]
permalink: /201910171756java
---

## 正文

今天在tomcat里部署运行了一个小工程，工程结构如下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/ba6e7774b3bc5b7339659b63665b8f6e.png)

运行tomcat服务器后，访问index.html，发现报404：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/992368e1fe38f2ac2506ae33bc7bc49a.png)

但是后台接口是正常返回的：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d4a9ccb29fee59173fbc62ad16db7368.png)

去看webapps里工程目录下，index.html文件是有的，见鬼了，是哪儿出了问题？

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/de65e64c8f1ef51a3d2287a02a3d5a66.png)

然后看到控制台日志（或者tomcat_home/logs/catalina.log）报错如下：

```sh
org.springframework.web.servlet.PageNotFound.noHandlerFound No mapping fo
und for HTTP request with URI [/artmuseum/index.html] in DispatcherServlet with name 'springmvc'
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/97a4d97ea72854f8fa64dab4987b093e.png)

大致意思是springmvc这个servlet处理不了index.html。原来是配置有问题。

看看web.xml配置，是这样写的：

```xml

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
```

这里url-pattern匹配所有请求，可以实现现在很流行的REST风格，但是会导致js、html、css等静态资源被拦截，拦截后找不到对应的Handler去处理，就会报404





**可以通过以下几种方式去解决：**



**1、**

在web.xml中配置默认servlet，去处理静态资源，配置如下：

```xml
<servlet-mapping>
 <servlet-name>default</servlet-name>
 <url-pattern>*.html</url-pattern>
</servlet-mapping>
<servlet-mapping>
 <servlet-name>default</servlet-name>
 <url-pattern>*.css</url-pattern>
</servlet-mapping>
<servlet-mapping>
 <servlet-name>default</servlet-name>
 <url-pattern>*.xml</url-pattern>
</servlet-mapping>
<servlet-mapping>
 <servlet-name>default</servlet-name>
 <url-pattern>*.swf</url-pattern>
</servlet-mapping>
```

这样配置后，匹配到的静态资源会被Servlet名称是"default"的DefaultServletHttpRequestHandler去处理，这样就可以找到了。但是该方式每种静态资源文件都得配置一个。



**2、**

 在spring3.0.4以后版本提供了mvc:resources,使用方法：

```xml
<!-- 对静态资源文件的访问 -->      
<mvc:resources mapping="/css/**" location="/css/" />
<mvc:resources mapping="/js/**" location="/js/" />
```

使用<mvc:resources/>元素,把mapping的URI注册到SimpleUrlHandlerMapping的urlMap中,

key为mapping的URI pattern值,而value为ResourceHttpRequestHandler,

这样就巧妙的把对静态资源的访问由HandlerMapping转到ResourceHttpRequestHandler处理并返回,所以就支持classpath目录,jar包内静态资源的访问。


**3、**

使用<mvc:default-servlet-handler/>

```xml
<mvc:default-servlet-handler/>
```

该标签会把"/**" url,注册到SimpleUrlHandlerMapping的urlMap中,把对静态资源的访问由HandlerMapping转到DefaultServletHttpRequestHandler 处理并返回，

DefaultServletHttpRequestHandler使用就是各个Servlet容器自己的默认Servlet

按照最简单的第三种方式，修改以后，index.html页面访问正常：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/119c3a9996ab99f06da22678278a84c6.png)

总结一下，归根结底还是自己对SpringMVC不熟悉。

