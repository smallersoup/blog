---
title: 备战CKA每日一题——第1天 | CKA简介、考纲、Daemonset知识知识点初探
date: '2019-11-19 09:52:40'
updated: '2019-11-21 22:55:02'
tags: [kubernetes, CKA]
permalink: /201911190952kube
---

这两年 Kubernetes 已经成为容器编排的事实标准，预计未来两年内将全面普及，现在企业招这块人才需求也越来越大，工资也是很高的，未来这块的发展空间也很大。

最近正准备备考CKA，CKA是什么？有些人可能还不知道，这里简单普及一下：

CKA 证书是云原生计算基金会 CNCF 组织的，考察的是你是否具备足够管理 Kubernetes 集群的必备知识。考试形式是上机直接在集群上操作，限时 3 小时，非常考验个人知识的扎实程度和 Kubernetes 实践经验。考上 75 分，你就能拿到证书。考试期间只可查阅K8S官方手册。证书有效期两年，考试费用300美元（国外考试费用就是贵），一年内可有一次免费补考的机会。



CKA证书的含金量如何？考不考这个证完全取决于个人，因为持证并不等于上岗，尤其是上心仪公司的岗。考证可以帮你获得初级职位，但高级职位需要个人经验的大量积累。而站在面试官的角度看，有这个证至少可以为你搏一个面试机会，尤其是应届生和有转岗想法的程序员。这些人可能缺乏足够经验，但 CKA 证很能体现个人技术水平，行业认可程度也很高。



## 考纲如下
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191118175827692.png)
可访问https://github.com/cncf/curriculum关注最新的考纲变化！


作为在Kubernetes技术上摸爬滚打1年多的老鸟，最近正准备备考CKA，鉴于此，我希望想证明自己kubernetes开发运维能力的小伙伴能一起从今天开始，我们一起每日一题，在留言区答题打卡。

## 今日考题

以下 Daemonset yaml 中，哪些是正确的？（多选）
```yaml
A. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Never
B. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Onfailure
C. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1 restartPolicy: Always
D. apiVersion: apps/v1 kind: DaemonSet metadata: name: fluentd-elasticsearch namespace: default labels: k8s-app: fluentd-logging spec: selector: matchLabels: name: fluentd-elasticsearch template: metadata: labels: name: fluentd-elasticsearch spec: containers: - name: fluentd-elasticsearch image: gcr.io/fluentd-elasticsearch/fluentd:v2.5.1
```

## 每日解答
每日答题打卡，第二天会较详细的分析考题答案，尽量做到知其然知其所以然。最终还有电子书送给大家，欢迎参与！我们一起备考。
