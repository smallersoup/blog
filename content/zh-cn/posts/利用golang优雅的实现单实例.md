title: 利用golang优雅的实现单实例
date: '2019-10-18 12:58:57'
updated: '2019-10-18 12:58:57'
tags: [golang]
permalink: /201910181258golang
---
平时编写代码过程中，经常会遇到对于全局角度只需运行一次的代码，比如全局初始化操作，设计模式中的单例模式。针对单例模式，**java**中又出现了饿汉模式、懒汉模式，再配合**synchronized**同步关键字来实现。其目的无非就是将对象只初始化一次，而且最好保证在用到的时候再进行初始化，以避免初始化太早浪费资源，或者两次初始化破坏单例模式的实例唯一性。

**Go**语言的**sync**包中提供了一个**Once**类型来保证全局的唯一性操作，其通过**Do(f func())**方法来实现，即使** f** 函数发生变化，其也不会被执行，下面我们来看一个小例子：

```
package main

import (
 "fmt"
 "sync"
 "time"
)

var once sync.Once

func main() {

 //once循环调用firstMethod函数10次,其实只执行一次
 for i := 0; i < 10; i   {
   once.Do(firstMethod)
   fmt.Println("count:---", i)
 }

 //起10个协程,虽然用once去调secondMethod函数,但该函数不会被执行
 //只打印------i
 for i := 0; i < 10; i   {
   go func(i int) {
     once.Do(secondMethod)
     fmt.Println("-----", i)
   }(i)
 }
 //主协程等1min,等上面的10个协程执行完
 time.Sleep(1 * time.Second)
}
func firstMethod() {
 fmt.Println("firstMethod")
}
func secondMethod() {
 fmt.Println("secondMethod")
}
```

运行程序输出如下结果：

```
firstMethod
count:--- 0
count:--- 1
count:--- 2
count:--- 3
count:--- 4
count:--- 5
count:--- 6
count:--- 7
count:--- 8
count:--- 9
----- 0
----- 2
----- 4
----- 5
----- 8
----- 6
----- 9
----- 3
----- 7
----- 1

Process finished with exit code 0
```

**然后我们来分析一下：**

程序中首先定义了一个名为**once**的**sync.Once**类型，然后**main**函数中第一个**for**循环10次，但是由于**once.Do(f func)**中的**f**函数全局只执行一次，所以**firstMethod()**函数只被执行一次；之后进入第二个**for**循环，这里**once.Do(f func)**方法的参数变为**secondMethod**函数。起10个协程去调，但由于**once.Do(secondMethod)**和**once.Do(firstMethod)**用的是**Once**类型的同一个实例，所以**secondMethod**函数实际上不会被执行。这解释了上面运行结果输出。

查看源代码**once.go**，里面有这样的解释：

> if once.Do(f) is called multiple times, only the first call will invoke f,
even if f has a different value in each invocation. A new instance of
Once is required for each function to execute.

大概意思是：如果**once.Do(f)**被调用多次，只有第一次调用才会执行**f**函数，即使**f**是不同的函数。为了每一个函数都被执行，就需要不同的**Once**实例。

我们查看**Once**类型的定义：

```
type Once struct {
 m    Mutex
 done uint32
}
```

源码中其实用到了互斥锁**m**和标志位**done**。然后再看**Do**方法的实现：

```
func (o *Once) Do(f func()) {
 if atomic.LoadUint32(&o.done) == 1 {
   return
 }
 // Slow-path.
 o.m.Lock()
 defer o.m.Unlock()
 if o.done == 0 {
   defer atomic.StoreUint32(&o.done, 1)
   f()
 }
}
```

每次调用**Do**方法之前，用**atomic**包的**LoadUint32**函数获取标志位**done**的值，等于1则说明**Do**方法已经被调用过，直接**return**，什么都不做。否则利用互斥锁，保证协程安全的去调用**f**函数，之后把标志位**done**置为1。

下面我们看一个例子，来实现单实例：

```
package main

import (
 "fmt"
 "sync"
 "time"
)

var once sync.Once

var mmp map[int]string

func main() {

 for i := 0; i < 10; i   {
   go func(i int) {
     once.Do(func (){
        mmp = make(map[int]string, 10)
     })
     fmt.Printf("-----%d------%p\n", i, &mmp)
   }(i)
 }
 //主协程等1min,等上面的10个协程执行完
 time.Sleep(1 * time.Second)
}
```

我们起10个协程去竞争初始化类型为字典类型的**mmp**，然后打印每次**mmp**的地址，运行输出如下：

```
-----1------0x50cca0
-----3------0x50cca0
-----2------0x50cca0
-----4------0x50cca0
-----7------0x50cca0
-----6------0x50cca0
-----8------0x50cca0
-----9------0x50cca0
-----5------0x50cca0
-----0------0x50cca0

Process finished with exit code 0
```

我们可以看到**mmp**每次地址都一样。如此就轻松优雅就实现了和**java**单例模式相似的效果。

推荐文章：

[java单例模式](https://mp.weixin.qq.com/s?__biz=MzI4Njc5NjM1NQ==&mid=2247485196&idx=1&sn=777aabdd20d10b1256a7dfcb163e034f&scene=21#wechat_redirect)


