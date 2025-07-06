---
title: ElasticSearch5.x 删除数据
date: '2019-10-18 13:06:55'
updated: '2019-10-18 13:06:55'
tags: [elasticsearch]
permalink: /201910181306elasticsearch
---
以下测试在elasticsearch5.6.10版本。

首先要说明的是ElasticSearch从2.x开始就已经不支持删除一个type了，所以使用delete命令想要尝试删除一个type的时候会出现如下错误：

```shell
No handler found for uri [/dating_profile/zhenai/] and method [DELETE]
```

## 测试

假如存在一个名为dating_profile的index和zhenai的type：

```shell
curl -XDELETE http://192.168.1.102:9200/dating_profile/zhenai
```

执行后报错如下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/2019101800563038.png)

所以现在如果想要删除type有两种选择： 

***1、***重新设置index。 

***2、***删除type下的所有数据。

如果重新设置index，官方建议：

***https://www.elastic.co/guide/en/elasticsearch/reference/5.4/indices-delete-mapping.html***

> **Delete Mapping**
It is no longer possible to delete the mapping for a type. Instead you should delete the index and recreate it with the new mappings.

## 删除index

如下，删除名为dating_profile的index：

```shell
curl -XDELETE http://192.168.1.102:9200/dating_profile/
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005630302.png)

删除成功，返回值为：

```json
{
 "acknowledged": true
}
```
## 删除type下的所有数据

想要一次性删除type为zhenai所有数据内容的话，可以参考官方文档：

***https://www.elastic.co/guide/en/elasticsearch/reference/5.4/docs-delete-by-query.html***

其中有讲到，可以通过_delete_by_query限制到一个单独的type，如下，它仅仅会删除index为dating_profile下type为zhenai下的所有数据：

```json
curl -X POST "http://192.168.1.102:9200/dating_profile/zhenai/_delete_by_query?conflicts=proceed" -H 'Content-Type: application/json' -d'
{
 "query": {
   "match_all": {}
 }
}'
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005630522.jpeg)

删除成功，返回值如下：

```json
{
 "took": 78,
 "timed_out": false,
 "total": 107,
 "deleted": 107,
 "batches": 1,
 "version_conflicts": 0,
 "noops": 0,
 "retries": {
   "bulk": 0,
   "search": 0
 },
 "throttled_millis": 0,
 "requests_per_second": -1.0,
 "throttled_until_millis": 0,
 "failures": []
}

```

也可以一次性删除多个index和多个type下的文档，如下：删除index为dating_profile下的type为zhenai的数据；同时删除index为movies下的type为movie的数据。

```shell
curl -X POST "http://192.168.1.102:9200/dating_profile,movies/zhenai,movie/_delete_by_query" -H 'Content-Type: application/json' -d'
{
 "query": {
   "match_all": {}
 }
}
'
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005630726.jpeg)

返回值如下：

```json
{
 "took": 93,
 "timed_out": false,
 "total": 61,
 "deleted": 61,
 "batches": 1,
 "version_conflicts": 0,
 "noops": 0,
 "retries": {
   "bulk": 0,
   "search": 0
 },
 "throttled_millis": 0,
 "requests_per_second": -1.0,
 "throttled_until_millis": 0,
 "failures": []
}
```

##  题外话

5.xES提供的Reindex可以直接在搜索集群中对数据进行重建。如下可以直接修改mapping。

如下将index为dating_profile改为new_dating_profile

```shell
curl -XPOST "http://192.168.1.102:9200/_reindex?pretty" -H 'Content-Type: application/json' -d'
{
 "source": {
   "index": "dating_profile"
 },
 "dest": {
   "index": "new_dating_profile"
 }
}
'
```

这样执行后，旧的index还是存在的，dating_profile和new_dating_profile都可以查到旧数据。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005630908.gif)

**ElasticSearch＋ELK日志平台全套视频教程等相关学习资源可以在公众号后台回复【1】加小助手索取。**



------------

