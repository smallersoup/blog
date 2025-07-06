---
title: k8s自定义资源类型代码自动生成
date: '2019-10-18 13:29:09'
updated: '2019-10-18 13:29:09'
tags: [kubernetes]
permalink: /201910181329k8s
---

## 正文


用以下命令生成代码：
```sh
./generate-groups.sh all "github.com/openshift-evangelist/crd-code-generation/pkg/client" "github.com/openshift-evangelist/crd-code-generation/pkg/apis" "ingressgroup:v1"
```
### 第一个报错
生成代码报错：
```sh
Generating deepcopy funcs
F0910 19:18:35.552948   12153 main.go:82] Error: Failed making a parser: unable to add directory "github.com/openshift-evangelist/crd-code-generation/pkg/client": unable to import "github.com/asdfsx/getkubeconfig/pkg/apis/example/v1": cannot find package "github.com/openshift-evangelist/crd-code-generation/pkg/client" in any of:
        D:/Program Files/Go/go103/src/github.com/openshift-evangelist/crd-code-generation/pkg/client (from $GOROOT)
        D:/SoftwareAndProgram/program/Go/Development/src/github.com/openshift-evangelist/crd-code-generation/pkg/client (from $GOPATH)
```
这个问题可以参考[issue](https://github.com/kubernetes/code-generator/issues/55)
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/3e85f552280469d10d0c15bffe25a066.png)

可以参考这个文章：
https://medium.com/@trstringer/create-kubernetes-controllers-for-core-and-custom-resources-62fc35ad64a3

由于该链接国内访问比较困难，故转载到了这里：
[https://www.jianshu.com/p/dcfe6eac4152](https://www.jianshu.com/p/dcfe6eac4152)


### 第二个报错：
```sh
Generating deepcopy funcs
F1104 02:57:44.419529      35 main.go:82] Error: Failed executing generator: some packages had errors:
type "k8s.io/apimachinery/pkg/runtime.Object" in k8s:deepcopy-gen:interfaces tag of type k8s.io/apimachinery/pkg/runtime.Object is not an interface, but: ""
goroutine 1 [running]:
```
这个报错是因为k8s.io/apimachinery这个包目录结构不对，放到vendor目录下找不到，必须放到$GOPATH下的src/k8s.io/apimachinery，具体参考[issue](https://github.com/kubernetes/code-generator/issues/21)
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/50de8ae6550e0e380954bbfb58ee2a3e.png)

> 我解决了这个问题 。这不起作用，除非k8s.io/apimachinery在GOPATH中，如果它只是在vendor目录下，那么deepcopy无法找到它。至少，这需要在某处记录。如果在vendor目录下也能正常工作，那将会很棒。

目录结构如下：
$GOPATH/src
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/680df73958cfdc4a49e6fa0124e672c4.png)

$GOPATH/src/github.com/
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/1dbf78a43881c04ec67bc77955a84201.png)

### 第三个报错
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/185c6b7818fa5f451e3248adfc837d2d.png)
```sh
Generating deepcopy funcs
F0221 09:54:08.335328   26316 main.go:82] Error: Failed executing generator: som                                          e packages had errors:
errors in package "github.com/openshift-evangelist/crd-code-generation/pkg/apis/                                          ingressgroup/v1":
unable to format file "D:\\SoftwareAndProgram\\program\\Go\\Development\\src\\gi                                          thub.com\\openshift-evangelist\\crd-code-generation\\pkg\\apis\\ingressgroup\\v1                                          \\zz_generated.deepcopy.go" (The filename, directory name, or volume label synta                                          x is incorrect.).
```
windows上执行报这个错，需要在linux上执行generate-groups.sh 脚本。

### 最终生成如下：
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/e77908ca30379d872bc61040d05f0a21.png)

```sh
[root@master-192 code-generator]# dos2unix generate-groups.sh 
dos2unix: converting file generate-groups.sh to Unix format ...
[root@master-192 code-generator]# ./generate-groups.sh all "github.com/openshift-evangelist/crd-code-generation/pkg/client" "github.com/openshift-evangelist/crd-code-generation/pkg/apis" "ingressgroup:v1"
Generating deepcopy funcs
Generating clientset for ingressgroup:v1 at github.com/openshift-evangelist/crd-code-generation/pkg/client/clientset
Generating listers for ingressgroup:v1 at github.com/openshift-evangelist/crd-code-generation/pkg/client/listers
Generating informers for ingressgroup:v1 at github.com/openshift-evangelist/crd-code-generation/pkg/client/informers
```
最终生成目录结构如下：
```sh
[root@master-192 crd-code-generation]# pwd
/root/Work/programmer/go/gopath/src/github.com/openshift-evangelist/crd-code-generation
[root@master-192 crd-code-generation]# tree
.
└── pkg
    ├── apis
    │   └── ingressgroup
    │       ├── register.go
    │       └── v1
    │           ├── doc.go
    │           ├── register.go
    │           ├── types.go
    │           └── zz_generated.deepcopy.go
    └── client
        ├── clientset
        │   └── versioned
        │       ├── clientset.go
        │       ├── doc.go
        │       ├── fake
        │       │   ├── clientset_generated.go
        │       │   ├── doc.go
        │       │   └── register.go
        │       ├── scheme
        │       │   ├── doc.go
        │       │   └── register.go
        │       └── typed
        │           └── ingressgroup
        │               └── v1
        │                   ├── doc.go
        │                   ├── fake
        │                   │   ├── doc.go
        │                   │   ├── fake_ingressgroup_client.go
        │                   │   └── fake_ingressgroup.go
        │                   ├── generated_expansion.go
        │                   ├── ingressgroup_client.go
        │                   └── ingressgroup.go
        ├── informers
        │   └── externalversions
        │       ├── factory.go
        │       ├── generic.go
        │       ├── ingressgroup
        │       │   ├── interface.go
        │       │   └── v1
        │       │       ├── ingressgroup.go
        │       │       └── interface.go
        │       └── internalinterfaces
        │           └── factory_interfaces.go
        └── listers
            └── ingressgroup
                └── v1
                    ├── expansion_generated.go
                    └── ingressgroup.go
```


---------

