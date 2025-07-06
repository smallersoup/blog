---
title: 一次写shell脚本的经历记录——特殊字符惹的祸
date: '2019-10-18 13:33:00'
updated: '2019-10-18 13:33:00'
tags: [shell]
permalink: /201910181332shell
---




redis在容器化的过程中，涉及到纵向扩pod实例cpu、内存以及redis实例的maxmemory值，statefulset管理的pod需要重启。所以把redis集群的状态检查放到了健康检查中，依赖statefulset的原生能力（pod实例ready后才重启下一个，ready后endpoints controller将pod信息更新到endpoints资源对象中）,而没有在redis operator中写逻辑去判断。



需要用redis-cli -h {redis实例IP} ping查看redis是否正常，同时用redis-cli -c -h {redis实例IP} -a {redis密码} cluster info输出的信息解析cluster_state的值是否为ok，以及cluster_known_nodes的值是否为1，判断redis集群是否正常；



如果redis集群刚创建，cluster_known_nodes为1，cluster_state为fail;

如果redis集群为纵向扩容(扩CPU、内存)升级重启，cluster_known_nodes不为1，cluster_state为ok时才认为集群正常，才能重启下一个pod。



因为涉及到字符串相等判断，所以用以下这样判断：
```shell
if [ "$cluster_known_nodes"x = "1"x  ]; then
.....
fi
```

但是判断一直有问题，如下图，在$a后面加个x，会变为在开头覆盖式的加a，结果就是判断结果不相等。
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190528235957739.png)
把redis-cli -c -h {redis实例IP} -a {redis密码} cluster info执行的结果重定向到文件里。



vi 1.txt查看文件，在vi里用set ff命令查看文件格式为unix，但是文件每一行后面都有一个^M的特殊字符，这就是问题所在了。
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190529000010121.png)

最主要是通过cat都看不出来特殊字符的存在。
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190529000018493.png)

手动把^M特殊字符删掉就好了。
![在这里插入图片描述](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20190529000024884.png)



网上说^M是windows格式文本文件的换行符\r\n，可以用dos2unix命令转为unix格式。但是执行cluster info命令全程在linux中操作，而且重定向到文件中set ff命令看到也是unix格式。这点还是很费解。



先用sed命令将^M换掉，试了sed  's/^M//g'没有用，所以选择用sed 's?\r??g'替换，最终脚本如下。



if语句的[[]]需要用bash执行，用sh执行会报错[[: not found
```shell
#!/bin/bash

#需要用redis-cli -h {redis实例IP} ping查看redis是否正常
#用redis-cli -c -h {redis实例IP} -a {redis密码} cluster info输出
#的信息解析cluster_state的值是否为ok，以及cluster_known_nodes的值是
#否为1，判断redis集群是否正常；如果redis集群刚创建，cluster_known_nodes
#为1，cluster_state为fail;如果redis集群为纵向扩容(扩CPU、内存)升级重启
#cluster_known_nodes不为1，cluster_state为ok时才认为集群正常，才能重启
#下一个pod，改健康检查脚本旨在维护升级时redis集群状态，不在operator中维护
# 利用好statefulset一个实例ready后重启下一个pod的特性

pingres=$(redis-cli -h $(hostname) ping)

# cluster_state:ok
# cluster_slots_assigned:16384
# cluster_slots_ok:16384      
# cluster_slots_pfail:0        
# cluster_slots_fail:0        
# cluster_known_nodes:6        
# cluster_size:3                
# cluster_current_epoch:15      
# cluster_my_epoch:12          
# cluster_stats_messages_sent:270782059
# cluster_stats_messages_received:270732696
pingres=$(echo "${pingres}" | sed 's?\r??g')
if [[ "$pingres"x = "PONG"x ]]; then
    clusterinfo=$(redis-cli -c -h ${PODIP} cluster info)
    # redis-cli -c -h ${PODIP} cluster info output info include ^M(win \n\r) char lead to error, so use sed 's?\r??g'
    clusterknownnodes=$(echo "${clusterinfo}" | grep cluster_known_nodes | sed 's?\r??g' | awk -F ':' '{print $2}')
    clusterstate=$(echo "${clusterinfo}" | grep cluster_state | sed 's?\r??g' | awk -F ':' '{print $2}')

    echo "clusterknownnodes: ${clusterknownnodes} --- clusterstate: ${clusterstate}"
    # [[ need run this script use /bin/bash instead of /bin/sh
    # if语句的[[]]需要用bash执行，用sh执行会报错[[: not found
    if [[ "${clusterknownnodes}"x = "1"x && "${clusterstate}"x = "ok"x ]]; then
        echo "--1--"
        exit 0
    elif [[ "${clusterknownnodes}"x != "1"x && "${clusterstate}"x = "ok"x ]]; then
        echo "--2--"
        exit 0
    # create redis cluster
    elif [[ "${clusterknownnodes}"x = "1"x && "${clusterstate}"x != "ok"x ]]; then
        echo "--3--"
        exit 0
    elif [[ "${clusterknownnodes}"x != "1"x && "${clusterstate}"x != "ok"x ]]; then
        echo "--4--"
        exit 1
    else
        echo "--5--"
        exit 1
    fi
else
    exit 1
fi
```



一般这种怪异的问题都是脚本里有特殊字符造成的，可以在脚本中set list显示特殊字符。当然windows上编辑过的脚本在linux上运行一般dos2unix test.sh这样转换一下最好，免的遇到麻烦。



## 参考：

shell中括号的特殊用法 linux if多条件判断
https://www.cnblogs.com/jjzd/p/6397495.html



运行shell脚本时报错"[[ : not found"解决方法
https://www.cnblogs.com/han-1034683568/p/7211392.html




--------
