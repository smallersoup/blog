---
title: mysql数据导出golang实现
date: '2019-10-18 13:34:05'
updated: '2019-10-18 13:34:05'
tags: [mysql]
permalink: /201910181333mysql
---

## 正文

mysql数据导出为excel文件，golang实现：

首先下载依赖到的三方库：

>Simple install the package to your [$GOPATH](https://github.com/golang/go/wiki/GOPATH "GOPATH") with the [go tool](https://golang.org/cmd/go/ "go command") from shell:

```source-shell
$ go get -u github.com/go-sql-driver/mysql
```
<br>
**具体说明请看：**
[库地址](https://github.com/go-sql-driver/mysql)
[wiki说明](https://github.com/go-sql-driver/mysql/wiki/Examples)

代码示例如下，用到了go的flag包的能力，传入命令行参数。具体看helpInfo：
```source-shell
Usage of mysqldataexport:
  -port int
     	the port for mysql,default:32085
  -addr string
    	the address for mysql,default:10.146.145.67
  -user string
    	the username for login mysql,default:dbuser

  -pwd 	string
    	the password for login mysql by the username,default:Admin@123
  -db 	string
    	the port for me to listen on,default:auditlogdb
  -tables string
    	the tables will export data, multi tables separator by comma, default:op_log,sc_log,sys_log
```

代码：

```go
package main

// 从Mysql中导出数据到CSV文件。

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"os"
	_ "github.com/go-sql-driver/mysql"
	"flag"
	"strings"
)

var (
	tables         = make([]string, 0)
	dataSourceName = ""
)

const (
	driverNameMysql = "mysql"

	helpInfo = `Usage of mysqldataexport:
  -port int
     	the port for mysql,default:32085
  -addr string
    	the address for mysql,default:10.146.145.67
  -user string
    	the username for login mysql,default:dbuser

  -pwd 	string
    	the password for login mysql by the username,default:Admin@123
  -db 	string
    	the port for me to listen on,default:auditlogdb
  -tables string
    	the tables will export data, multi tables separator by comma, default:op_log,sc_log,sys_log
	`
)

func init() {

	port := flag.Int("port", 32085, "the port for mysql,default:32085")
	addr := flag.String("addr", "10.146.145.67", "the address for mysql,default:10.146.145.67")
	user := flag.String("user", "dbuser", "the username for login mysql,default:dbuser")
	pwd := flag.String("pwd", "Admin@123", "the password for login mysql by the username,default:Admin@123")
	db := flag.String("db", "auditlogdb", "the port for me to listen on,default:auditlogdb")
	tabs := flag.String("tables", "op_log,sc_log,sys_log", "the tables will export data, multi tables separator by comma, default:op_log,sc_log,sys_log")

	flag.Usage = usage

	flag.Parse()

	tables = append(tables, strings.Split(*tabs, ",")...)

	dataSourceName = fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8", *user, *pwd, *addr, *port, *db)
}

func main() {

	count := len(tables)
	ch := make(chan bool, count)

	db, err := sql.Open(driverNameMysql, dataSourceName)
	defer db.Close()
	if err != nil {
		panic(err.Error())
	}

	// Open doesn't open a connection. Validate DSN data:
	err = db.Ping()
	if err != nil {
		panic(err.Error())
	}

	for _, table := range tables {
		go querySQL(db, table, ch)
	}

	for i := 0; i < count; i++ {
		<-ch
	}
	fmt.Println("Done!")
}

func querySQL(db *sql.DB, table string, ch chan bool) {
	fmt.Println("开始处理：", table)
	rows, err := db.Query(fmt.Sprintf("SELECT * from %s", table))

	if err != nil {
		panic(err)
	}

	columns, err := rows.Columns()
	if err != nil {
		panic(err.Error())
	}

	//values：一行的所有值,把每一行的各个字段放到values中，values长度==列数
	values := make([]sql.RawBytes, len(columns))
	// print(len(values))

	scanArgs := make([]interface{}, len(values))
	for i := range values {
		scanArgs[i] = &values[i]
	}

	//存所有行的内容totalValues
	totalValues := make([][]string, 0)
	for rows.Next() {

		//存每一行的内容
		var s []string

		//把每行的内容添加到scanArgs，也添加到了values
		err = rows.Scan(scanArgs...)
		if err != nil {
			panic(err.Error())
		}

		for _, v := range values {
			s = append(s, string(v))
			// print(len(s))
		}
		totalValues = append(totalValues, s)
	}

	if err = rows.Err(); err != nil {
		panic(err.Error())
	}
	writeToCSV(table+".csv", columns, totalValues)
	ch <- true
}

//writeToCSV
func writeToCSV(file string, columns []string, totalValues [][]string) {
	f, err := os.Create(file)
	// fmt.Println(columns)
	defer f.Close()
	if err != nil {
		panic(err)
	}
	//f.WriteString("\xEF\xBB\xBF")
	w := csv.NewWriter(f)
	for i, row := range totalValues {
		//第一次写列名+第一行数据
		if i == 0 {
			w.Write(columns)
			w.Write(row)
		} else {
			w.Write(row)
		}
	}
	w.Flush()
	fmt.Println("处理完毕：", file)
}

func usage() {
	fmt.Fprint(os.Stderr, helpInfo)
	flag.PrintDefaults()
}

```
操作示例：

编译代码生成可执行文件：
```
go build mysqldataexport.go
```

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/30ff4171c11f0be82aa772dec6ef0aad.png)


数据库中有test2库下的test表：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/0be2f1be962adbf028c6f81c7ae9ca4a.png)


导出其中的数据：
```
.\mysqldataexport.exe -port=3306 -addr="localhost" -user="root" -pwd="mysql" -db="test2" -tables="test"
```
![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/feb133b6844f15f4f7241a91933dc43e.png)

导出结果如下：

![image.png](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/artical/imgconvert-csdnimg/035fe6989d835b8f2922f5259b437791.png)




---------
