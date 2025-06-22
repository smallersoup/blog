title: nginx map配置根据请求头不同分配流量到不同后端服务
date: '2019-10-18 13:28:31'
updated: '2019-10-18 13:28:31'
tags: [nginx]
permalink: /201910181328nginx
---

## 正文

最近在做一个需求开发：根据请求后的不同，nginx将请求分发到不同的后端服务；需要修改kubernetes的ingress-nginx-controller的源码，调试的时候遇到了挺多问题，写出来，有需要的老铁可以参考。具体方案就不说了，只说一下nginx配置这一块。

首先贴出组件版本：
ingress-nginx-controller的版本为0.9-beta.18，可以在github上找到开源的项目源码：

nginx map配置根据请求头不同分配流量到不同后端服务
nginx版本为：nginx version: nginx/1.13.7

## map配置的一个报错：
nginx.conf文件部分如下：
```conf
http {
	
    include /etc/nginx/conf.d/server-map.d/*-map.conf;
    include /etc/nginx/conf.d/*-upstream.conf;
    include /etc/nginx/conf.d/server-map.d/*-server.conf;

	....

    map_hash_bucket_size 64;

	....
}
```
在/etc/nginx/conf.d/server-map.d/目录下的flow-ppp-map.conf：
```conf
map $http_x_group_env $svc_upstream {
	default zxl-test-splitflow-old-version;
	~*old zxl-test-splitflow-old-version;
	~*new zxl-test-splitflow-new-version;
}
```

flow-ppp-server.conf
```conf
server {
	listen 8998;
	server_name aa.hc.harmonycloud.cn;
	location /testdemo/test {
		proxy_pass http://$svc_upstream;
	}
}
```

ingressgroup-upstream.conf
```conf
upstream zxl-test-splitflow-old-version {
	server 10.168.173.29:8080 max_fails=0 fail_timeout=0;
}

upstream zxl-test-splitflow-new-version {
	server 10.168.177.171:8080 max_fails=0 fail_timeout=0;
}
```
当nginx -tc /etc/nginx/nginx.conf测试配置正确与否时报错如下：
```sh
Error: exit status 1
nginx: [emerg] "map_hash_bucket_size" directive is duplicate in /etc/nginx/nginx.conf:60
nginx: configuration file c test failed
```

![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWY2M2FhYmQ1ZmEyM2U1NGIucG5n?x-oss-process=image/format,png)

### 解决：

这是因为首次调用map时会隐式设置map_hash_bucket_size，即在nginx中map后写map_hash_bucket_size相当于设置了两次map_hash_bucket_size，如：
```conf
http {
    ...
    map $status $_status {
        default 42;
    }
    map_hash_bucket_size 64;
    ...
}
```
因此可以在map之前设置它，如下所示。
```conf
http {
    map_hash_bucket_size 64;
    ...
    map $status $_status {
        default 42;
    }
    ...
}
```
所以include map配置也应该放到设置map_hash_bucket_size之后：
```conf
http {
	...

    map_hash_bucket_size 64;

	...
	
	include /etc/nginx/conf.d/server-map.d/*-map.conf;
    include /etc/nginx/conf.d/*-upstream.conf;
    include /etc/nginx/conf.d/server-map.d/*-server.conf;
}
```

## map配置说明：

通过上面的include三个配置文件，最终对nginx生效的配置应该是这样的：

```conf
http {
	...

    map_hash_bucket_size 64;

	...
	
	map $http_x_group_env $svc_upstream {
		default zxl-test-splitflow-old-version;
		~*old zxl-test-splitflow-old-version;
		~*new zxl-test-splitflow-new-version;
	}
	
	
    upstream zxl-test-splitflow-old-version {
		server 10.168.173.29:8080 max_fails=0 fail_timeout=0;
	}

	upstream zxl-test-splitflow-new-version {
		server 10.168.177.171:8080 max_fails=0 fail_timeout=0;
	}
	
    server {
		listen 8998;
		server_name aa.hc.harmonycloud.cn;
		location /testdemo/test {
			proxy_pass http://$svc_upstream;
		}
	}
}
```
当在电脑上hosts文件里配置了aa.hc.harmonycloud.cn域名解析后，访问http://aa.hc.harmonycloud.cn:8998/testdemo/test时(即server的server_name和listen、location的配置)，nginx将会把请求转发到http://\$svc_upstream，这个$svc_upstream具体是什么，就是通过map配置来赋值的。这里map配置如下：
```conf
map $http_x_group_env $svc_upstream {
		default zxl-test-splitflow-old-version;
		~*old zxl-test-splitflow-old-version;
		~*new zxl-test-splitflow-new-version;
}
```
其中\$http_x_group_env可以是nginx内置变量，也可以是自定义的header的key、请求参数名；\$svc_upstream即为自定义变量名。这里的配置含义为：当请求头里的x-group-env的值old时，\$svc_upstream被赋值为zxl-test-splitflow-old-version；当请求头里的x-group-env的值new时，\$svc_upstream被赋值为zxl-test-splitflow-new-version；默认赋值为zxl-test-splitflow-old-version；
（其中正则表达式如果以 “~” 开头，表示这个正则表达式对大小写敏感。以 “~*”开头，表示这个正则表达式对大小写不敏感）。而zxl-test-splitflow-new-version和zxl-test-splitflow-old-version表示两个upstream名称。

因此nginx将会把请求转发到http://\$svc_upstream，这里的$svc_upstream会被替换为upstream的名称，最终将得到upstream中的后端服务IP和Port。

注意：如果我们自定义header为X-Real-IP,通过第二个nginx获取该header时需要这样：$http_x_real_ip; (一律采用小写，而且前面多了个http_，且中间用_替换）

## 测试

当请求头里加x-group-env为new时，访问后端打印出的是I am new version
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTk0MmViMzQ3MzFiMmJlYTcucG5n?x-oss-process=image/format,png)

当请求头里加x-group-env为old时，访问后端打印出的是I am old version
![image.png](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTk2MGE2ZGNhMTU5NzFlOWMucG5n?x-oss-process=image/format,png)

最终通过请求头不同实现了将流量分配到不同的后端服务。

将请求头的key变为X-Group-Env，value变为OLD或者NEW也没关系：
![old](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTg0YTRiZGUxOThmNTgxMTkucG5n?x-oss-process=image/format,png)


![new](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTFlN2RkN2RhYmI0YTdhMzEucG5n?x-oss-process=image/format,png)








---------
