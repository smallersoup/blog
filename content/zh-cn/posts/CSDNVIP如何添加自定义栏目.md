title: CSDN VIP如何添加自定义栏目
date: '2019-10-17 14:33:49'
updated: '2019-10-17 14:33:49'
tags: [blog]
permalink: /201910171433blog
---
![](https://img.hacpai.com/bing/20180806.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)

几个月前我也开始在csdn上开了博客，一来给自己加几个少的可怜的流量，再者，让公众号的原创文章获得更多的曝光，让有需要的同学看到。

写过csdn博客的同学都知道，默认只有打赏c币功能；也没有专门广告位；引导栏目，只有侧栏csdn自己的引导二维码。

----

如何在csdn自定义栏目，加赞赏功能，或者其他等引导，让读者能很直观的看到，而不是在每篇文章加，增加自己工作量。这个功能以前对所有用户开放，但是很不幸，这功能被CSDN下架了，看下图：

![custom](https://img-blog.csdnimg.cn/2019101523524513.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

----

**我也是之前为了给读者下载CSDN资料开了VIP，目前还有400次下载，为了限制，每天有8个免费下载名额，需要的可以扫码关注公众号，在后台回复【2】加我代下载。**

----

鼠标放到头像处，点击下拉框中的【管理博客】>> 点击侧栏的【博客模块管理】

![custom](https://img-blog.csdnimg.cn/20191015235245852.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

![custom](https://img-blog.csdnimg.cn/20191015235246987.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

只能添加一条自定义栏目，栏目内容支持html，可以自由发挥：
![custom](https://img-blog.csdnimg.cn/20191015235248215.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

## 添加公众号引导
```html
<div>
    <p><strong>公众号</strong></p>
    <img src="http://www.liabio.cn/img/me/gongzhonghao-ercode.jpg" alt="长按识别二维码关注,精彩第一时间送达" title="长按识别二维码关注,精彩第一时间送达" height="100%" width="100%">
    <marquee><font color=" red">欢迎扫码关注！ </font></marquee>
</div>
```
### 效果图
![custom](https://img-blog.csdnimg.cn/20191015235249267.png)

## 添加QQ、QQ群、邮箱、友情链接等：
```html
<div id="custom_column_27694137" class="panel">
    <p><strong>联系方式</strong></p>
    <br><br>
    <ul class="panel_head">
        <span><a target="_blank" href="http://sighttp.qq.com/msgrd?v=3&uin=1939137617&site=&menu=yes">☞ 本人QQ: 1939137617</a>
        </span>
    </ul>
    
    <ul class="panel_head">
        <span><a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=1a08adf5d7f9d49a2a83bb0d3b4acf0e94554895e12dc657ecfb88d706d82673"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="程序员实战" title="程序员实战"></a></span>
    </ul>
    <ul class="panel_head">
        <span><a target="_blank" href="https://github.com/liabio">☞ github.com/liabio</a></span>
    </ul>
    <ul class="panel_head">
        <span><a href="mailto:coderaction@foxmail.com">☞ coderaction@foxmail.com</a></span>
    </ul>
    <span><a href="https://liabio.blog.csdn.net/">☞ https://liabio.blog.csdn.net/</a></span>
    <marquee><font color=" red">欢迎光临！ </font></marquee>
</div>

<div>
    <p><strong>友情链接</strong></p>
    <br><br>
    <a target="_blank" href="http://www.liabio.cn/">【小碗汤】的博客</a><br><br>
    <marquee><font color=" red">欢迎来踩！ </font></marquee>
</div>
```
### 效果图
![custom](https://img-blog.csdnimg.cn/20191015235249524.png)

* 其中点击QQ会打开登陆QQ的对话框，只需要把href里链接中QQ号换为自己的；

* 点击加入QQ群后会跳转到加群窗口，需要在https://qun.qq.com/join.html 网站中登陆需要绑定的QQ号 >> 选择群 >> 复制网页代码
![custom](https://img-blog.csdnimg.cn/20191015235250148.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

* 点击邮箱会打开邮箱登陆窗口，只需修改href中的邮箱即可

## 添加打赏提问
```html
<div>
    <p><strong>欢迎打赏和提问</strong></p>
    <img src="http://www.liabio.cn/img/fee-say2.png" alt="长按识别提问码 向我提问" title="长按识别提问码 向我提问" height="100%" width="100%">
</div>
```

### 效果图
![custom](https://img-blog.csdnimg.cn/20191015235251206.png)

打赏问答图片由【Chat快问】小程序生成。

## 微信、支付宝打赏
```html
<div>
    <p><strong>扫码打赏</strong></p>
    <br>
    <img src="http://www.liabio.cn/img/wechat-zhifubao-QR.png" alt="长按识别 微信|支付宝打赏通用" title="长按识别 微信|支付宝打赏通用" height="100%" width="100%">
</div>
```

只用一个二维码实现微信、支付宝打赏，由小程序【二维码合并】支持。

## 整体代码
```html
<div id="asideCustom41021941" class="aside-box custom-box">
    <div class="aside-content clearfix">
        <div>
             <p><strong>公众号</strong></p>
             <img src="http://www.liabio.cn/img/me/gongzhonghao-ercode.jpg" alt="长按识别二维码关注,精彩第一时间送达" title="长按识别二维码关注,精彩第一时间送达" height="100%" width="100%">
             <marquee><font color=" red">欢迎扫码关注！ </font></marquee>
        </div>
        <br>
        
        <div id="custom_column_27694137" class="panel">
            <p><strong>联系方式</strong></p>
            <ul class="panel_head">
                <span><a target="_blank" href="http://sighttp.qq.com/msgrd?v=3&uin=1939137617&site=&menu=yes">☞ 本人QQ: 1939137617</a>
                </span>
            </ul>
            
            <ul class="panel_head">
                <span><a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=1a08adf5d7f9d49a2a83bb0d3b4acf0e94554895e12dc657ecfb88d706d82673"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="程序员实战" title="程序员实战"></a></span>
            </ul>
            <ul class="panel_head">
                <span><a target="_blank" href="https://github.com/liabio">☞ github.com/liabio</a></span>
            </ul>
            <ul class="panel_head">
                <span><a href="mailto:coderaction@foxmail.com">☞ coderaction@foxmail.com</a></span>
            </ul>
            <span><a href="https://liabio.blog.csdn.net/">☞ https://liabio.blog.csdn.net/</a></span>
            <marquee><font color=" red">欢迎光临！ </font></marquee>
        </div>
        <br>
        
        <div>
            <p><strong>友情链接</strong></p>
            <a target="_blank" href="http://www.liabio.cn/">【小碗汤】的博客</a><br><br>
            <marquee><font color=" red">欢迎来踩！ </font></marquee>
        </div>
        <br>

        <div>
            <p><strong>欢迎打赏和提问</strong></p>
            <img src="http://www.liabio.cn/img/fee-say2.png" alt="长按识别提问码 向我提问" title="长按识别提问码 向我提问" height="100%" width="100%">
        </div>
        <br>
        <div>
            <p><strong>扫码打赏</strong></p>
            <img src="http://www.liabio.cn/img/wechat-zhifubao-QR.png" alt="长按识别 微信|支付宝打赏通用" title="长按识别 微信|支付宝打赏通用" height="100%" width="100%">
        </div>
    </div>
</div>
```


## 整体效果
![custom](https://img-blog.csdnimg.cn/20191015235253724.png)



