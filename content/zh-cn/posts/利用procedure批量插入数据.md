title: 利用procedure批量插入数据
date: '2019-10-17 14:47:21'
updated: '2019-10-17 14:47:21'
tags: [mysql]
permalink: /201910171447mysql
---
![](https://img.hacpai.com/bing/20180204.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文
**&emsp;&emsp;要求在页面查询到5000条数据，为了方便插入，准备用shell脚本写curl命令调用自己写的代码接口，但是速度慢，而且写的时候遇到点儿小问题，故用sql语句写了这个功能**
**&emsp;&emsp;由于operationlog表中的ts字段为13位的时间戳，所以采用了截取的方式。**

```SQL
DROP TABLE IF EXISTS `operationlog`;
CREATE TABLE `operationlog` (
  `sn` int(11) NOT NULL AUTO_INCREMENT,
  `opl` varchar(8) NOT NULL,
  `src` varchar(32) NOT NULL,
  `pid` varchar(32) DEFAULT NULL,
  `ts` varchar(13) NOT NULL,
  PRIMARY KEY (`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop procedure if exists batchAdd;

/*count1 循环次数 opl和src为operationlog的列*/
create procedure batchAdd(in count1 int,in opl varchar(32),in src varchar(32))
begin
	declare a int;
	set a=0;
	while a<count1 do
		begin
			/*延时1s*/
			select sleep(1);
			/*获取时间戳1523285555.207000,后面3位是0,现在的需求是ts为13位,即带ms的*/
			select @time1:=unix_timestamp(now(3));
			/*将1523285555.207000的.去掉*/
			select @time1:=replace(@time1, '.', '');
			/*取1523285555207000左边13位*/
			select @time1:=left(@time1, 13);
			/*生成sql,进行insert*/
			insert into operationlog(opl, src, pid, ts) values(opl, src, '1111', @time1);
			/*a加1*/
			set a = a + 1;
		end;

	end while;
end;

--查看procedure
show procedure status;

--调用该procedure
call batchAdd(10, 'INFO', 'AJG');

--删除procedure
drop procedure batchAdd;
```
### create procedure batchAdd如图所示：
![batchAdd_procedure](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWFiZTMzZjA2YWYwMzU3MmMucG5n?x-oss-process=image/format,png)


### 创建好procedure后,可以通过call batchAdd(10, 'INFO', 'AJG');来调用,如下图所示：
![call_batchAdd](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTI1MTE4MmYwNWI4ZWUzNzYucG5n?x-oss-process=image/format,png)




