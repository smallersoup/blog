---
title: java中this关键字易错点和说明
date: '2019-10-17 15:36:27'
updated: '2019-10-17 15:36:27'
tags: [java]
permalink: /201910171536java
---
![](https://img.hacpai.com/bing/20180324.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

今天首先来看个问题，用原生servlet实现的接口，大家看下控制台输出结果是什么？

web.xml如下：

```xml
<!DOCTYPE web-app PUBLIC
"-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN"
"http://java.sun.com/dtd/web-app_2_3.dtd" >

<web-app>

 <servlet>
   <servlet-name>myServlet</servlet-name>
   <servlet-class>com.smallsoup.servlet.SonServlet</servlet-class>
 </servlet>

 <servlet-mapping>
   <servlet-name>myServlet</servlet-name>
   <url-pattern>/rest/v3/access/*</url-pattern>
 </servlet-mapping>
</web-app>
```

SonServlet.java如下：

```java
package com.smallsoup.servlet;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
* @program: myServlet
* @description: SonServlet
* @author: smallsoup
* @create: 2018-08-01 20:46
**/

public class SonServlet extends ParentServlet{

   @Override
   public void handleGet(HttpServletRequest req, HttpServletResponse resp) {
       System.out.println("I am SonServlet handleGet");
   }
}
```

ParentServlet.java如下：

```java
package com.smallsoup.servlet;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
* @program: myServlet
* @description: ParentServlet
* @author: smallsoup
* @create: 2018-08-01 20:47
**/

public class ParentServlet extends HttpServlet {

   @Override
   protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
       System.out.println("I am ParentServlet doGet");
       this.handleGet(req, resp);
   }

   public void handleGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
       System.out.println("I am ParentServlet handleGet");
       super.doGet(req, resp);
   }
}
```
启动tomcat，用postman发请求：
```sh
GET：http://localhost:8080/rest/v3/access/1212
```

控制台会输出什么呢？答案是：

```sh
I am ParentServlet doGet
I am SonServlet handleGet

```
我相信很多小伙伴应该会答错，以为会输出：
```sh
I am ParentServlet doGet
I am ParentServlet handleGet
```

或者别的答案。小编今天遇到这个问题也懵逼了，基础掌握不扎实，还得回过头来补补。



------



首先根据url匹配到web.xml中定义的name为myServlet的servlet，所以会到SonServlet中去处理，但是SonServlet没有重写HttpServlet的doGet()方法，它的父类ParentServlet重写了，所以请求会到ParentServlet的doGet()方法，但是这里的doGet方法中的this.handleGet中的this指的是什么呢？我们通过debug看到this其实是SonServlet的实例。
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWM2ODE5ZWJmYjVlOWM3MjcucG5n?x-oss-process=image/format,png)

由此看来，this.handleGet会去调用SonServlet的方法，这就解释了控制台的输出。



这个问题，主要包含两个知识点：



1、servlet处理请求的流程；

2、this关键字指什么？





下面这篇对this关键字讲的非常好，出自：

https://www.cnblogs.com/zheting/p/7751752.html



### Java中this关键字使用小结：



当一个对象创建后，Java虚拟机（JVM）就会给这个对象分配一个引用自身的指针，这个指针的名字就是 this。

因此，this只能在类中的非静态方法中使用，静态方法和静态的代码块中绝对不能出现this，并且this只和特定的对象关联，而不和类关联，同一个类的不同对象有不同的this。



**1、使用this来区分当前对象**



Java中为解决变量的命名冲突和不确定性问题，引入关键字this代表其所在方法的当前对象的引用：

1)  构造方法中指该构造器所创建的新对象；

2)  方法中指调用该方法的对象；

3)  在类本身的方法或构造器中引用该类的实例变量（全局变量）和方法。



this只能用在构造器或者方法中，用于获得调用当前的构造器方法的对象引用。可以和任何的对象引用一样来处理这个this对象。

**说明：**

当实例变量和局部变量重名，JAVA平台会按照先局部变量、后实例变量的顺序寻找。即，方法中使用到的变量的寻找规律是先找局部变量，再找实例变量。如果没用找到，将会有一个编译错误而无法通过编译。

如果使用this.a，则不会在方法（局部变量）中寻找变量a,而是直接去实例变量中去寻找，如果寻找不到，则会有一个编译错误。

在一个方法内，如果没有出现局部变量和实例变量重名的情况下，是否使用this关键字是没有区别的。

在同一个类中，Java普通方法的互相调用可以省略this+点号，而直接使用方法名+参数。因为Java编译器会帮我们加上。



**2、 在构造器中使用this来调用对象本身的其他构造器**



在构造器中使用this（[args_list]）；可以调用对象本身的其他的构造器。直接使用this()加上类构造器所需要的参数。就可以调用类本身的其他构造器了。如果类中有多个其他构造器定义，系统将自动根据this()中的参数个数和类型来找出类中相匹配的构造器。

**注意：**  在构造器中可以通过this()方式来调用其他的构造器。但在一个构造器中最多只能调用一个其他的构造器。并且，对其他构造器的调用动作必须放在构造器的起始处（也就是构造器的首行），否则编译的时候将会出现错误，另外不能在构造器以外的地方以这种方式调用构造器。



3、 this关键字还有一个重大的作用就是返回类的引用。如在代码中，可以使用return this来返回某个类的引用。此时，这个this关键字就代表类的名称。





**例1、把this作为参数传递**

当你要把自己作为参数传递给别的对象时，也可以用this。如：

```java
package com.smallsoup.servlet;

/**
* @program: myServlet
* @description: A
* @author: smallsoup
* @create: 2018-08-01 22:58
**/

public class A {

   public A(){
       new B(this).print();
   }

   public void print(){
       System.out.println("From A!");
   }

   public static void main(String[] args) {
       new A();
   }
}

class B{
   A a;
   public B(A a){
       this.a = a;
   }

   public void print(){
       a.print();
       System.out.println("From B!");
   }
}
```

运行结果：
```sh
From A!
From B!
```

在这个例子中，对象A的构造函数中，用new B(this)把对象A自己作为参数传递给了对象B的构造函数。





**例2、注意匿名类和内部类中的中的this**

有时候，我们会用到一些内部类和匿名类，如事件处理。当在匿名类中出现this时，这个this则指的是匿名类或内部类本身。这时如果我们要使用外部类的方法和变量的话，则应该加上外部类的类名。如下面这个例子：

```java
package com.smallsoup.servlet;

/**
* @program: myServlet
* @description: C
* @author: smallsoup
* @create: 2018-08-01 23:00
**/

public class C {

   int i = 1;
   public C(){
       Thread thread = new Thread(){

           @Override
           public void run(){
               for(;;){//表示是死循环
                   C.this.run();//调用外部方法run()
                   try {
                       sleep(1000);
                   } catch (InterruptedException e) {
                       e.printStackTrace();
                   }
               }
           }
       };//注意这里有分号;
       thread.start();
   }

   public void run(){
       System.out.println("i = " + i);
       i++;
   }

   public static void main(String[] args) throws Exception {
       new C();
   }
}
```

运行结果：每一秒产生一个数：1,2,3 ……



在上面这个例子中, thread 是一个匿名类对象，在它的定义中，它的 run 函数里用到了外部类的 run 函数。这时由于函数同名，直接调用就不行了。这时有两种办法，一种就是把外部的 run 函数换一个名字，但这种办法对于一个开发到中途的应用来说是不可取的。那么就可以用这个例子中的办法用外部类的类名加上 this 引用来说明要调用的是外部类的方法 run。





**例3 、this关键字最大的作用是，让类的一个方法，访问该类的另一个方法或者属性。**

先看一个不好的例子:
```java
package com.smallsoup.servlet;

/**
* @program: myServlet
* @description: Baby
* @author: smallsoup
* @create: 2018-08-01 23:03
**/

public class Baby {

   public void wakeUp(){
       System.out.println("宝宝醒啦");
   }

   public void eat(){
       Baby baby = new Baby();
       baby.wakeUp();
       System.out.println("吃东西");
   }
}
```

这样不符合逻辑。这就相当于本对象的eat方法，需要调用另一个对象的wakeUp方法。

我们看这个例子:

```java
public class Baby {
   
   public void wakeUp() {
       System.out.println("宝宝醒啦");
   }

   public void eat() {
       this.wakeUp();
       System.out.println("吃东西");
   }
}
```

这样就符合逻辑了。自己的eat方法，还需要自己的一个wakeUp方法。

java允许同一个对象的方法直接调用该对象的属性或者方法，所以this可以省略。

 -------------

**注意：java中为什么在static中不能使用this关键字？**

Static方法是类方法，先于任何的实例（对象）存在。即Static方法在类加载时就已经存在了，但是对象是在创建时才在内存中生成。而this指代的是当前的对象在方法中定义使用的this关键字,它的值是当前对象的引用。也就是说你只能用它来调用属于当前对象的方法或者使用this处理方法中成员变量和局部变量重名的情况，而且，更为重要的是this和super都无法出现在static 修饰的方法中，static 修饰的方法是属于类的，该方法的调用者可能是一个类,而不是对象。如果使用的是类来调用而不是对象，则 this就无法指向合适的对象.所以static 修饰的方法中不能使用this

-----
