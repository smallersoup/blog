title: kube-apiserver审计日志记录和采集
date: '2019-10-18 13:03:22'
updated: '2019-10-18 13:03:22'
tags: [kubernetes]
permalink: /201910181303k8s
---
Kubernetes 审计功能提供了与安全相关的按时间顺序排列的记录集，记录单个用户、管理员或系统其他组件影响系统的活动顺序。它能帮助集群管理员处理以下问题：

*   发生了什么？

*   什么时候发生的？

*   谁触发的？

*   为什么发生？

*   在哪观察到的？

*   它从哪触发的？

*   它将产生什么后果？

Kube-apiserver 执行审计。每个执行阶段的每个请求都会生成一个事件，然后根据特定策略对事件进行预处理并写入后端。

每个请求都可以用相关的 “stage” 记录。已知的 stage 有：

* **RequestReceived -**事件的 stage 将在审计处理器接收到请求后，并且在委托给其余处理器之前生成。

* **ResponseStarted -** 在响应消息的头部发送后，但是响应消息体发送前。这个 stage 仅为长时间运行的请求生成（例如 watch）。

*   **ResponseComplete -** 当响应消息体完成并且没有更多数据需要传输的时候。

*   **Panic -** 当 panic 发生时生成。

**Note:**

审计日志记录功能会增加 API server的内存消耗，因为需要为每个请求存储审计所需的某些上下文。此外，内存消耗取决于审计日志记录的配置。

## 审计策略

审计政策定义了关于应记录哪些事件以及应包含哪些数据的规则。处理事件时，将按顺序与规则列表进行比较。第一个匹配规则设置事件的 [审计级别][auditing-level]。已知的审计级别有：

**None -**符合这条规则的日志将不会记录。

**Metadata -**记录请求的 metadata（请求的用户、timestamp、resource、verb 等等），但是不记录请求或者响应的消息体。

**Request -**记录事件的 metadata 和请求的消息体，但是不记录响应的消息体。这不适用于非资源类型的请求。

**RequestResponse -**记录事件的 metadata，请求和响应的消息体。这不适用于非资源类型的请求。

您可以使用 --audit-policy-file 标志将包含策略的文件传递给 kube-apiserver。如果不设置该标志，则不记录事件。注意 rules 字段必须在审计策略文件中提供。

以下是一个审计策略文件的示例：
```shell
audit/audit-policy.yaml
```

```yaml
apiVersion: audit.k8s.io/v1beta1 # This is required.
kind: Policy
# Don't generate audit events for all requests in RequestReceived stage.
omitStages:
  - "RequestReceived"
rules:
  # Log pod changes at RequestResponse level
  - level: RequestResponse
    resources:
    - group: ""
      # Resource "pods" doesn't match requests to any subresource of pods,
      # which is consistent with the RBAC policy.
      resources: ["pods"]
  # Log "pods/log", "pods/status" at Metadata level
  - level: Metadata
    resources:
    - group: ""
      resources: ["pods/log", "pods/status"]

  # Don't log requests to a configmap called "controller-leader"
  - level: None
    resources:
    - group: ""
      resources: ["configmaps"]
      resourceNames: ["controller-leader"]

  # Don't log watch requests by the "system:kube-proxy" on endpoints or services
  - level: None
    users: ["system:kube-proxy"]
    verbs: ["watch"]
    resources:
    - group: "" # core API group
      resources: ["endpoints", "services"]

  # Don't log authenticated requests to certain non-resource URL paths.
  - level: None
    userGroups: ["system:authenticated"]
    nonResourceURLs:
    - "/api*" # Wildcard matching.
    - "/version"

  # Log the request body of configmap changes in kube-system.
  - level: Request
    resources:
    - group: "" # core API group
      resources: ["configmaps"]
    # This rule only applies to resources in the "kube-system" namespace.
    # The empty string "" can be used to select non-namespaced resources.
    namespaces: ["kube-system"]

  # Log configmap and secret changes in all other namespaces at the Metadata level.
  - level: Metadata
    resources:
    - group: "" # core API group
      resources: ["secrets", "configmaps"]

  # Log all other resources in core and extensions at the Request level.
  - level: Request
    resources:
    - group: "" # core API group
    - group: "extensions" # Version of group should NOT be included.

  # A catch-all rule to log all other requests at the Metadata level.
  - level: Metadata
    # Long-running requests like watches that fall under this rule will not
    # generate an audit event in RequestReceived.
    omitStages:
      - "RequestReceived"
```

也可以使用最低限度的审计策略文件在 Metadata 级别记录所有请求：

```yaml
# Log all requests at the Metadata level.
apiVersion: audit.k8s.io/v1beta1
kind: Policy
rules:
- level: Metadata
```

## 审计日志后端

k8s目前提供两种日志后端，Log后端和webhook后端，Log后端可以将日志输出到文件，webhook后端将日志发送到远端日志服务器，接下来暂且只对Log后端日志的记录配置和采集做一下实践。

**以下实践组件版本docker ce17，k8s 1.9.2**

可以使用以下 kube-apiserver 标志配置 Log 审计后端：

**--audit-log-path**指定用来写入审计事件的日志文件路径。不指定此标志会禁用日志后端。- 意味着标准化

**--audit-log-maxage**定义了保留旧审计日志文件的最大天数

**--audit-log-maxbackup**定义了要保留的审计日志文件的最大数量

**--audit-log-maxsize**定义审计日志文件的最大大小（兆字节）

我司目前集群中kube-apiserver组件作为static pod方式运行，生命周期由kubelet直接管理，static pod由kebelet根据yaml文件创建，yaml存放路径为/etc/kubernetes/manifests/目录，其中apiserver由kubelet根据kube-apiserver.yaml创建，Log后端需要在kube-apiserver.yaml的启动参数里加以下参数：

```shell
--feature-gates=AdvancedAuditing=true
--audit-policy-file=/etc/kubernetes/pki/audit-policy.yaml
--audit-log-format=json
--audit-log-path=/var/log/kubernetes/kubernetes-audit
--audit-log-maxage=30 
--audit-log-maxbackup=3 
--audit-log-maxsize=100 
```

**说明：**

*   AdvancedAuditing指明启用高级审计功能，即：可以使--audit-policy-file参数指定审计策略，该参数从k8s 1.8版本以后默认为true；

*   audit-policy-file指定策略文件的位置，该路径为kube-apiserver容器内的路径，所以得从宿主机挂载策略文件到容器内，故暂且放在/etc/kubernetes/pki/目录下；

*   audit-log-format指定最终审计日志的格式为json，该参数默认为json；

*   audit-log-path指定最终审计日志存放在容器内的位置，该位置会自动创建。上述表示最终的审计日志文件为kubernetes-audit

**最终配置如下：**

![image](https://img-blog.csdnimg.cn/20191018004829812.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

修改完成后，kubelet会自动删除重建kube-apiserver的pod（如果pod被删除后，过几分钟还不被创建，可以修改--audit-log-maxbackup的值保存退出，等待pod被创建---这可能是一个bug），重启状态变为running后可以进入容器查看生成的审计日志文件：

![image](https://img-blog.csdnimg.cn/20191018004830142.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

查看该日志：

![image](https://img-blog.csdnimg.cn/20191018004832126.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

达到100M后：

![image](https://img-blog.csdnimg.cn/20191018004832638.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

因为后面要用fluentd作为agent去采集该日志，所以需要把容器内的日志挂载到宿主机目录下，修改kube-apiserver.yaml如下，即将容器内/var/log/kubernetes目录挂载到宿主机的/var/log/kubernetes目录。

![image](https://img-blog.csdnimg.cn/20191018004832845.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

#### **日志采集**

目前集群中已部署了fluentd elasticsearch日志方案，所以选用fluentd作为 Logging-agent ，Elasticsearch作为  Logging Backend 。集群中的fluentd-es作为DaemonSet 方式运行，根据DaemonSet的特性，应该在每个Node上都会运行fluentd-es的pod，但实际情况是19环境上3个master节点都没有该pod。查看名为fluentd-es-v1.22的DaemonSet yaml可以发现，pod只会运行在有alpha.kubernetes.io/fluentd-ds-ready: “true”标签的node上：

![image](https://img-blog.csdnimg.cn/20191018004833390.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

查看master节点的node yaml，发现确实没有该标签。故需要在master节点node上添加该标签：

![image](https://img-blog.csdnimg.cn/2019101800483521.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

添加完label后，可以看到在docker-vm-6节点上pod会被自动创建。

Fluentd的配置文件在容器内的/etc/td-agent/td-agent.conf中配置，部分配置截图如下：

![image](https://img-blog.csdnimg.cn/20191018004835379.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

该配置由名为fluentd的ConfigMap指定：

![image](https://img-blog.csdnimg.cn/20191018004836830.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

可以看到配置里并不会去采集、转发审计日志/var/log/kubernetes/kubernetes-audit，所以需要在该ConfigMap中添加以下配置：

![image](https://img-blog.csdnimg.cn/201910180048373.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

添加后的截图如下：

![image](https://img-blog.csdnimg.cn/20191018004838465.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

之后需要重启一下kube-apiserver节点的fluentd pod，fluentd采集时，也会输出日志到宿主机的/var/log/fluentd.log里，可以看到错误日志等信息，用于定位问题。如果该文件没有审计日志相关错误，日志应该就会被发送到logging-backend：elasticsearch，可以用以下命令验证：

*   先查看elasticsearch的service IP和Port，然后用curl命令调用rest接口查询当前集群中所有index信息：

![image](https://img-blog.csdnimg.cn/20191018004838908.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

*   查询到审计日志信息如下，大概有220万条记录：

![image](https://img-blog.csdnimg.cn/20191018004839598.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

详细信息如下，和审计日志文件中记录的一样：

![image](https://img-blog.csdnimg.cn/20191018004841772.jpeg?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)

  后续可以用Kibana进行日志展示，Elasticsearch、Fluentd、Kibana即为大名鼎鼎的EFK日志收集方案，还有ELK等，可以根据项目的需求选择适当的组件。
