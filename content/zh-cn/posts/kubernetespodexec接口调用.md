---
title: kubernetes pod exec接口调用
date: '2019-10-18 13:30:04'
updated: '2019-10-18 13:30:04'
tags: [kubernetes]
permalink: /201910181329kubernetes
---

## 正文

一般生产环境上由于网络安全策略，大多数端口是不能为集群外部访问的。多个集群之间一般都是通过k8s的ApiServer组件提供的接口通信，如https://192.168.1.101:6443。所以在做云平台时，集群管理平台（雅称：观云台）需要操作其他集群的资源对象时，必然也得通过ApiServer。

k8s负载均衡器组件ingress-nginx-controller中集成的nginx，当集群ingress、tcp configmaps、udp configmaps等资源发生变化时，ingress-nginx-controller会根据这些资源最新配置，并根据提前设定好的nginx.tmpl模板（nginx配置文件nginx.conf由该模板生成）生成最新的nginx.conf配置，并自动进行nginx -s reload操作。
最近做的一个需求，部分负载均衡器可以在页面上由运维人员自动配置，通过nginx的server、map配置。根据请求头的不同将流量分配到不同的服务。可以参考[nginx map配置根据请求头不同分配流量到不同后端服务](https://www.jianshu.com/p/0897e16f7ea2)

配置后需要在观云台上手动reload负载均衡器，以使配置生效。这就涉及到从观云台去操作多集群的负载均衡器。

通过修改ingress-nginx-controller源码提供接口reload方案，由于网络规则限制肯定行不通；
只有6443端口可以走。能不能像操作集群内资源一样去操作其他集群资源？

1、kubectl命令其实对应的就是调用apiserver去操作资源，在集群内我们都知道可以用以下命令：
```sh
kubectl exec -ti ingress-nginx-abab121 -nkube-system -- nginx -s reload
```
那么从A集群去操作B集群，假设B的ApiServer地址为：https://192.168.1.101:6443，Bearer token为212k1jj1jak12k1kjaeeba，则命令如下：
```sh
kubectl exec -ti ingress-nginx-abab121 -nkube-system --server=https://192.168.1.101:6443 --token=212k1jj1jak12k1kjaeeba --insecure-skip-tls-verify=true -- nginx -s reload
```
通过查看kubelet的源代码，可以发现$GOPATH\src\k8s.io\kubernetes\pkg\kubelet\server\server.go的InstallDebuggingHandlers方法中注册了exec、attach、portForward等接口，同时kubelet的内部接口通过api server对外提供服务，所以对API server的这些接口调用，可以直接访问到kubelet，即client -->> API server --> kubelet

2、可以用curl命令调用如下：
```sh
curl -k \
     -H "Connection: Upgrade" \
	 -H "Authorization: Bearer 212k1jj1jak12k1kjaeeba" \
	 -H "Upgrade: websocket" \
	 -H "Sec-Websocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
	 -H "Sec-Websocket-Version: 13" \
"https://192.168.26.19:6443/api/v1/namespaces/liano/pods/nginx/exec?command=ls&stdin=true&stout=true&tty=true"
```
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/imgconvert-csdnimg/79e732b139c04b0359d7df701ce92435.png)

3、kubernetes开源社区维护了各种语言版本与k8s apiserver交互的client库，比如java库地址如下：
https://github.com/kubernetes-client/java
其中提供了调用pod的exec接口代码示例：
https://github.com/kubernetes-client/java/blob/master/examples/src/main/java/io/kubernetes/client/examples/ExecExample.java
需要先依赖：
```xml
<dependency>
    <groupId>io.kubernetes</groupId>
    <artifactId>client-java</artifactId>
    <version>4.0.0</version>
    <scope>compile</scope>
</dependency>
````
然后根据apiserver地址和Bearer token构建client，到访问pod exec接口进行nginx -s reload代码示例如下：
```java
package com.liano.api.test;

import com.alibaba.fastjson.JSONObject;
import com.google.common.base.Preconditions;
import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.Exec;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.credentials.AccessTokenAuthentication;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;

/**
 * @program: k8s-mars
 * @description: ExecKubelet
 * @author: liano
 * @create: 2019-03-06 15:10
 **/

public class ExecKubeletDemo {
    public static void main(String[] args) throws IOException, ApiException, InterruptedException {
        new ExecKubeletDemo().execNginxReload();
    }

    private void execNginxReload() throws InterruptedException, ApiException, IOException {

		//apiServer地址和Bbearer token方式认证
        ApiClient client = new ClientBuilder().setBasePath("https://10.10.101.60:6443").setVerifyingSsl(false)
                .setAuthentication(new AccessTokenAuthentication("33095a7b86a7a3462ea45a1410624b")).build();
//        client.setDebugging(true);

        Configuration.setDefaultApiClient(client);

        JSONObject res = process("nginx-97ccd777-xk9pw", "kube-system");
        System.out.println(JSONObject.toJSONString(res));
    }

    private JSONObject process(String podName, String namespace) throws IOException, ApiException, InterruptedException {
        Exec exec = new Exec();
        // final Process proc = exec.exec("default", "nginx-4217019353-k5sn9", new String[]
        //   {"sh", "-c", "echo foo"}, true, tty);
        String[] commands = new String[]{"nginx", "-s", "reload"};
        final Process proc = exec.exec(namespace, podName, commands, true, true);

        JSONObject res = new JSONObject();

        Thread out = new Thread(
                new Runnable() {
                    public void run() {
                        String copy = copy(proc.getInputStream());
                        res.put("data", copy);
                    }
                });
        out.start();

        proc.waitFor();

        out.join();

        proc.destroy();

        if (proc.exitValue() != 0) {
            res.put("success", false);
        } else {
            res.put("success", true);
        }

        return res;
    }
	
	private String copy(InputStream from) {
        Preconditions.checkNotNull(from);
        BufferedReader in = null;
        Reader reader = null;
        StringBuilder sb = new StringBuilder();
        try {
            reader = new InputStreamReader(from);
            in = new BufferedReader(reader);
            String line;
            while ((line = in.readLine()) != null) {
                sb.append(line);
            }
        } catch (Exception e) {
            System.out.println(e);
        } finally {
            try {
                if (from != null) {
                    from.close();
                }

                if (reader != null) {
                    reader.close();
                }

                if (in != null) {
                    in.close();
                }
            } catch (Exception e) {
                System.out.println(e);
            }
        }

        return sb.toString();
    }
}
```
从io.kubernetes.client.Exec源码中可以看到，需求通过 HTTP/1.1 协议的101状态码进行握手进一步建立websocket。websocket是一种在单个TCP连接上进行全双工通信的协议， 是独立的、创建在 TCP 上的协议。为了创建Websocket连接，需要通过客户端发出请求，之后服务器进行回应，这个过程通常称为“握手”（handshaking）。

一个典型的Websocket握手请求如下：

```sh
GET / HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Host: example.com
Origin: http://example.com
Sec-WebSocket-Key: sN9cRrP/n9NdMgdcy2VJFQ==
Sec-WebSocket-Version: 13
```

服务器回应
 ```sh
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: fFBooB7FAkLlXgRSz0BT3v4hq5s=
Sec-WebSocket-Location: ws://example.com/
```

字段说明
```sh
Connection必须设置Upgrade，表示客户端希望连接升级。
Upgrade字段必须设置Websocket，表示希望升级到Websocket协议。
Sec-WebSocket-Key是随机的字符串，服务器端会用这些数据来构造出一个SHA-1的信息摘要。把“Sec-WebSocket-Key”加上一个特殊字符串“258EAFA5-E914-47DA-95CA-C5AB0DC85B11”，然后计算SHA-1摘要，之后进行BASE-64编码，将结果做为“Sec-WebSocket-Accept”头的值，返回给客户端。如此操作，可以尽量避免普通HTTP请求被误认为Websocket协议。
Sec-WebSocket-Version 表示支持的Websocket版本。RFC6455要求使用的版本是13，之前草案的版本均应当弃用。
Origin字段是可选的，通常用来表示在浏览器中发起此Websocket连接所在的页面，类似于Referer。但是，与Referer不同的是，Origin只包含了协议和主机名称。
其他一些定义在HTTP协议中的字段，如Cookie等，也可以在Websocket中使用。
```






---------
