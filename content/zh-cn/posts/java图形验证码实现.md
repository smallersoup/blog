title: java图形验证码实现
date: '2019-10-17 17:59:04'
updated: '2019-10-17 18:00:18'
tags: [java, 验证码]
permalink: /201910171758java
---
![](https://img.hacpai.com/bing/20190705.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

今天来学习下图形验证码的生成，首先依赖开源组件：

```xml
<dependency>
   <groupId>com.github.penggle</groupId>
   <artifactId>kaptcha</artifactId>
   <version>2.3.2</version>
</dependency>
```

在web.xml中配置名为Kaptcha的servlet：

```xml
<servlet>
 <!-- 生成图片的Servlet -->
 <servlet-name>Kaptcha</servlet-name>
 <servlet-class>com.google.code.kaptcha.servlet.KaptchaServlet</servlet-class>

 <!-- 是否有边框 -->
 <init-param>
   <param-name>kaptcha.border</param-name>
   <param-value>no</param-value>
 </init-param>
 <!-- 字体颜色 -->
 <init-param>
   <param-name>kaptcha.textproducer.font.color</param-name>
   <param-value>red</param-value>
 </init-param>
 <!-- 图片宽度 -->
 <init-param>
   <param-name>kaptcha.image.width</param-name>
   <param-value>135</param-value>
 </init-param>
 <!-- 使用哪些字符生成验证码 -->
 <init-param>
   <param-name>kaptcha.textproducer.char.string</param-name>
   <param-value>ACDEFHKPRSTWX345679</param-value>
 </init-param>
 <!-- 图片高度 -->
 <init-param>
   <param-name>kaptcha.image.height</param-name>
   <param-value>50</param-value>
 </init-param>
 <!-- 字体大小 -->
 <init-param>
   <param-name>kaptcha.textproducer.font.size</param-name>
   <param-value>43</param-value>
 </init-param>
 <!-- 干扰线的颜色 -->
 <init-param>
   <param-name>kaptcha.noise.color</param-name>
   <param-value>black</param-value>
 </init-param>
 <!-- 字符个数 -->
 <init-param>
   <param-name>kaptcha.textproducer.char.length</param-name>
   <param-value>4</param-value>
 </init-param>
 <!-- 使用哪些字体 -->
 <init-param>
   <param-name>kaptcha.textproducer.font.names</param-name>
   <param-value>Arial</param-value>
 </init-param>
</servlet>
<!-- 映射的url -->
<servlet-mapping>
 <servlet-name>Kaptcha</servlet-name>
 <url-pattern>/Kaptcha</url-pattern>
</servlet-mapping>
```

html中添加验证码标签，并绑定javascript事件：


```html
<!--验证码-->
<li class="align-top">
 <div class="item-content">
   <div class="item-inner">
     <div class="item-title label">验证码</div>
     <input type="text" id="j_captcha" placeholder="验证码">
       <div class="item-input">
         <img id="captcha_img" alt="点击更换" title="点击更换" src="../Kaptcha"
                                        onclick="changeVerifyCode(this)"/>
       </div>
   </div>
 </div>
</li>
```
```js
<script type="text/javascript">
       function changeVerifyCode(img) {
           // alert("asssssssssss");
           img.src = "../Kaptcha?" + Math.floor(Math.random() * 100);
       };
</script>
```

效果图：

![image](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNTJlMzVhNTQ4ODIxZGM0ZQ?x-oss-process=image/format,png)

