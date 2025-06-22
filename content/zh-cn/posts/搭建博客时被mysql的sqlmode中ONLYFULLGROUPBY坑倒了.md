title: 搭建博客时，被mysql的sql_mode中ONLY_FULL_GROUP_BY坑倒了
date: '2019-11-03 09:54:58'
updated: '2019-11-03 09:54:58'
tags: [mysql, blog]
permalink: /201911030954mysqlblog
---

## 1、背景
前两天在阿里云服务器上搭建了自己的博客，一切都很顺利，今天在点击归档按钮时，发现是报404。于是我把solo代码在本地运行起来，用本地的mysql数据库，看是否有同样的问题，结果是可以正常访问的。那就看看服务器上的solo日志呗，结果发现了以下报错：
```shell
Caused by: org.b3log.latke.repository.RepositoryException: java.sql.SQLSyntaxErrorException: Expression #20 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'solo.aa.oId' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by
```
原来，这个问题出现在MySQL5.7后版本上，默认的sql_mode值是这样的：
```shell
ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
```
那么sql_mode 有哪些配置？都代表什么意思？
## 2、sql_mode 配置解析
**ONLY_FULL_GROUP_BY** 

对于GROUP BY聚合操作，如果在SELECT中的列，没有在GROUP BY中出现，那么这个SQL是不合法的，因为列不在GROUP BY从句中。简而言之，就是SELECT后面接的列必须被GROUP BY后面接的列所包含。如：
```sql
select a,b from table group by a,b,c; (正确)
select a,b,c from table group by a,b; (错误)
```
这个配置会使得GROUP BY语句环境变得十分狭窄，所以一般都不加这个配置

* **NO_AUTO_VALUE_ON_ZERO** 

该值影响自增长列的插入。默认设置下，插入0或NULL代表生成下一个自增长值。（不信的可以试试，默认的sql_mode你在自增主键列设置为0，该字段会自动变为最新的自增值，效果和null一样），如果用户希望插入的值为0（不改变），该列又是自增长的，那么这个选项就有用了。

* **STRICT_TRANS_TABLES**

在该模式下，如果一个值不能插入到一个事务表中，则中断当前的操作，对非事务表不做限制。（InnoDB默认事务表，MyISAM默认非事务表；MySQL事务表支持将批处理当做一个完整的任务统一提交或回滚，即对包含在事务中的多条语句要么全执行，要么全部不执行。非事务表则不支持此种操作，批处理中的语句如果遇到错误，在错误前的语句执行成功，之后的则不执行；MySQL事务表有表锁与行锁非事务表则只有表锁）

* **NO_ZERO_IN_DATE**

在严格模式下，不允许日期和月份为零

* **NO_ZERO_DATE**

设置该值，mysql数据库不允许插入零日期，插入零日期会抛出错误而不是警告。

* **ERROR_FOR_DIVISION_BY_ZERO**

在INSERT或UPDATE过程中，如果数据被零除，则产生错误而非警告。如 果未给出该模式，那么数据被零除时MySQL返回NULL

* **NO_AUTO_CREATE_USER**

禁止GRANT创建密码为空的用户

* **NO_ENGINE_SUBSTITUTION**

如果需要的存储引擎被禁用或未编译，那么抛出错误。不设置此值时，用默认的存储引擎替代，并抛出一个异常

* **PIPES_AS_CONCAT**

将”||”视为字符串的连接操作符而非或运算符，这和Oracle数据库是一样的，也和字符串的拼接函数Concat相类似

* **ANSI_QUOTES**

启用ANSI_QUOTES后，不能用双引号来引用字符串，因为它被解释为识别符

---

## 3、测试
本地起一个数据库，先查看sql_mode模式：
```sql
mysql> select @@global.sql_mode;                
+--------------------------------------------+  
| @@global.sql_mode                          |  
+--------------------------------------------+  
| STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION |  
+--------------------------------------------+  
1 row in set (0.00 sec)                         
                                                
mysql> select @@session.sql_mode;               
+--------------------------------------------+  
| @@session.sql_mode                         |  
+--------------------------------------------+  
| STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION |  
+--------------------------------------------+  
1 row in set (0.00 sec)                         
```
创建一个测试的表：
```sql
mysql> CREATE TABLE IF NOT EXISTS `demo`(                       
    ->    `id` INT UNSIGNED AUTO_INCREMENT,                     
    ->    `rank` VARCHAR(100) NOT NULL,                         
    ->    `name` VARCHAR(40) NOT NULL,                          
    ->    `gender` TINYINT NOT NULL,                            
    ->    PRIMARY KEY ( `id` )                                  
    -> )ENGINE=InnoDB DEFAULT CHARSET=utf8;                     
Query OK, 0 rows affected (0.02 sec)                            
                                                                
mysql>                                                          
mysql> show tables;                                             
+----------------+                                              
| Tables_in_test |                                              
+----------------+                                              
| demo           |                                              
+----------------+                                              
1 row in set (0.00 sec)                                         
                                                                
mysql> desc demo;                                               
+--------+------------------+------+-----+---------+------------
| Field  | Type             | Null | Key | Default | Extra      
+--------+------------------+------+-----+---------+------------
| id     | int(10) unsigned | NO   | PRI | NULL    | auto_increm
| rank   | varchar(100)     | NO   |     | NULL    |            
| name   | varchar(40)      | NO   |     | NULL    |            
| gender | tinyint(4)       | NO   |     | NULL    |            
+--------+------------------+------+-----+---------+------------
4 rows in set (0.01 sec)                                        
```
插入测试数据：
```sql                                                              
mysql> insert into demo values(1, 'A', 'coderaction1', '20');   
Query OK, 1 row affected (0.01 sec)                             
                                                                
mysql> insert into demo values(2, 'B', 'coderaction2', '21');   
Query OK, 1 row affected (0.00 sec)                             
                                                                
mysql> insert into demo values(3, 'A', 'coderaction3', '22');   
Query OK, 1 row affected (0.00 sec)                             
                                                                
mysql> insert into demo values(4, 'C', 'coderaction4', '23');   
Query OK, 1 row affected (0.00 sec)                             
                                                                
mysql> insert into demo values(5, 'A', 'coderaction5', '21');   
Query OK, 1 row affected (0.00 sec)                             
                                                                
mysql> insert into demo values(6, 'C', 'coderaction6', '28');   
Query OK, 1 row affected (0.01 sec)                             
                                                                
mysql>                                                          
mysql> select * from demo;                                      
+----+------+--------------+--------+                           
| id | rank | name         | gender |                           
+----+------+--------------+--------+                           
|  1 | A    | coderaction1 |     20 |                           
|  2 | B    | coderaction2 |     21 |                           
|  3 | A    | coderaction3 |     22 |                           
|  4 | C    | coderaction4 |     23 |                           
|  5 | A    | coderaction5 |     21 |                           
|  6 | C    | coderaction6 |     28 |                           
+----+------+--------------+--------+                           
6 rows in set (0.00 sec)                                        
```
分别执行以下sql命令：
```sql                                                              
mysql> select count(id) from demo order by rank;                
+-----------+                                                   
| count(id) |                                                   
+-----------+                                                   
|         6 |                                                   
+-----------+                                                   
1 row in set (0.01 sec)                                         
                                                                
mysql> select count(id) from demo group by rank;                
+-----------+                                                   
| count(id) |                                                   
+-----------+                                                   
|         3 |                                                   
|         1 |                                                   
|         2 |                                                   
+-----------+                                                   
3 rows in set (0.00 sec)                                        
                                                                
mysql> select count(rank),id from demo group by rank;           
+-------------+----+                                            
| count(rank) | id |                                            
+-------------+----+                                            
|           3 |  1 |                                            
|           1 |  2 |                                            
|           2 |  4 |                                            
+-------------+----+                                            
3 rows in set (0.00 sec)                                        
                                                                     
mysql> select count(rank),id from demo group by id;             
+-------------+----+                                            
| count(rank) | id |                                            
+-------------+----+                                            
|           1 |  1 |                                            
|           1 |  2 |                                            
|           1 |  3 |                                            
|           1 |  4 |                                            
|           1 |  5 |                                            
|           1 |  6 |                                            
+-------------+----+                                            
6 rows in set (0.00 sec)                                        
                                                                
mysql>                                                          
```
可以看到上面四个sql都执行成功。

**修改sql_mode，临时修改sql_mode方式有两种，一种是设置当前会话连接的session级别的sql_mode，另一个是global级别的sql_mode。**

### session级别
先来看看session级别的sql_mode，设置方式有两种：
```sql
mysql> set session sql_mode='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> set @@session.sql_mode='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> select @@session.sql_mode;
+-------------------------------------------------------------------------------------------------------------------------------------------+
| @@session.sql_mode                                                                                                                        |
+-------------------------------------------------------------------------------------------------------------------------------------------+
| ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+-------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
设置session级别sql_mode，当前session级别查询到新的，下次重连后失效。

### global级别
再看看global级别的sql_mode，设置方式有两种：
```sql
mysql> set @@global.sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> select @@global.sql_mode;
+------------------------------------------------------------------------------------------------------------------------+
| @@global.sql_mode                                                                                                      |
+------------------------------------------------------------------------------------------------------------------------+
| STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
设置global级别sql_mode，当前session级别查询到还是旧的，所以执行命令时，还是按照旧配置。下次重连后利用新配置。

---

当我们设置完上面session级别的sql_mode，在其中加ONLY_FULL_GROUP_BY后，执行测试sql语句报错：
```sql
mysql> select count(rank),id from demo group by rank;                                                                                                         
ERROR 1055 (42000): Expression #2 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'test.demo.id' which is not functionally dependen
t on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by                                                                        
mysql> select count(rank),id from demo group by id;                                                                                                           
+-------------+----+                                                                                                                                          
| count(rank) | id |                                                                                                                                          
+-------------+----+                                                                                                                                          
|           1 |  1 |                                                                                                                                          
|           1 |  2 |                                                                                                                                          
|           1 |  3 |                                                                                                                                          
|           1 |  4 |                                                                                                                                          
|           1 |  5 |                                                                                                                                          
|           1 |  6 |                                                                                                                                          
+-------------+----+                                                                                                                                          
6 rows in set (0.00 sec)                                                                                                                                      
```
这也验证了：SELECT后面接的列必须被GROUP BY后面接的列所包含。

**注意：通过session和global设置临时生效的，即当mysql重启后，都会失效。需要在mysql启动配置文件中默认设置。**
## 4、解决办法
除了上面测试时用到的临时解决的两种方法。要想mysql重启后依然生效，需要在mysql的配置文件，一般是my.cnf中的[mysqld]下面加sql_mode配置。因为我使用的是k8s部署的mysql，镜像安装和在宿主机上通过软件包安装有一定差别。但最终还是更改的my.cnf。

```shell
kubectl exec -ti mysql-75797cf796-84rdl bash
root@mysql-75797cf796-84rdl:/# 
root@mysql-75797cf796-84rdl:/# cat /etc/mysql/my.cnf
# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.
# .....
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20191102234955851.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9saWFiaW8uYmxvZy5jc2RuLm5ldA==,size_16,color_FFFFFF,t_70)
可以看到这里包含了两个目录下的文件，查看一下，mysql.conf.d下，发现有我们需要更改的文件
```shell
cat /etc/mysql/mysql.conf.d/mysqld.cnf
```
查看并将该文件用kubectl cp命令拷贝到宿主机上，修改后最终要挂载进入pod里。
```shell
kubectl cp default/mysql-75797cf796-84rdl:/etc/mysql/mysql.conf.d/mysqld.cnf /data/blog-solo/mysql-config/mysqld.cnf
```
修改后文件如下，主要关注sql_mode
```shell
root@mysql-75797cf796-84rdl:/# cd /etc/mysql/mysql.conf.d/
root@mysql-75797cf796-84rdl:/etc/mysql/mysql.conf.d# ls -l
total 4
-rw-r--r-- 1 root root 1671 Oct 26 11:40 mysqld.cnf
root@mysql-75797cf796-84rdl:/etc/mysql/mysql.conf.d# cat mysqld.cnf 
# Copyright (c) 2014, 2016, Oracle and/or its affiliates. All rights reserved.
# ...
[mysqld]
pid-file	= /var/run/mysqld/mysqld.pid
socket		= /var/run/mysqld/mysqld.sock
datadir		= /var/lib/mysql
sql_mode        = STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION
#log-error	= /var/log/mysql/error.log
# By default we only accept connections from localhost
#bind-address	= 127.0.0.1
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
root@mysql-75797cf796-84rdl:/etc/mysql/mysql.conf.d#
```
最后修改mysql-deployment：
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: mysql
spec:
  replicas: 1
  template: 
    metadata:
      labels:
        name: mysql
    spec:
      containers:
      - name: mysql 
        image: mysql:5.7.28 
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password"
        volumeMounts:
        - name: mysql-config
          mountPath: /etc/mysql/mysql.conf.d
        - name: mysql-data
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-config
        hostPath:
          path: /data/blog-solo/mysql-config/
      - name: mysql-data
        hostPath:
          path: /data/blog-solo/mysql-data/
```
注意要把配置文件和数据都挂载到宿主机上，否则pod重启后就会丢失配置和数据。

## 4、参考

[docker 下修改 mysql sql_mode和配置文件](https://blog.csdn.net/qq_31659985/article/details/80701769)
[记一次Group by 查询时的ONLY_FULL_GROUP_BY错误以及后续](https://blog.csdn.net/Abysscarry/article/details/79468411)




---------

* * *

**本公众号**免费 **提供csdn下载服务，海量IT学习资源**如果你准备入IT坑，励志成为优秀的程序猿，那么这些资源很适合你，包括但不限于java、go、python、springcloud、elk、嵌入式 、大数据、面试资料、前端 等资源。同时我们组建了一个技术交流群，里面有很多大佬，会不定时分享技术文章，如果你想来一起学习提高，可以公众号后台回复【**2**】，免费邀请加技术交流群互相学习提高，会不定期分享编程IT相关资源。

* * *

扫码关注，精彩内容第一时间推给你

![image](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTE2YjU5M2MyZjVjM2VmOGY?x-oss-process=image/format,png)

