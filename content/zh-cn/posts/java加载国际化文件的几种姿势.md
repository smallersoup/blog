---
title: java加载国际化文件的几种姿势
date: '2019-10-17 15:37:23'
updated: '2019-10-17 15:37:23'
tags: [java]
permalink: /201910171537java
---
![](https://img.hacpai.com/bing/20190316.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

***1、***

通过util包中的ResourceBundle加载：

首先国际化资源文件放在了classpath下的i18n目录下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/10f80654d71352adea8f7023b9d12dac.png)

mymessage_en_US.properties：

```xml
com.website.operation=\u67e5\u8be2\u64cd\u4f5c\u65e5\u5fd7
com.website.write=\u5199\u65e5\u5fd7
com.website.writeLog=\u5199 {0} \u65e5\u5fd7
```
mymessage_en_US.properties：

```xml
com.website.operation=queryOperationLog
com.website.write=recordLog
com.website.writeLog=record {0} Log
```

利用ResourceBundle加载国际化文件，这里列出四个方法，分别是利用默认Locale、zh_CN、en_US以及带占位符的处理方式。这里需要注意的是BaseName为classpath下的目录+/+国际化文件名前缀，即i18n/mymessage

```java
package com.website.controller.utils;

import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;

/**
* @program: website
* @description: 获取国际化配置文件
* @author: smallsoup
* @create: 2018-07-27 22:32
**/

public class ResourceUtils {

   public static String getEnglishValueByKey(String key){

       Locale locale = new Locale("en", "US");
       //使用指定的英文Locale
       ResourceBundle mySource = ResourceBundle.getBundle("i18n/mymessage", locale);
       return mySource.getString(key);
   }

   public static String getChineseValueByKey(String key){

       Locale locale = new Locale("zh", "CN");
       //使用指定的中文Locale
       ResourceBundle mySource = ResourceBundle.getBundle("i18n/mymessage", locale);
       return mySource.getString(key);
   }

   public static String getDeafultValueByKey(String key){

       //使用默认的Locale
       ResourceBundle mySource = ResourceBundle.getBundle("i18n/mymessage");
       return mySource.getString(key);
   }

   public static String getValueAndPlaceholder(String key){

       //使用默认的Locale
       ResourceBundle mySource = ResourceBundle.getBundle("i18n/mymessage");

       String beforeValue = mySource.getString(key);

       //填充国家化文件中的占位符
       String afterValue = MessageFormat.format(beforeValue, "安全");
       return afterValue;
   }

}
```

在controller里面调用ResourceUtils里的方法：

```java
  @RequestMapping(value = "/projectadd")
   public String projectAdd(){

       LOGGER.warn("projectAdd getChineseValueByKey is {}", ResourceUtils.getChineseValueByKey("com.website.operation"));
       LOGGER.warn("projectAdd getDeafultValueByKey is {}", ResourceUtils.getDeafultValueByKey("com.website.operation"));
       LOGGER.warn("projectAdd getEnglishValueByKey is {}", ResourceUtils.getEnglishValueByKey("com.website.operation"));
       LOGGER.warn("projectAdd getValueAndPlaceholder is {}", ResourceUtils.getValueAndPlaceholder("com.website.writeLog"));
       return "project/projectadd";
   }
```

启动tomcat打印日志：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/f8f5e69dedebc75f59513e8868aeecce.png)


***2、***

利用spring的ResourceBundleMessageSource

ResourceBundleMessageSource是基于JDK ResourceBundle的MessageSource接口实现类。它会将访问过的ResourceBundle缓存起来，以便于下次直接从缓存中获取进行使用。

和上面不同的是ResourceUtils的实现，实现如下：

```java
package com.website.controller.utils;


import org.springframework.context.support.ResourceBundleMessageSource;

import java.util.Locale;

/**
* @program: website
* @description: 获取国际化配置文件
* @author: smallsoup
* @create: 2018-07-27 22:32
**/

public class ResourceUtils {

   private static ResourceBundleMessageSource messageSource = new ResourceBundleMessageSource();

   static {
       //指定国家化资源文件路径
       messageSource.setBasename("i18n/mymessage");
       //指定将用来加载对应资源文件时使用的编码，默认为空，表示将使用默认的编码进行获取。
       messageSource.setDefaultEncoding("UTF-8");
   }

   public static String getChineseValueByKey(String key){

       return messageSource.getMessage(key, null, Locale.CHINA);
   }

   public static String getDeafultValueByKey(String key){

       return messageSource.getMessage(key, null, null);
   }

   public static String getEnglishValueByKey(String key){

       return messageSource.getMessage(key, null, Locale.US);
   }

   public static String getValueAndPlaceholder(String key){

       return messageSource.getMessage(key, new Object[]{"安全"}, null);
   }

}
```
***3、***

利用spring的ReloadableResourceBundleMessageSource

ReloadableResourceBundleMessageSource也是MessageSource的一种实现，其用法配置等和ResourceBundleMessageSource基本一致。所不同的是ReloadableResourceBundleMessageSource内部是使用PropertiesPersister来加载对应的文件，这包括properties文件和xml文件，然后使用java.util.Properties来保存对应的数据。

```java
package com.website.controller.utils;

import org.springframework.context.support.ReloadableResourceBundleMessageSource;

import java.util.Locale;

/**
* @program: website
* @description: 获取国际化配置文件
* @author: smallsoup
* @create: 2018-07-27 22:32
**/

public class ResourceUtils {

   private static ReloadableResourceBundleMessageSource messageSource = new ReloadableResourceBundleMessageSource();

   static {
       //指定国家化资源文件路径
       messageSource.setBasename("i18n/mymessage");
       //指定将用来加载对应资源文件时使用的编码，默认为空，表示将使用默认的编码进行获取。
       messageSource.setDefaultEncoding("UTF-8");

       //是否允许并发刷新
       messageSource.setConcurrentRefresh(true);

       //ReloadableResourceBundleMessageSource也是支持缓存对应的资源文件的，默认的缓存时间为永久，即获取了一次资源文件后就将其缓存起来，以后再也不重新去获取该文件。这个可以通过setCacheSeconds()方法来指定对应的缓存时间，单位为秒
       messageSource.setCacheSeconds(1200);
   }

   public static String getChineseValueByKey(String key){

       return messageSource.getMessage(key, null, Locale.CHINA);
   }

   public static String getDeafultValueByKey(String key){

       return messageSource.getMessage(key, null, null);
   }

   public static String getEnglishValueByKey(String key){

       return messageSource.getMessage(key, null, Locale.US);
   }

   public static String getValueAndPlaceholder(String key){

       return messageSource.getMessage(key, new Object[]{"安全"}, null);
   }

}
```

这三种方式最后结果是一样的。

----

**参考：**

国际化MessageSource

***http://elim.iteye.com/blog/2392583***

-----
