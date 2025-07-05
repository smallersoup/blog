---
title: mysql支持原生json使用说明
date: '2019-10-17 18:08:26'
updated: '2019-10-17 18:08:26'
tags: [mysql]
permalink: /201910171808mysql
---

## 正文

MySQL在5.7.8开始对json原生支持，本文将对MySQL中json类型的用法简单说明，希望对你有用。

```sql
CREATE TABLE testproject (

   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,

   `skill` JSON NOT NULL,

   `student` JSON NOT NULL,

   PRIMARY KEY (`id`)

);
```

查看表结构：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0eecad120e2af022a0dd800f301ae6c7.png)

这样JSON的字段就被创建好了

**注：**JSON类型不能有默认值。

### 插入JSON


插入 json 格式的字符串，可以是对象的形式，也可以是数组的形式，

```sql
INSERT INTO `testproject` (student, skill) VALUES ('{"id": 1, "name": "ggjg"}', '["java", "go", "vue"]');
INSERT INTO `testproject` (student, skill) VALUES ('{"id": 5, "name": "guogege"}', '[]');
```

插入json时，数据库会对json做校验，不符合json规范就会报错。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/7766e0dd76091032df10a2d0a966124e.png)

### 查询JSON：

查询 json 中的数据用 column->path 的形式，其中对象类型 path 这样表示 $.path, 而数组类型则是 $[index]


查询testproject表student字段中json对象id为1的记录：

```sql
SELECT * FROM testproject WHERE student->'$.id'= 1;
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/374d619ad147f81d38c8a735e17da304.png)

查询testproject表student字段中json对象id为1或者5的记录：

```sql
SELECT * FROM testproject WHERE student->'$.id' in (1,5);

SELECT * FROM testproject WHERE student->'$.id' = 1 or student->'$.id' = 5;
```
[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-ShdsDUDU-1571306793566)(http://upload-images.jianshu.io/upload_images/9134763-cda653c6a30e3965?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)]

也可以用函数json_extract：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/07cd73023bafa2b6b88c3e06c2ef32f2.png)

column->path方法有限制，数据源必须是表字段，否则就报错：
![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/d2914cc408cd22ba64c055947fd79bbc.png)

以下这样查询，查出来student->'$.name'包含双引号：

```sql
SELECT id, student->'$.id', student->'$.name', skill->'$[0]', skill->'$[2]' FROM testproject;
```

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/1f8e52db6c6e79873cac495a861651ff.png)

这不是我们想要的，可以用 JSON_UNQUOTE 函数将双引号去掉，从 MySQL 5.7.13 起也可以通过这个操作符 ->> 这个和 JSON_UNQUOTE 是等价的。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/93a7b9a5c601b876c1e2ceba28935a3e.png)

因为 JSON 不同于字符串，所以如果用字符串和 JSON 字段比较，是不会相等的：

```sql
mysql> SELECT * FROM testproject WHERE student = '{"id": 1, "name": "ggjg"}';
Empty set (0.00 sec)
```

此时可以通过 CAST 将字符串转成 JSON 的形式：
```sql
mysql>  SELECT * FROM testproject WHERE student = CAST('{"id": 1, "name": "ggjg"}' as JSON);
+----+-----------------------+---------------------------+
| id | skill                 | student                   |
+----+-----------------------+---------------------------+
| 10 | ["java", "go", "vue"] | {"id": 1, "name": "ggjg"} |
+----+-----------------------+---------------------------+
1 row in set (0.01 sec)
```

要特别注意的是，JSON 中的元素搜索是严格区分变量类型的，比如说整型和字符串是严格区分的：

```
mysql> SELECT * FROM testproject WHERE student->'$.id' = '1';
Empty set (0.00 sec)

mysql>
mysql> SELECT * FROM testproject WHERE student->'$.id' = 1;
+----+-----------------------+---------------------------+
| id | skill                 | student                   |
+----+-----------------------+---------------------------+
| 10 | ["java", "go", "vue"] | {"id": 1, "name": "ggjg"} |
+----+-----------------------+---------------------------+
1 row in set (0.00 sec)
```

可以看到搜索字符串 1 和整型 1 的结果是不一样的。





除了用以上 column->path 的形式搜索，还可以用JSON_CONTAINS 函数，但和 column->path 的形式有点相反的是，JSON_CONTAINS 第二个参数是不接受整数的，无论 json 元素是整型还是字符串，否则会出现这个错误：

```sql
mysql> SELECT * FROM testproject WHERE JSON_CONTAINS(student, 1, '$.id');
ERROR 3146 (22032): Invalid data type for JSON data in argument 2 to function json_contains; a JSON string or JSON type is required.
mysql>
```

这里必须要使用字符串：

```sql
mysql> SELECT * FROM testproject WHERE JSON_CONTAINS(student, '1', '$.id');
+----+-----------------------+---------------------------+
| id | skill                 | student                   |
+----+-----------------------+---------------------------+
| 10 | ["java", "go", "vue"] | {"id": 1, "name": "ggjg"} |
+----+-----------------------+---------------------------+
1 row in set (0.00 sec)
```

对于数组类型的 JSON 的查询，比如说 skill 中包含有 3 的数据，同样要用 JSON_CONTAINS 函数，同样第二个参数也需要是字符串：

```sql
mysql> SELECT * FROM testproject WHERE JSON_CONTAINS(skill, '"go"');
+----+-----------------------+---------------------------+
| id | skill                 | student                   |
+----+-----------------------+---------------------------+
| 10 | ["java", "go", "vue"] | {"id": 1, "name": "ggjg"} |
+----+-----------------------+---------------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM testproject WHERE JSON_CONTAINS(skill, '1');
+----+-----------+------------------------------+
| id | skill     | student                      |
+----+-----------+------------------------------+
| 12 | [1, 2, 3] | {"id": 4, "name": "guogege"} |
+----+-----------+------------------------------+
1 row in set (0.00 sec)
```


### 更新数据



MySQL 并不支持 column->path 的形式进行更新操作。



如果是整个 json 更新的话，和插入时类似的：

```sql
mysql> select * from testproject where id = 10;                          
+----+-----------------------+---------------------------+               
| id | skill                 | student                   |               
+----+-----------------------+---------------------------+               
| 10 | ["java", "go", "vue"] | {"id": 1, "name": "ggjg"} |               
+----+-----------------------+---------------------------+               
1 row in set (0.00 sec)                                                  
                                                                        
mysql> UPDATE testproject SET skill = '["js", "java"]' WHERE id = 10;    
Query OK, 1 row affected (0.01 sec)                                      
Rows matched: 1  Changed: 1  Warnings: 0                                 
                                                                        
mysql> select * from testproject where id = 10;                          
+----+----------------+---------------------------+                      
| id | skill          | student                   |                      
+----+----------------+---------------------------+                      
| 10 | ["js", "java"] | {"id": 1, "name": "ggjg"} |                      
+----+----------------+---------------------------+                      
1 row in set (0.00 sec)
```

json_array_append和json_array_insert函数使用：

json_array_append是在json后面追加；

json_array_insert是在指定下标插入。

```sql
mysql> select * from testproject;                                            
+----+----------------+------------------------------+                       
| id | skill          | student                      |                       
+----+----------------+------------------------------+                       
| 10 | ["js", "java"] | {"id": 1, "name": "ggjg"}    |                       
| 11 | []             | {"id": 5, "name": "guogege"} |                       
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"} |                       
+----+----------------+------------------------------+                       
3 rows in set (0.00 sec)                                                     
                                                                            
mysql> SELECT json_array_append(skill, '$', 'c') from testproject;           
+------------------------------------+                                       
| json_array_append(skill, '$', 'c') |                                       
+------------------------------------+                                       
| ["js", "java", "c"]                |                                       
| ["c"]                              |                                       
| [1, 2, 3, "c"]                     |                                       
+------------------------------------+                                       
3 rows in set (0.00 sec)                                                     
                                                                            
mysql> SELECT json_array_insert(skill, '$[1]', 'php') from testproject;      
+-----------------------------------------+                                  
| json_array_insert(skill, '$[1]', 'php') |                                  
+-----------------------------------------+                                  
| ["js", "php", "java"]                   |                                  
| ["php"]                                 |                                  
| [1, "php", 2, 3]                        |                                  
+-----------------------------------------+                                  
3 rows in set (0.00 sec)                                                     
                                                                            
mysql>
```

json_replace、json_set、json_insert和json_remove函数用法：



json_replace：只替换已经存在的旧值，不存在则忽略；

json_set：替换旧值，并插入不存在的新值；

json_insert：插入新值，但不替换已经存在的旧值；

json_remove() 删除元素。



**json_replace：**

```sql
mysql> select * from testproject;                                                                                      
+----+----------------+--------------------------------+                                                               
| id | skill          | student                        |                                                               
+----+----------------+--------------------------------+                                                               
| 10 | ["js", "java"] | {"id": 1, "name": "smallsoup"} |                                                               
| 11 | []             | {"id": 5, "name": "guogege"}   |                                                               
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"}   |                                                               
+----+----------------+--------------------------------+                                                               
3 rows in set (0.00 sec)                                                                                               
                                                                                                                      
mysql>                                                                                                                 
mysql> UPDATE testproject SET student->'$.name' = 'smallsoup' where student->'$.id' = 1;                               
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server versio
n for the right syntax to use near '->'$.name' = 'smallsoup' where student->'$.id' = 1' at line 1                      
mysql>                                                                                                                 
mysql> UPDATE testproject SET student = json_replace(student, '$.name', 'soup') WHERE student->'$.id' = 1;             
Query OK, 1 row affected (0.01 sec)                                                                                    
Rows matched: 1  Changed: 1  Warnings: 0                                                                               
                                                                                                                      
mysql> select * from testproject;                                                                                      
+----+----------------+------------------------------+                                                                 
| id | skill          | student                      |                                                                 
+----+----------------+------------------------------+                                                                 
| 10 | ["js", "java"] | {"id": 1, "name": "soup"}    |                                                                 
| 11 | []         | {"id": 5, "name": "guogege"} |                                                                 
| 12 | [1, 2, 3]    | {"id": 4, "name": "guogege"} |                                                                 
+----+----------------+------------------------------+                                                                 
3 rows in set (0.00 sec)
```

**json_set：**

```sql
mysql> select * from testproject;
+----+----------------+------------------------------+
| id | skill          | student                      |
+----+----------------+------------------------------+
| 10 | ["js", "java"] | {"id": 1, "name": "soup"}    |
| 11 | []             | {"id": 5, "name": "guogege"} |
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"} |
+----+----------------+------------------------------+
3 rows in set (0.00 sec)

mysql>  UPDATE testproject SET student = json_set(student, '$.name', 'small', '$.age', 22) WHERE student->'$.id'= 1;
Query OK, 1 row affected (0.01 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> select * from testproject;
+----+----------------+---------------------------------------+
| id | skill          | student                               |
+----+----------------+---------------------------------------+
| 10 | ["js", "java"] | {"id": 1, "age": 22, "name": "small"} |
| 11 | []             | {"id": 5, "name": "guogege"}          |
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"}          |
+----+----------------+---------------------------------------+
3 rows in set (0.00 sec)
```

**json_insert：**

```sql
mysql> select * from testproject;                                                                                      
+----+----------------+---------------------------------------+                                                        
| id | skill          | student                               |                                                        
+----+----------------+---------------------------------------+                                                        
| 10 | ["js", "java"] | {"id": 1, "age": 22, "name": "small"} |                                                        
| 11 | []             | {"id": 5, "name": "guogege"}          |                                                        
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"}          |                                                        
+----+----------------+---------------------------------------+                                                        
3 rows in set (0.00 sec)                                                                                               
                                                                                                                      
mysql> UPDATE testproject SET student = json_insert(student, '$.name', 'soup', '$.addr', '苏州') WHERE student->'$.id'=  
1;                                                                                                                    
Query OK, 1 row affected (0.00 sec)                                                                                    
Rows matched: 1  Changed: 1  Warnings: 0                                                                               
                                                                                                                      
mysql> select * from testproject;                                                                                      
+----+----------------+---------------------------------------------------------+                                      
| id | skill          | student                                                 |                                      
+----+----------------+---------------------------------------------------------+                                      
| 10 | ["js", "java"] | {"id": 1, "age": 22, "addr": "苏州", "name": "small"}   |                                        
| 11 | []             | {"id": 5, "name": "guogege"}                            |                                      
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"}                            |                                      
+----+----------------+---------------------------------------------------------+                                      
3 rows in set (0.00 sec)
```

**json_remove() :**

```sql
mysql> select * from testproject;
+----+----------------+---------------------------------------------------------+
| id | skill          | student                                                 |
+----+----------------+---------------------------------------------------------+
| 10 | ["js", "java"] | {"id": 1, "age": 22, "addr": "苏州", "name": "small"}   |
| 11 | []             | {"id": 5, "name": "guogege"}                            |
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"}                            |
+----+----------------+---------------------------------------------------------+
3 rows in set (0.00 sec)

mysql> UPDATE testproject SET student = json_remove(student, '$.name', '$.age') WHERE student->'$.id' = 1;
Query OK, 1 row affected (0.01 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> select * from testproject;
+----+----------------+------------------------------+
| id | skill          | student                      |
+----+----------------+------------------------------+
| 10 | ["js", "java"] | {"id": 1, "addr": "苏州"}    |
| 11 | []             | {"id": 5, "name": "guogege"} |
| 12 | [1, 2, 3]      | {"id": 4, "name": "guogege"} |
+----+----------------+------------------------------+
3 rows in set (0.00 sec)
```

可以看到name和age就被移除了。

以上只列出了部分函数的说明，mysql官方提供的函数列表如下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/77c3a56e868fe77bba332c8240eeaa0c.png)

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/b3174c14810640a4cf827b112a546b9b.png)


更多用法请查看官方文档：

https://dev.mysql.com/doc/refman/5.7/en/json-function-reference.html

