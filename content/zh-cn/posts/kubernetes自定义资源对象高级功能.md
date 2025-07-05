---
title: kubernetes自定义资源对象高级功能
date: '2019-10-18 13:33:34'
updated: '2019-10-18 13:33:34'
tags: [kubernetes]
permalink: /201910181333kubernetes
---
kubernetes自定义资源对象再极大程度提高了API Server的可扩展性，让企业能够根据业务需求通过CRD编写controller或者operator来实现生产中各种特殊场景。随着k8s的版本升级，CRD的功能也越来越完善，下面对其中几点进行说明。

以下验证kubernetes版本为1.13.2，docker版本：18.09.5

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/eaa3886beee80673a515559237192ace.png)

## Validation（验证）

在项目中用自定义资源对象时，如果创建自定义资源时某些字段不符合要求，会导致监听该资源对象的controller或者operator出现异常，解析结构体报错，所以Validation这个功能非常实用，在创建时就进行校验，减少后面的排错和异常处理的麻烦。

可以通过 [OpenAPI v3 schema](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#schemaObject)验证自定义对象是否符合标准 。此外，以下限制适用于 schema：

- 字段`default`、`nullable`、`discriminator`、`readOnly`、`writeOnly`、`xml`、 `deprecated` 和 `$ref` 不能设置。
- 该字段 `uniqueItems` 不能设置为 true。
- 该字段 `additionalProperties` 不能设置为 false。

可以使用 kube-apiserver`CustomResourceValidation` 上的功能门（feature gate）禁用此功能：

```shell
--feature-gates=CustomResourceValidation=false
```

从以下特性门参数说明地址，可以看到Validation功能在k8s 1.8版本就已经有了，但是CustomResourceValidation特性门是默认false，1.9Beta之后版本默认为true

<https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/> 

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/8102ad54fb34c2a5ef669b3d5fbcf876.png)

以下示例将大概对该功能进行应用和说明，在以下示例中，CustomResourceDefinition 对自定义对象应用以下验证：

- `spec.replicas` 为必填项，类型为integer，值为大于等于0小于50的偶数（2的倍数）；
- `spec.repository` 为必填项；
- `spec.version`为必填项；
- `spec.pause`为boolean类型；
- `spec.updateStrategy`为object类型，该object中有type、pipeline、assignStrategies属性；
- `spec.updateStrategy.type`为string类型，而且只能为"AssignReceive", "AutoReceive"两个枚举值；
- `spec.updateStrategy.pipeline`为string类型，而且为正整数的字符串，符合正则表达式`^([1-9][0-9]*){1,3}$`;
- `spec.updateStrategy.assignStrategies`为array类型，其元素为object类型（包含slots和fromReplicas属性）；
- `spec.updateStrategy.assignStrategies.slots`为1-16384的正整数；
- `spec.updateStrategy.assignStrategies.fromReplicas`为字符串，符合正则表达式`^[a-z0-9,]{3,}$`，即至少匹配3位a-z或者0-9或者逗号的字符串；
- `spec.pod`为array类型，其元素为object类型（包含configmap、monitorImage、initImage、middlewareImage字段）；
- `spec.pod.configmap`、`spec.pod.monitorImage`、`spec.pod.initImage` 、`spec.pod.middlewareImage`为string类型；且用required指定configmap、initImage、middlewareImage字段为必填项。

将以下内容保存到 `redis-cluster-crd.yaml`：

```yaml
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: redisclusters.redis.middleware.hc.cn
spec:
  group: redis.middleware.hc.cn
  versions:
    - name: v1alpha1
      # Each version can be enabled/disabled by Served flag.
      served: true
      # One and only one version must be marked as the storage version.
      storage: true
  scope: Namespaced
  names:
    kind: RedisCluster
    singular: rediscluster
    listKind: RedisClusterList
    plural: redisclusters
    shortNames:
    - rec
    # 执行kubectl get all时会查到pod、service、该crd等属于all categories的资源对象
    categories:
    - all
  validation:
    # openAPIV3Schema 适用于验证自定义对象的 schema。
    openAPIV3Schema:
      properties:
        spec:
          required: ["replicas", "repository", "version"]
          properties:
            pause:
              type: boolean
            replicas:
              type: integer
              minimum: 0
              maximum: 50
              # 偶数
              multipleOf: 2
            updateStrategy:
              type: object
              properties:
                type:
                  type: string
                  # 枚举
                  enum: ["AssignReceive", "AutoReceive"]
                pipeline:
                  type: string
                  pattern: '^([1-9][0-9]*){1,3}$'
                assignStrategies:
                  type: array
                  items:
                    type: object
                    properties:
                      slots:
                        type: integer
                        minimum: 1
                        maximum: 16384
                      fromReplicas:
                        type: string
                        # 至少匹配3位,a-z或者0-9或者,
                        pattern: '^[a-z0-9,]{3,}$'
            pod:
              type: array
              items:
                type: object
                required: ["configmap", "middlewareImage", "initImage"]
                properties:
                  configmap:
                    type: string
                  monitorImage:
                    type: string
                  initImage:
                    type: string
                  middlewareImage:
                    type: string
```

创建它：

```
kubectl create -f redis-cluster-crd.yaml
```

默认不加validation时，在创建自定义资源对象时，不会校验，有些字段没有了（如`spec.replicas`）都可以正常被创建，为了减少排错的难度和operator、controller的麻烦的检验，所以在创建自定义资源定义时，就把validation加上。以上的检验应该覆盖到了常见的检验场景，其他场景可以自己摸索。具体还可以参考kubernetes源码，1.13.2版本kubernetes源码位于types.go第327行CustomResourceValidation结构体：

```
$GOPATH/src/k8s.io/kubernetes/staging/src/k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/types.go
```

将以下YAML保存到`redis-cluster-cr.yaml`：

```yaml
apiVersion: redis.middleware.hc.cn/v1alpha1
kind: RedisCluster
metadata: 
  name: example000-redis-cluster
  namespace: kube-system
spec:
  # 代表redis集群的个数
  replicas: 3
  # 代表是否进入维修状态
  pause: true
  repository: library/redis
  # 镜像版本，便于后续多版本特化支持
  version: 3.2.6
  #redis集群升级策略
  updateStrategy:
    # 升级类型为AutoReceive（自动分配,不用AssignStrategies）, AssignReceive（指定值分配，需要用AssignStrategies）
    type: AssignReceive1
    pipeline: "100a"
    assignStrategies:
       - 
        slots: 0
        fromReplicas: nodeId1
       - 
        # 从nodeId3,nodeId4一共分配1000个卡槽
        slots: 1000 
        # 多个nodeId用逗号分隔
        fromReplicas: nodeId3,nodeId4
  # redis 实例配置详情
  pod:
    # 配置文件模板名
  - configmap: example000-redis-cluster-config
    # 监控镜像
    monitorImage: redis-exporter:v1
    # 初始化镜像
    #initImage: redis-init:v1
    # 中间件容器镜像
    middlewareImage: redis-trib:3.2.6
```

并创建它：

```shell
kubectl create -f redis-cluster-cr.yaml
```

会发现报以下错误：

```shell
# kubectl apply -f redis-cluster-cr.yaml 
The RedisCluster "example000-redis-cluster" is invalid: []: Invalid value: map[string]interface {}{"apiVersion":"redis.middleware.hc.cn/v1alpha1", "kind":"RedisCluster", "metadata":map[string]interface {}{"namespace":"kube-system", "uid":"b0946031-766b-11e9-b457-000c295db389", "resourceVersion":"44231", "generation":19, "creationTimestamp":"2019-05-14T17:14:10Z", "annotations":map[string]interface {}{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"redis.middleware.hc.cn/v1alpha1\",\"kind\":\"RedisCluster\",\"metadata\":{\"annotations\":{},\"name\":\"example000-redis-cluster\",\"namespace\":\"kube-system\"},\"spec\":{\"pause\":true,\"pod\":[{\"configmap\":\"example000-redis-cluster-config\",\"middlewareImage\":\"redis-trib:3.2.6\",\"monitorImage\":\"redis-exporter:v1\"}],\"replicas\":3,\"repository\":\"library/redis\",\"updateStrategy\":{\"assignStrategies\":[{\"fromReplicas\":\"nodeId1\",\"slots\":0},{\"fromReplicas\":\"nodeId3,nodeId4\",\"slots\":1000}],\"pipeline\":\"100a\",\"type\":\"AssignReceive1\"},\"version\":\"3.2.6\"}}\n"}, "name":"example000-redis-cluster"}, "spec":map[string]interface {}{"version":"3.2.6", "pause":true, "pod":[]interface {}{map[string]interface {}{"middlewareImage":"redis-trib:3.2.6", "monitorImage":"redis-exporter:v1", "configmap":"example000-redis-cluster-config"}}, "replicas":3, "repository":"library/redis", "updateStrategy":map[string]interface {}{"assignStrategies":[]interface {}{map[string]interface {}{"fromReplicas":"nodeId1", "slots":0}, map[string]interface {}{"fromReplicas":"nodeId3,nodeId4", "slots":1000}}, "pipeline":"100a", "type":"AssignReceive1"}}}: validation failure list:
spec.updateStrategy.assignStrategies.fromReplicas in body should match '^[a-z0-9,]{3,}$'
spec.updateStrategy.assignStrategies.slots in body should be greater than or equal to 1
spec.updateStrategy.pipeline in body should match '^([1-9][0-9]*){1,3}$'
spec.updateStrategy.type in body should be one of [AssignReceive AutoReceive]
spec.pod.initImage in body is required
spec.replicas in body should be a multiple of 2
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/8cfe98bce56cc80f3cea064acc49f4d3.png)

如果所有字段都符合校验逻辑，才可以创建对象。

将以下 YAML 保存到 `redis-cluster-cr.yaml`：

```yaml
apiVersion: redis.middleware.hc.cn/v1alpha1
kind: RedisCluster
metadata: 
  name: example000-redis-cluster
  namespace: kube-system
spec:
  # 代表redis集群的个数
  replicas: 6
  # 代表是否进入维修状态
  pause: true
  repository: library/redis
  # 镜像版本，便于后续多版本特化支持
  version: 3.2.6
  #redis集群升级策略
  updateStrategy:
    # 升级类型为AutoReceive（自动分配,不用AssignStrategies）, AssignReceive（指定值分配，需要用AssignStrategies）
    type: AssignReceive
    pipeline: "100"
    assignStrategies:
       - 
        slots: 1
        fromReplicas: all
       - 
        # 从nodeId3,nodeId4一共分配1000个卡槽
        slots: 1000 
        # 多个nodeId用逗号分隔
        fromReplicas: node1,node2
  # redis 实例配置详情
  pod:
    # 配置文件模板名
  - configmap: example000-redis-cluster-config
    # 监控镜像
    monitorImage: redis-exporter:v1
    # 初始化镜像
    initImage: redis-init:v1
    # 中间件容器镜像
    middlewareImage: redis-trib:3.2.6
```

并创建它，发现才可以创建：

```shell
# kubectl apply -f redis-cluster-cr.yaml 
rediscluster.redis.middleware.hc.cn/example000-redis-cluster configured
```



### Category（分类）

类别是自定义资源所属的分组资源的列表（例如 `all`）。您可以使用 `kubectl get <category-name>` 列出属于该类别的资源。此功能可用于 v1.10 及以上k8s版本自定义资源。

以下示例添加 `all` CustomResourceDefinition 中的类别列表，并说明如何使用 `kubectl get all` 输出自定义资源 。

将以下 内容保存到 `redis-cluster-crd.yaml`中执行`kubectl apply -f redis-cluster-crd.yaml`：

```yaml
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: redisclusters.redis.middleware.hc.cn
spec:
  group: redis.middleware.hc.cn
  versions:
    - name: v1alpha1
      # Each version can be enabled/disabled by Served flag.
      served: true
      # One and only one version must be marked as the storage version.
      storage: true
  scope: Namespaced
  names:
    kind: RedisCluster
    singular: rediscluster
    listKind: RedisClusterList
    plural: redisclusters
    shortNames:
    - rec
    # 执行kubectl get all时会查到pod、service、该crd等属于all categories的资源对象
    categories:
    - all
```

将以下内容保存到`redis-cluster-cr.yaml`中执行`kubectl apply -f redis-cluster-cr.yaml`：

```yaml
apiVersion: redis.middleware.hc.cn/v1alpha1
kind: RedisCluster
metadata: 
  name: example000-redis-cluster
  namespace: kube-system
spec:
  # 代表redis集群的个数
  replicas: 6
  # 代表是否进入维修状态
  pause: true
  repository: library/redis
  # 镜像版本，便于后续多版本特化支持
  version: 3.2.6
  #redis集群升级策略
  updateStrategy:
    # 升级类型为AutoReceive（自动分配,不用AssignStrategies）, AssignReceive（指定值分配，需要用AssignStrategies）
    type: AssignReceive
    pipeline: "100"
    assignStrategies:
       - 
        slots: 2000
        fromReplicas: nodeId1
       - 
        # 从nodeId3,nodeId4一共分配1000个卡槽
        slots: 1000 
        # 多个nodeId用逗号分隔
        fromReplicas: nodeId3,nodeId4
  # redis 实例配置详情
  pod:
    # 配置文件模板名
  - configmap: example000-redis-cluster-config
    # 监控镜像
    monitorImage: redis-exporter:v1
    # 初始化镜像
    initImage: redis-init:v1
    # 中间件容器镜像
    middlewareImage: redis-trib:3.2.6
```

执行kubectl get all时会查到pod、service、该crd等属于all categories的资源对象。（这个可能得等几分钟才能生效）

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0ae02e2503580fca4c4f690e29fb6f06.png)



## 子资源

### status子资源

启用状态子资源后，将公开自定义资源的子资源 `/status`。

* 状态和规范节分别由自定义资源内的 `.status` 和 `.spec` JSONPath 表示。
* `PUT /status` 对子资源的请求采用自定义资源对象，并忽略除状态节之外的任何更改。
* `PUT /status` 对子资源的请求仅验证自定义资源的状态节。
* `PUT/ POST/ PATCH` 请求自定义资源忽略更改状态节。
* 对 spec 节的任何更改都会增加 `.metadata.generation` 的值。

在code-generator生成代码时会生成，如下方法：

```go
// RedisClusterInterface has methods to work with RedisCluster resources.
type RedisClusterInterface interface {
	Create(*v1alpha1.RedisCluster) (*v1alpha1.RedisCluster, error)
	Update(*v1alpha1.RedisCluster) (*v1alpha1.RedisCluster, error)
	UpdateStatus(*v1alpha1.RedisCluster) (*v1alpha1.RedisCluster, error)
    ......
}
```



### scale子资源

启用 scale 子资源后，将公开自定义资源的子资源 `/scale`。该 autoscaling/v1.Scale 对象作为有效负载发送 /scale。

要启用 scale 子资源，CustomResourceDefinition 中需要定义以下值。

* SpecReplicasPath 在与之对应的自定义资源中定义 JSONPath Scale.Spec.Replicas。这是一个必需的值。.spec 只允许使用带点符号的 JSONPaths 。如果 SpecReplicasPath 自定义资源中没有值，则 /scale 子资源将在GET上返回错误。

* StatusReplicasPath 在与之对应的自定义资源中定义 JSONPath Scale.Status.Replicas。这是一个必需的值。.stutus 只允许使用带点符号的 JSONPaths 。如果 StatusReplicasPath 自定义资源中没有值，则子资源 /scale 中的状态副本值将默认为 0。

* LabelSelectorPath在与之对应的自定义资源中定义 JSONPath Scale.Status.Selector。这是一个可选值。必须将其设置为与 HPA 一起使用。.status 只允许使用带点符号的 JSONPaths 。如果 LabelSelectorPath 自定义资源中没有值，则子资源 /scale 中的状态选择器值将默认为空字符串。

在以下示例中，启用了status 和 scale 子资源。

将以下内容保存到`redis-cluster-crd.yaml`并创建 `kubectl apply -f redis-cluster-crd.yaml`：

```yaml
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: redisclusters.redis.middleware.hc.cn
spec:
  group: redis.middleware.hc.cn
  versions:
    - name: v1alpha1
      # Each version can be enabled/disabled by Served flag.
      served: true
      # One and only one version must be marked as the storage version.
      storage: true
  scope: Namespaced
  names:
    kind: RedisCluster
    singular: rediscluster
    listKind: RedisClusterList
    plural: redisclusters
    shortNames:
    - rec
    # 执行kubectl get all时会查到pod、service、该crd等属于all categories的资源对象
    categories:
    - all
  subresources:
    # status enables the status subresource.
    status: {}
    scale:
      # specReplicasPath defines the JSONPath inside of a custom resource that corresponds to Scale.Spec.Replicas.
      specReplicasPath: .spec.replicas
      # statusReplicasPath defines the JSONPath inside of a custom resource that corresponds to Scale.Status.Replicas.
      statusReplicasPath: .status.replicas
      # labelSelectorPath defines the JSONPath inside of a custom resource that corresponds to Scale.Status.Selector.
      labelSelectorPath: .status.labelSelector
```

创建 CustomResourceDefinition 对象后，您可以创建自定义对象。

如果您将以下 YAML 保存到 `redis-cluster-cr.yaml`：

```yaml
apiVersion: redis.middleware.hc.cn/v1alpha1
kind: RedisCluster
metadata: 
  name: example000-redis-cluster
  namespace: kube-system
spec:
  # 代表redis集群的个数
  replicas: 6
  # 代表是否进入维修状态
  pause: true
  repository: library/redis
  # 镜像版本，便于后续多版本特化支持
  version: 3.2.6
  #redis集群升级策略
  updateStrategy:
    # 升级类型为AutoReceive（自动分配,不用AssignStrategies）, AssignReceive（指定值分配，需要用AssignStrategies）
    type: AssignReceive
    pipeline: "100"
    assignStrategies:
       - 
        slots: 2000
        fromReplicas: nodeId1
       - 
        # 从nodeId3,nodeId4一共分配1000个卡槽
        slots: 1000 
        # 多个nodeId用逗号分隔
        fromReplicas: nodeId3,nodeId4
  # redis 实例配置详情
  pod:
    # 配置文件模板名
  - configmap: example000-redis-cluster-config
    # 监控镜像
    monitorImage: redis-exporter:v1
    # 初始化镜像
    initImage: redis-init:v1
    # 中间件容器镜像
    middlewareImage: redis-trib:3.2.6
```

并创建它：

```shell
kubectl create -f redis-cluster-cr.yaml
```

然后在以下位置创建新的命名空间 RESTful API 端点：

```
/apis/redis.middleware.hc.cn/v1alpha1/namespaces/kube-system/redisclusters/example000-redis-cluster/status
```

和

```shell
/apis/redis.middleware.hc.cn/v1alpha1/namespaces/kube-system/redisclusters/example000-redis-cluster/scale
```

可以使用该 `kubectl scale` 命令缩放自定义资源。例如，以上创建的自定义资源的的 `.spec.replicas` 设置为 10：

```shell
# kubectl get rec --all-namespaces
NAMESPACE     NAME                       DESIRED   PAUSE   AGE
kube-system   example000-redis-cluster   6         true    10h

# kubectl scale --replicas=10 rec/example000-redis-cluster -nkube-system
rediscluster.redis.middleware.hc.cn/example000-redis-cluster scaled

# kubectl get rec --all-namespaces
NAMESPACE     NAME                       DESIRED   PAUSE   AGE
kube-system   example000-redis-cluster   10        true    10h

# kubectl get rec example000-redis-cluster -n kube-system -o jsonpath='{.spec.replicas}'
10
```



## 打印其他列

从 Kubernetes 1.11 开始，kubectl 使用服务器端打印。服务器决定 `kubectl get` 命令显示哪些列。您可以使用 CustomResourceDefinition 自定义这些列。下面的示例将输出 `Spec`、`Replicas` 和 `Age` 列。

1. 将 CustomResourceDefinition保存到 `redis-cluster-crd.yaml`。

   ```yaml
   apiVersion: apiextensions.k8s.io/v1beta1
   kind: CustomResourceDefinition
   metadata:
     name: redisclusters.redis.middleware.hc.cn
   spec:
     group: redis.middleware.hc.cn
     versions:
       - name: v1alpha1
         # Each version can be enabled/disabled by Served flag.
         served: true
         # One and only one version must be marked as the storage version.
         storage: true
     scope: Namespaced
     names:
       kind: RedisCluster
       singular: rediscluster
       listKind: RedisClusterList
       plural: redisclusters
       shortNames:
       - rec
       # 执行kubectl get all时会查到pod、service、该crd等属于all categories的资源对象
       categories:
       - all
     additionalPrinterColumns:
     - name: DESIRED
       type: integer
       description: The number of statefulset managed by the this redisCluster
       JSONPath: .spec.replicas
       # boolean,date,integer,number,string
     - name: PAUSE
       type: boolean
       description: Whether this redisCluster's grandson (pod) will not be managed by statefulset
       JSONPath: .spec.pause
   ```

2. 创建 CustomResourceDefinition：

   ```
   kubectl create -f redis-cluster-crd.yaml
   ```

3. 使用上面创建的 `redis-cluster-cr.yaml` 实例。

4. 调用服务器端打印：

   ```
   kubectl get rec --all-namespaces
   ```

   请注意 `NAME`、`NAMESPACE`, `DESIRED`、`PAUSE` 和 `AGE` 在输出列，并且都被转成了大写字母：

   ```
   [root@master-192 redis-container]# kubectl get rec --all-namespaces
   NAMESPACE     NAME                       DESIRED   PAUSE   AGE
   kube-system   example000-redis-cluster   6         true    10h
   ```

   `NAME`和`NAMESPACE` 列是隐含的，不需要在 CustomResourceDefinition 中定义。



## operator中应用该特性

在golang编写的operator代码中创建该结构体：

```go
//创建CRD
func CreateRedisClusterCRD(extensionCRClient *extensionsclient.Clientset) error {
	//add CustomResourceValidation due to guarantee redis operator work normally
	labelSelectorPath := ".status.labelSelector"
	replicasMinimum := float64(0)
	replicasMaximum := float64(50)
	replicasMultipleOf := float64(2)
	slotsMinimum := float64(1)
	slotsMaximum := float64(16384)
	assignStr := "AssignReceive"
	autoStr := "AutoReceive"
	assignJson, _ := json.Marshal(assignStr)
	autoJson, _ := json.Marshal(autoStr)

	crd := &v1beta1.CustomResourceDefinition{
		ObjectMeta: metav1.ObjectMeta{
			Name: "redisclusters." + v1alpha1.SchemeGroupVersion.Group,
		},
		Spec: v1beta1.CustomResourceDefinitionSpec{
			Group:   v1alpha1.SchemeGroupVersion.Group,
			Versions: []v1beta1.CustomResourceDefinitionVersion {
				{
					// Served is a flag enabling/disabling this version from being served via REST APIs
					Served: true,
					Name: v1alpha1.SchemeGroupVersion.Version,
					// Storage flags the version as storage version. There must be exactly one flagged as storage version
					Storage: true,
				},
			},
			Scope:   v1beta1.NamespaceScoped,
			Names: v1beta1.CustomResourceDefinitionNames{
				Kind:       "RedisCluster",
				ListKind:   "RedisClusterList",
				Plural:     "redisclusters",
				Singular:   "rediscluster",
				ShortNames: []string{"rec"},
				Categories: []string{"all"},
			},
			Subresources: &v1beta1.CustomResourceSubresources {
				Status: &v1beta1.CustomResourceSubresourceStatus {},
				Scale: &v1beta1.CustomResourceSubresourceScale {
					SpecReplicasPath: ".spec.replicas",
					StatusReplicasPath: ".status.replicas",
					LabelSelectorPath: &labelSelectorPath,
				},
			},
			AdditionalPrinterColumns: []v1beta1.CustomResourceColumnDefinition{
				{
					Name: "DESIRED",
					Type: "integer",
					Description: "The number of statefulset managed by the this redisCluster",
					JSONPath: ".spec.replicas",
				},
				{
					Name: "PAUSE",
					Type: "boolean",
					Description: "Whether this redisCluster's grandson (pod) will not be managed by statefulset",
					JSONPath: ".spec.pause",
				},
				{
					Name: "AGE",
					Type: "date",
					JSONPath: ".metadata.creationTimestamp",
				},
			},
			Validation: &v1beta1.CustomResourceValidation {
				OpenAPIV3Schema: &v1beta1.JSONSchemaProps {
					Properties: map[string]v1beta1.JSONSchemaProps {
						"spec": {
							Required: []string{"replicas", "repository", "version"},
							Properties: map[string]v1beta1.JSONSchemaProps{
								"pause": {
									Type: "boolean",
								},
								"replicas": {
									Type:       "integer",
									Minimum:    &replicasMinimum,
									Maximum:    &replicasMaximum,
									MultipleOf: &replicasMultipleOf,
								},
								"updateStrategy": {
									Type: "object",
									Properties: map[string]v1beta1.JSONSchemaProps{
										"type": {
											Type: "string",
											Enum: []v1beta1.JSON {
												{
                                                    //这里必须是JSON格式的字符串
													Raw: assignJson,
												},
												{
													Raw: autoJson,
												},
											},
										},
										"pipeline": {
											Type:    "string",
											Pattern: `^([1-9][0-9]*){1,3}$`,
										},
										"assignStrategies": {
											Type: "array",
											Items: &v1beta1.JSONSchemaPropsOrArray{
												Schema: &v1beta1.JSONSchemaProps{
													Type: "object",
													Properties: map[string]v1beta1.JSONSchemaProps{
														"slots": {
															Type:    "integer",
															Minimum: &slotsMinimum,
															Maximum: &slotsMaximum,
														},
														"fromReplicas": {
															Type:    "string",
															Pattern: `^[a-z0-9,]{3,}$`,
														},
													},
												},
											},
										},
									},
								},
							},
						},
						"pod": {
							Type: "array",
							Items: &v1beta1.JSONSchemaPropsOrArray {
								Schema: &v1beta1.JSONSchemaProps {
									Type: "object",
									Required: []string{"replicas", "repository", "version"},
									Properties: map[string]v1beta1.JSONSchemaProps{
										"configmap": {
											Type: "string",
										},
										"monitorImage": {
											Type: "string",
										},
										"initImage": {
											Type: "string",
										},
										"middlewareImage": {
											Type: "string",
										},
									},
								},
							},
						},
					},
				},
			},
		},
	}
	_, err := extensionCRClient.ApiextensionsV1beta1().CustomResourceDefinitions().Create(crd)
	return err
}

```



## 参考

官方Extend the Kubernetes API with CustomResourceDefinitions：

https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/

feature-gates参数说明：

https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/

CustomResourceDefinition中文文档：

https://kubernetes.feisky.xyz/cha-jian-kuo-zhan/api/customresourcedefinition

swagger和openAPI: 数据类型：

https://www.breakyizhan.com/swagger/2969.html

正则表达式：

https://www.cnblogs.com/afarmer/archive/2011/08/29/2158860.html
