---
title: 亚马逊AWS云服务器不合理扣费怎么处理
date: '2019-10-17 14:37:39'
updated: '2019-10-17 14:37:39'
tags: [服务器]
permalink: /201910171437aes
---
![](https://img.hacpai.com/bing/20180512.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


有些小伙伴可能不知道，亚马逊AWS对新用户有个免费体验一年的活动。如果希望体验免费亚马逊AWS云服务器产品，或者看看他们后台面板长什么样，体验产品的速度和性能，又或者准备搭建一个免费t z，可以
注册玩玩。

很简单，全程基本都是中文，不用担心看不懂英文。

----

我是2018年6月30号注册的账号，在EC2面板创建了一个实例，平时就上上谷歌；国内网速慢，在上面下载一些kubernetes镜像，编译一些golang项目。

悲剧的是我把时间记错了，以为是2016年8月10号开始使用的，能用到今年8月。直到8月份信用卡收到扣费提示，才发现时间记错了...
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee3.PNG)\]](https://img-blog.csdnimg.cn/20191013230918844.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
于是乎，赶紧到EC2 DashBoard面板把实例停止，删除掉，以为这样就不会再扣费了。

结果到9月份又收到信用卡扣费提醒：
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee4.PNG)\]](https://img-blog.csdnimg.cn/20191013230939150.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
这次我以为是扣除8月份的，也就20多元，没当回事。

到10月份又收到信用卡扣费提醒：
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee5.PNG)\]](https://img-blog.csdnimg.cn/20191013230948297.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
这次我就解释不了了。

登陆亚马逊控制台，点击到【用户名】>> 我的账户 >> 账单，选择7月份，看到扣费详情：
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee6.PNG)\]](https://img-blog.csdnimg.cn/20191013230956871.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

* 每个云服务器实例每小时0.0716美元，共使用160小时，扣费11.46美元；

* 每月每GB通用固态SSD（gp2）预置存储0.10美元，使用6.422 GB，扣费0.64美元；

* 每小时未附加到正在运行的实例的每个弹性IP地址0.005美元，扣费2.92美元；

同样的查看了8，9，10月的扣费详情后。我把EC2 DashBoard里所有资源都删除掉。
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee2.png)\]](https://img-blog.csdnimg.cn/20191013231003699.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

有一个默认安全组，是直接删不掉的，需要去删除vpc，安全组就会被删除。![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee1.png)\]](https://img-blog.csdnimg.cn/20191013231010720.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

如果不是因为免费，1核2M，40G硬盘这价格，其实还是很贵的。

能不能把这些费用让退回来呢？于是我点击 支持中心 >> create case：
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee7.PNG)\]](https://img-blog.csdnimg.cn/20191013231020827.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee8.PNG)\]](https://img-blog.csdnimg.cn/20191013231029587.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

```shell
I have released the cloud server since in August. Although the elastic IP service has not been released, 
but there is no traffic, Why does the elastic IP cost the billing in August, September and October? 
I think this is unreasonable, I need you to return the elastic IP fee deducted from August to October months.
Pleas help and check and confim, contact me by my email 8374108792@qq.com or my phone +8615211111104.
```

提交后，过了几小时，客服回复我了
```shell
Hello,

Thank you for your reply.

I've immediately refund the charges back it will take 5 days to complete.

Now for any Elastic Ip left idle or not 
associated with an instance a small charge gets generated I know you've not been aware. 
So to avoid unexpected charges in the future, 
please make sure to monitor your usage periodically and 
let us know if you have any questions regarding the billing aspects of our services. 
```
大概意思是，会立即退还费用，但到账还需要5天才能完成。
现在对于任何弹性Ip闲置或与一个小实例负责生成我知道你没有意识到。
所以在未来避免意想不到的费用,请确认定期监控您的使用,让我们知道如果你有任何关于我们的计费方面的问题。


在账单里查看到已经处理了退款：![(/img/2019-10-13-cloud-service-server-deduct-fee.md/fee9.PNG)\]](https://img-blog.csdnimg.cn/20191013231048201.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

提case时也不用担心英语不好，怕客服看不懂，直接在谷歌翻译上翻译一下就可以，基本都可以理解！

其实AWS的服务真的挺好、只要不是恶意使用还去退款的、基本上都可以申请退款成功。

如果你也在使用亚马逊，以下这些点还是得注意一下，避免带来困扰：

* 需要用到手机号码PIN验证，以及信用卡会扣1美金作为验证卡是否能用的费用；

* 免费12个月AWS云服务器，有流量限制的，如果超过流量会额外计费，如果不好过反正就免费使用。其规定的是一个周期30天内免费流量是15G，包括出和入的流量，如果超了就要从信用卡扣款。这一项一定要注意，而且注意是30天一个月如果有31天的话就需要停一天服务，流量监控可以在控制面板里面去查看；

* 一年到期后，一定要记得释放所有资源，否则会出现直接在信用卡里扣费的情况，费用还是很高的。

---

> 现在我用的是ucloud香港服务器，速度挺快，如果你也需要，可以点击以下链接去注册:
https://passport.ucloud.cn/?invitation_code=C1xAF50DBB253EC&ytag=re677q
然后联系我的微信837448792,获取优惠方式！






