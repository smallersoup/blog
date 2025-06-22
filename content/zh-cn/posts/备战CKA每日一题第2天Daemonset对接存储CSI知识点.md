---
title: 备战CKA每日一题——第2天 | Daemonset、对接存储CSI知识点
date: '2019-11-19 09:54:46'
updated: '2019-11-21 23:24:21'
tags: [kubernetes, CKA]
permalink: /201911190954kube
---
> 本活动在微信公众号【我的小碗汤】上举行，这里参与答题无效哦！

**接上一篇[备战CKA每日一题——第1天](https://liabio.blog.csdn.net/article/details/103126903)**

## 昨日考题
以下 Daemonset yaml 中，哪些是正确的？（多选）
```yaml
A. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Never
B. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Onfailure
C. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Always
D. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1
```

## 昨日答案
`CD`
## 昨日解析
在考试时，只能用谷歌浏览器，并打开两个标签页，一个是考题的标签页，另一个是kubernetes官网标签页。https://kubernetes.io/
查询daemonset的说明文档，见以下链接：
https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191118210527458.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

> A Pod Template in a DaemonSet must have a RestartPolicy equal to Always, or be unspecified, which defaults to Always.
Daemonset里的pod Template下必须有RestartPolicy，如果没指定，会默认为Always

restartPolicy 字段，可选值为 Always、OnFailure 和 Never。默认为 Always。 一个Pod中可以有多个容器，restartPolicy适用于Pod 中的所有容器。restartPolicy作用是，让kubelet重启失败的容器。

另外Deployment、Statefulset的restartPolicy也必须为Always，保证pod异常退出，或者健康检查`livenessProbe`失败后由kubelet重启容器。
https://kubernetes.io/zh/docs/concepts/workloads/controllers/deployment/

Job和CronJob是运行一次的pod，restartPolicy只能为OnFailure或Never，确保容器执行完成后不再重启。
https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/


## 今日考题
在Kubernetes PVC+PV体系下通过CSI实现的volume plugins动态创建pv到pv可被pod使用有哪些组件需要参与？

```
A. PersistentVolumeController + CSI-Provisoner + CSI controller plugin
B. AttachDetachController + CSI-Attacher + CSI controller plugin
C. Kubelet + CSI node plugin
```

# 作者简洁 
> 作者：小碗汤，一位热爱、认真写作的小伙，目前维护原创公众号：『我的小碗汤』，专注于写golang、docker、kubernetes等知识等提升硬实力的文章，期待你的关注。 转载说明：务必注明来源（注明：来源于公众号：我的小碗汤， 作者：小碗汤）
