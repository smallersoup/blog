---
title: java、golang日志文件转储压缩实现
date: '2019-10-17 15:27:52'
updated: '2019-10-17 15:27:52'
tags: [golang, java, 日志]
permalink: /201910171527golangjava
---
![](https://img.hacpai.com/bing/20190324.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

日志的转储和压缩是非常关键的，它不仅可以减少硬盘空间占用，主要还可以在发生故障时根据日志定位出故障原因。下面来看看golang和java的文件转储实现。



### go语言：

用到了filepath包下的Walk方法，具体说明可以参看历史文章：
[go语言path/filepath包之Walk源码解析](https://mp.weixin.qq.com/s?__biz=MjM5MzU5NDYwNA==&mid=2247483686&idx=1&sn=dd9fae8d6c4954f595dd3b6c1f96179c&scene=21#wechat_redirect)

```go
package main

import (
 "fmt"
 "os"
 "io"
 "archive/zip"
 "path/filepath"
 "time"
 "log"
)

func main() {

 logFile := "D:/tmp/successLog/logs/root.log"

 backFile := "D:/tmp/successLog/logs/root_" + time.Now().Format("20060102150405") + ".zip"
 
 err := zipFile(logFile, backFile)
 if err != nil {
   log.Println(fmt.Sprintf("zip file %s to %s error : %v", logFile, backFile, err))
   return
 } else {
   os.Remove(logFile)
 }

 //转储后创建新文件
 //createFile()

 //修改文件权限
 //os.Chmod(backfile, 0400)

 //删除备份文件
 //deleteOldBackfiles(dir)
}


func zipFile(source, target string) error {

 zipFile, err := os.OpenFile(target, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0440)
 if err != nil {
   log.Println(err)
   return err
 }
 defer zipFile.Close()

 archive := zip.NewWriter(zipFile)
 defer archive.Close()

 return filepath.Walk(source, func(path string, info os.FileInfo, err error) error {
   if err != nil {
     return err
   }

   header, err := zip.FileInfoHeader(info)
   if err != nil {
     return err
   }

   if !info.IsDir() {
     header.Method = zip.Deflate
   }
   header.SetModTime(time.Now().UTC())
   header.Name = path
   writer, err := archive.CreateHeader(header)
   if err != nil {
     return err
   }

   if info.IsDir() {
     return nil
   }
   file, err := os.Open(path)

   if err != nil {
     return err
   }
   defer file.Close()

   _, err = io.Copy(writer, file)
   return err
 })
}
```

![go压缩结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWNjNTZkMTEyM2Y5OTFmN2IucG5n?x-oss-process=image/format,png)


### java版：

说明见注释。

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.zip.CRC32;
import java.util.zip.CheckedOutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
* @program: website
* @description: 转储压缩文件
* @author: smallsoup
* @create: 2018-08-12 17:58
**/

public class ZipFile {

   private static final Logger LOGGER = LoggerFactory.getLogger(ZipFile.class);

   /**
    * 格式化文件名格式
    */
   private static final String AUDIT_LOG_FORMAT = "yyyyMMddHHmmssSSS";

   /**
    * 压缩后文件后缀
    */
   private static final String AUDIT_FILE_ZIP_SUFFIX = ".zip";

   /**
    * 压缩前文件后缀
    */
   private static final String AUDIT_FILE_EXT = ".log";

   private static final int ZIP_BUFFER = 4096;

   /**
    * 控制压缩后的文件解压后是否带base路径
    */
   private static final String rootPath = "";


   public static void main(String[] args) throws IOException {

       System.out.println();

       new ZipFile().zipAuditLogFile("D:/tmp/successLog/logs/root.log");
   }

   /**
    * 日志压缩
    *
    * @param waitZipFile 要压缩文件名
    * @throws IOException
    */
   private void zipAuditLogFile(String waitZipFile) throws IOException {
       File oldFile = new File(waitZipFile);

       if (!oldFile.exists()) {
           LOGGER.error("zipAuditLogFile name is {} not exist", waitZipFile);
           return;
       }

       //生成zip文件名
       DateFormat dataFormat = new SimpleDateFormat(AUDIT_LOG_FORMAT);
       String formatTime = dataFormat.format(oldFile.lastModified());

       int end = waitZipFile.length() - AUDIT_FILE_EXT.length();
       String zipFileName = waitZipFile.subSequence(0, end) + "_" + formatTime + AUDIT_FILE_ZIP_SUFFIX;

       File zipFile = new File(zipFileName);

       FileOutputStream zipfos = null;
       ZipOutputStream zipOs = null;
       CheckedOutputStream cos = null;


       try {
           zipfos = new FileOutputStream(zipFile);
           cos = new CheckedOutputStream(zipfos, new CRC32());

           zipOs = new ZipOutputStream(cos);

           compress(oldFile, zipOs, rootPath);

           if (zipFile.exists()) {
               // 写完的日志文件权限改为400
               try {
                   //linux上才可以运行,windows上需要装cygwin并且把cygwin的bin目录加到环境变量的path中才可以
                   Runtime.getRuntime().exec("chmod 400 -R " + zipFile);
                   //压缩后删除旧文件
                   boolean isDelete = oldFile.delete();
                   //创建新文件
                   if (isDelete) {
                       oldFile.createNewFile();
                   }
//                    boolean isSuccess = PathUtil.setFilePermision(zipFile.toPath(), ARCHIVE_LOGFILE_PERMISION);
//                    LOGGER.warn("set archive file: {}, permision result is {}", zipFile.getAbsolutePath(), isSuccess);
               } catch (IOException e) {
                   LOGGER.error("set archive file:{} permision catch an error: {}", zipFile, e);
               }
           }

       } finally {

           if (null != zipOs) {
               zipOs.close();
           }

           if (null != cos) {
               cos.close();
           }

           if (null != zipfos) {
               zipfos.close();
           }
       }
   }

   /**
    * 压缩文件或目录
    *
    * @param oldFile 要压缩的文件
    * @param zipOut  压缩文件流
    * @param baseDir baseDir
    * @throws IOException
    */
   private void compress(File oldFile, ZipOutputStream zipOut, String baseDir) throws IOException {

       if (oldFile.isDirectory()) {

           compressDirectory(oldFile, zipOut, baseDir);

       } else {
           compressFile(oldFile, zipOut, baseDir);
       }
   }

   /**
    * 压缩目录
    *
    * @param dir     要压缩的目录
    * @param zipOut  压缩文件流
    * @param baseDir baseDir
    * @throws IOException
    */
   private void compressDirectory(File dir, ZipOutputStream zipOut, String baseDir) throws IOException {

       File[] files = dir.listFiles();

       for (File file : files) {
           compress(file, zipOut, baseDir + dir.getName() + File.separator);
       }
   }

   /**
    * 压缩文件
    *
    * @param oldFile 要压缩的文件
    * @param zipOut  压缩文件流
    * @param baseDir baseDir
    * @throws IOException
    */
   private void compressFile(File oldFile, ZipOutputStream zipOut, String baseDir) throws IOException {

       if (!oldFile.exists()) {
           LOGGER.error("zipAuditLogFile name is {} not exist", oldFile);
           return;
       }

       BufferedInputStream bis = null;

       try {

           bis = new BufferedInputStream(new FileInputStream(oldFile));

           ZipEntry zipEntry = new ZipEntry(baseDir + oldFile.getName());

           zipOut.putNextEntry(zipEntry);

           int count;

           byte data[] = new byte[ZIP_BUFFER];

           while ((count = bis.read(data, 0, ZIP_BUFFER)) != -1) {
               zipOut.write(data, 0, count);
           }

       } finally {
           if (null != bis) {
               bis.close();
           }
       }

   }

}  
```

![java压缩结果](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTkyYmJmMGNkOTRhMWFkMTUucG5n?x-oss-process=image/format,png)

修改权限也可以利用Java7中NIO.2对元数据文件操作的支持，具体可以查看NIO包的使用，其相关教程见文末说明。

代码如下：

```java
package com.website.common;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Set;

/**
* 提供文件路径公共函数 改变权限，判断是否正规文件，判断是否路径在安全路径下等
*
* @program: website
* @description: 路径工具, 修改权限
* @author: smallsoup
* @create: 2018-08-14 07:56
**/

public class PathUtil {

   /**
    * POSIX表示可移植操作系统接口,并不局限于unix类系统
    */
   private static final boolean ISPOSIX = FileSystems.getDefault().supportedFileAttributeViews().contains("posix");

   /**
    * 数字权限格式,如600
    */
   private static final int PERM_LEN_THREE = 3;

   /**
    * 如765   rwxrw_r_x
    */
   private static final int PERM_LEN_NINE = 9;


   /**
    * 设置文件的权限，尽在posix下有效
    *
    * @param file 文件
    * @param perm 权限 类似 “rw-r-----”, "640"
    * @return true 修改成功 false 修改失败
    * @throws IOException
    */
   public static boolean setFilePermision(Path file, String perm) throws IOException {
       if (!ISPOSIX) {
           return true;
       }
       // 750 -> "rwxr-x---"
       if (perm.length() == PERM_LEN_THREE) {
           perm = trans2StrPerm(perm);
       }

       if (perm.length() != PERM_LEN_NINE) {
           return false;
       }

       Set<PosixFilePermission> perms = PosixFilePermissions.fromString(perm);
       Files.setPosixFilePermissions(file, perms);
       return true;
   }

   /**
    * 转换
    *
    * @param digitPerm 长度为3的数字字符串
    * @return
    */
   private static String trans2StrPerm(String digitPerm) {
       StringBuilder builder = new StringBuilder(9);
       // owner
       builder.append(toStringPerm(digitPerm.charAt(0)));
       // group
       builder.append(toStringPerm(digitPerm.charAt(1)));
       // other
       builder.append(toStringPerm(digitPerm.charAt(2)));
       return builder.toString();
   }

   private static String toStringPerm(char ch) {
       switch (ch - '0') {
           case 7:
               return "rwx";
           case 6:
               return "rw-";
           case 5:
               return "r-x";
           case 4:
               return "r--";
           case 3:
               return "-wx";
           case 2:
               return "-w-";
           case 1:
               return "--x";
           case 0:
               return "---";
           default:
               return "";
       }
   }
}
```
-------

**go语言、NIO等学习资料 可以关注文末公众号后在后台回复【1】 获取。**

* * *
