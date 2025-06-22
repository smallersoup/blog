---
title: 自动评论csdn博客文章实现
date: '2019-10-17 17:52:19'
updated: '2019-10-17 17:52:19'
tags: [blog, java]
permalink: /201910171752blog
---
![](https://img.hacpai.com/bing/20181123.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

我们来用java代码爬取csdn博客网站，然后自动评论，这一波操作可以说是相当风骚了，话不多说，咱上代码。



第一步是登录代码，这个网上一大把，代码中用到了jsoup依赖包，用于解析html获取相应元素，相当于css选择器，很强大的三方件。

```java
/**
  * 登录csdn页面,评论当然需要登录了
  * 
  * @throws Exception
  */
 public static void loginCsdnPager() throws Exception {
   String html = HttpUtils.sendGet("https://passport.csdn.net/account/login?ref=toolbar");

   try {
     Thread.currentThread().sleep(3000);
   } catch (InterruptedException e) {
     // TODO Auto-generated catch block
     e.printStackTrace();
   }
   Document doc = Jsoup.parse(html);

   Element form = doc.select(".user-pass").get(0);
   String lt = form.select("input[name=lt]").get(0).val();
   String execution = form.select("input[name=execution]").get(0).val();
   String _eventId = form.select("input[name=_eventId]").get(0).val();

   List<NameValuePair> nvps = new ArrayList<NameValuePair>();
   nvps.add(new BasicNameValuePair("username", CSDNACCOUNT));
   nvps.add(new BasicNameValuePair("password", CSDNPASSWORD));
   nvps.add(new BasicNameValuePair("lt", lt));
   nvps.add(new BasicNameValuePair("execution", execution));
   nvps.add(new BasicNameValuePair("_eventId", _eventId));

   System.out.println(nvps);
   // 开始请求CSDN服务器进行登录操作。一个简单封装，直接获取返回结果
   String ret = HttpUtils.sendPost("https://passport.csdn.net/account/login", nvps);

   System.out.println("ret is " + ret);
   // ret中会包含以下信息，进行判断即可。
   if (ret.indexOf("redirect_back") > -1) {
     System.out.println("登陆成功。。。。。");
   } else if (ret.indexOf("登录太频繁") > -1) {
     throw new Exception("登录太频繁，请稍后再试。。。。。");
   } else {
     throw new Exception("登录太频繁，请稍后再试。。。。。");
   }
 }
```


有了登录代码我们还得获取博客文章列表，这是我们爬取的源头。下面以博客首页为起点往其他网络节点爬：



https://blog.csdn.net



我们可以把自己当做一个虫子，接下来将在蜘蛛网上从A节点到B节点，一直爬到目的地。



首先进入首页，然后获取到首页左侧栏的分类列表的url，点开这些url，就是分类下的所有文章了。这里我们只取每个分类下初始页的文章列表url（当然还可以自行实现鼠标下拉时的分页，以获取到更多的文章列表），这里定义了一个名为FETCHPAGES的数组常量，管理所需爬取的分类列表。

```java

String html = HttpUtils.sendGet("https://blog.csdn.net/");

   Document doc = Jsoup.parse(html);
   Elements as = doc.select(".nav_com").select("li").select("a");

   // 收集文章a标签
   List<Elements> blogList = Lists.newArrayListWithCapacity(as.size());
   for (Element a : as) {

     if (!FETCHPAGES.contains(a.text())) {
       continue;
     }

     String fetcheUrl = "https://blog.csdn.net" + a.attr("href");
     System.out.println(fetcheUrl);
     String blogHtml = HttpUtils.sendGet(fetcheUrl);

     Document blogDoc = Jsoup.parse(blogHtml);

     Elements blogAs = blogDoc.select(".---
title").select("h2").select("a");

     System.out.println(blogAs);
     blogList.add(blogAs);
   }
```

收集好文章列表之后，我们就需要登录了（登录后收集列表会出问题，具体原因不明），这里登录只是接下来评论时必须。

```java
// 收集完a标签后再登陆,否则会丢掉很多a标签,具体原因不名
   loginCsdnPager();

   BufferedOutputStream bos = null;
   // 评论成功计数器
   int count = 0;
   try {
     // 将评论成功的url打印到文件里
     File file = new File("D:/tmp/successLog/success.log");
     bos = new BufferedOutputStream(new FileOutputStream(file));
     // 爬取所有a标签
     for (Elements blogs : blogList) {

       for (Element blog : blogs) {

         // 拿到文章url
         String href = blog.attr("href");

         // 获取文章url后的ID,在评论时需要用到
         String commitSuffixUrl = href.substring(href.lastIndexOf("/") + 1);

         // 打开文章
         String blogHtml = HttpUtils.sendGet(href);
         System.out.println(blog.text() + "------------" + blog.attr("href"));

         Document blogDoc = Jsoup.parse(blogHtml);
         Elements ---
titleAs = blogDoc.select(".---
title-box").select("a");

         System.out.println(---
titleAs);

         if (---
titleAs != null && !---
titleAs.isEmpty()) {
           // 评论请求url前缀
           String commitPrefixUrl = ---
titleAs.get(0).attr("href");
           //
           System.out.println(---
titleAs.text() + "-----------" + commitPrefixUrl);

           // 拼接评论请求url
           String commitUrl = commitPrefixUrl + "/phoenix/comment/submit?id=" + commitSuffixUrl;

           System.out.println("commitUrl ==" + commitUrl);

           // 构造评论请求所需body体
           List<NameValuePair> nvps = new ArrayList<NameValuePair>();
           nvps.add(new BasicNameValuePair("replyId", ""));
           nvps.add(new BasicNameValuePair("content",
               "加Wei信ammlysouw 免费领取java、python、前端、安卓、数据库、大数据、IOS等学习资料"));

           // 发起评论
           String postRequest = HttpUtils.sendPost(commitUrl, nvps);
           JSONObject jsonObj = JSONObject.parseObject(postRequest);

           System.out.println(postRequest);

           // 评论结果,成功为1
           if (jsonObj.getInteger("result") == 1) {

             String articalUrl = commitPrefixUrl + "/article/details/" + commitSuffixUrl + "\n";
             System.out.println("success articalUrl is " + articalUrl);
             // 将评论成功的url记录到文件
             bos.write(articalUrl.getBytes());
             bos.flush();
             count++;
           } else {
             // 不成功说明请求太快,线程休眠2秒,这里会丢掉评论失败的文章
             try {
               Thread.currentThread().sleep(2 * 60 * 1000);
             } catch (InterruptedException e) {
               // TODO Auto-generated catch block
               e.printStackTrace();
             }
           }
         } else {
           continue;
         }
       }
     }
   } catch (IOException e) {
     System.out.println("error is " + e);
   } finally {

     if (bos != null) {
       try {
         // 把成功的送书记录到文件
         bos.write((count + "\n").getBytes());
         bos.flush();
         System.out.println("bos will colse");
         bos.close();
       } catch (IOException e) {
         // TODO Auto-generated catch block
         System.out.println("error is " + e);
       }
     }
   }
```

登录后就是解析收集到的文章url，然后打开url，拼接评论请求url，以及请求参数，发起post请求，评论上三次以后就会被网站服务器限制，提示评论太快，需要睡眠2秒钟再继续，最后会把评论成功的url和数量记录到本地文件中，便于查看。


