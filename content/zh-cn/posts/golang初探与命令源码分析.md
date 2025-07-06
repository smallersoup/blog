---
title: golang初探与命令源码分析
date: '2019-10-18 13:05:47'
updated: '2019-10-18 13:05:47'
tags: [golang]
permalink: /201910181305golang
---
前段时间有群友在群里问一个go语言的问题：

就是有一个main.go的main函数里调用了另一个demo.go里的hello()函数。其中main.go和hello.go同属于main包。但是在main.go的目录下执行go run main.go却报hello函数没有定义的错：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005423929.png)

**代码结构如下：**
```shell
**gopath ---- src**

          **----gohello** 

                **----hello.go** 

                    ** ----main.go**
```

**main.go如下：**

```
package main

import "fmt"

func main() {

 fmt.Println("my name is main")

 hello()
}

```

**hello.go如下：**

```
package main

import "fmt"

func hello() {
 fmt.Println("my name is hello")
}
```

当时我看了以为是他GOPATH配置的有问题，然后自己也按照这样试了一下，报同样的错，在网上查了，也有两篇文章是关于这个错的，也提供了解决方法，即用go run main.go hello.go，试了确实是可以的。

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005424163.png)

虽然是个很简单的问题，但是也涉及到了go语言底层对于命令行参数的解析。那就来分析一下语言底层的实现吧，看一下底层做了什么，为什么报这个错？

**分析：**

*以下使用到的Go SDK版本为1.8.3*

该版本中go支持的基本命令有以下16个：

```
build       compile packages and dependencies
clean       remove object files
doc         show documentation for package or symbol
env         print Go environment information
bug         start a bug report
fix         run go tool fix on packages
fmt         run gofmt on package sources
generate    generate Go files by processing source
get         download and install packages and dependencies
install     compile and install packages and dependencies
list        list packages
run         compile and run Go program
test        test packages
tool        run specified go tool
version     print Go version
vet         run go tool vet on packages
```

在Go SDK的src/cmd/go包下有main.go文件中，Command类型的commands数组对该16个命令提供了支持：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005424337.png)

我们首先知道go语言的初始化流程如下：

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005424529.jpeg)

在执行main.go中的主函数main之前，对import进来的包按顺序初始化，最后初始化main.go中的类型和变量，当初始化到commands数组时，由于cmdRun定义在于main.go同包下的run.go中，那么就先去初始化run.go中的变量和init方法，如下代码，先把cmdRun初始化为Command类型，然后执行init()函数。

```
var cmdRun = &Command{
 UsageLine: "run [build flags] [-exec xprog] gofiles... [arguments...]",
 Short:     "compile and run Go program",
 Long: `
Run compiles and runs the main package comprising the named Go source files.
A Go source file is defined to be a file ending in a literal ".go" suffix.

By default, 'go run' runs the compiled binary directly: 'a.out arguments...'.
If the -exec flag is given, 'go run' invokes the binary using xprog:
 'xprog a.out arguments...'.
If the -exec flag is not given, GOOS or GOARCH is different from the system
default, and a program named go_$GOOS_$GOARCH_exec can be found
on the current search path, 'go run' invokes the binary using that program,
for example 'go_nacl_386_exec a.out arguments...'. This allows execution of
cross-compiled programs when a simulator or other execution method is
available.

For more about build flags, see 'go help build'.

See also: go build.
 `,
}

func init() {
 cmdRun.Run = runRun // break init loop

 addBuildFlags(cmdRun)
 cmdRun.Flag.Var((*stringsFlag)(&execCmd), "exec", "")
}
```

init()中，将runRun（其实类型是一个方法，用于处理run后的参数）赋值给cmdRu.run，addBuildFlags(cmdRun)主要是给run后面增加命令行参数（如：-x是打印其执行过程中用到的所有命令，同时执行它们）。其他15个命令和cmdRun类似，各有各的run实现。

下来主要看main.go中main的这块代码：

```
for _, cmd := range commands {
   if cmd.Name() == args[0] && cmd.Runnable() {
     cmd.Flag.Usage = func() { cmd.Usage() }
     if cmd.CustomFlags {
       args = args[1:]
     } else {
       cmd.Flag.Parse(args[1:])
       args = cmd.Flag.Args()
     }
     cmd.Run(cmd, args)
     exit()
     return
   }
 }
```

这块代码遍历commands数组，当遍历到cmdRun时，cmd.Name()其实就是拿到cmdRun.UsageLine的第一个单词run

![image](https://cdn.jsdelivr.net/gh/smallersoup/jsDelivr-cdn@main/blog/article/csdnimg/20191018005424838.png)

就会进入if分支，由于cmd.CustomFlags没有初始化故为false，走else分支，然后开始解析args命令行参数，args[1:]即取run后的所有参数。然后去执行cmd.Run(cmd, args)，对于cmdRun来说，这里执行的就是run.go中init()的第一行赋值cmdRun.run（上面说了，这是一个函数，不同命令实现方式不同)，即去执行run.go中的runRun函数，该函数主要是将命令行参数当文件去处理，如果是_test为后缀的，即测试文件，直接报错。如果是目录也直接报错（而且go run后面只能包含一个含main函数的go文件）。注意到有这么一行：

```
p := goFilesPackage(files)
```

goFilesPackage(files)除了校验文件类型和后缀，还会入栈，加载，出栈等操作，由于启动的时候没有传递hello.go，所以系统加载main.go时找不到hello函数，导致报错。

------------
