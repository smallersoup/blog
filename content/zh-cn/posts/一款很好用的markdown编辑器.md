title: 一款很好用的markdown编辑器
date: '2019-10-17 15:25:57'
updated: '2019-10-17 15:25:57'
tags: [工具, typora]
permalink: /201910171525tools
---
![](https://img.hacpai.com/bing/20190115.jpg?imageView2/1/w/960/h/540/interlace/1/q/100)


## 正文

Markdown 其实向来是文字爱好者和码农们的小众需求，市面上也涌现出了形形色色的 Markdown 编辑器，Mou、Typed、Ulysess、Macdown、简书、有道云等，这些比较流行的 Markdown 编辑器，都基本采用了「写字」和「预览」相分离的策略。

Typora的设计理念就是极致简洁，它将「写字」和「预览」这两件事情合并了，输入的地方，也是输出的地方，即所见即所得。

**编辑预览合一：**

所有的行内元素（如加粗、斜体）都会根据当前是否在编辑态而智能地在编辑态和预览态切换，而区块级元素（如标题、列表）则会在按下 Enter 后即时渲染，不能再次编辑。

![编辑预览合一](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNGU1OGIxZDkyM2ZjYWM4Zg?x-oss-process=image/format,png)

**表格、代码、公式编辑：**

之所以把这三个放一块是因为他们都是区块元素，而且它们都可以使用快捷键插入。

**表格：**

插入表格的快捷键在windows上是ctrl + T,效果如下：

![表格](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNTcxOTBiZjRmNmQ4Y2U3YQ?x-oss-process=image/format,png)

**代码：**

输入```按下回车，如图：

![代码](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMzdmYmQ1YmE0Y2E3NTlhYQ?x-oss-process=image/format,png)

右下角可以输入代码的语言，可以根据不同的语言自动高亮显示，连 Swift 也不在例外。

**数学表达式：**

要启用这个功能，首先到Preference -> Editor中启用。

![数学表达式](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLWNkYjhiNjcxZjVjNTgyNWEucG5n?x-oss-process=image/format,png)


然后使用$符号包裹Tex命令，例如：

$lim_{x \to \infty} \ exp(-x)=0$

将产生如下的数学表达式：

limx→∞ exp(−x)=0

![数学表达式](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtOWY4YzgyNDY3MGU0MmZkZQ?x-oss-process=image/format,png)



Typora支持Latex的公式编辑，公式编辑几乎和代码编辑的使用方法相同，同样分行内公式和行间公式，行内公式用两个$包裹起来，行间公式可以使用快捷键ctrl+shift+m插入：

![公式](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZTI0MjYxMTZiNWE1MGYwZQ?x-oss-process=image/format,png)


**插入图片：**

在传统的 Markdown 编辑器中，如果想要插入一张图片，默认的语法是这样的：

![文字会被md解析，只能截图](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy85MTM0NzYzLTUxNTI5YjNiMmRiMjY5ZjMucG5n?x-oss-process=image/format,png)


而在 Typora 中，只需要像把图片拖拽进去，就大功告成了。再也不用记住语法格式，再也不用输文件名，再也不用自己去找文件的路径地址，就是这么简单。

![插入图片](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMDY2NDk1Y2M1MWMzZGY0Zg?x-oss-process=image/format,png)

**自定义主题：**

下载完成后默认会带有几套主题：Github、newprint、Night、pixyll、whitey

![自定义主题](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtNDZiZGRiYjZmYTg1ZDk3Mw?x-oss-process=image/format,png)

**导出：**

Typora的导出选项提供了很多选项，PDF、html等等，

![导出格式分类](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtZDRjNGViMTIzZjQzMDM0Nw?x-oss-process=image/format,png)

如下为导出的PDF格式预览：

![导出预览](https://imgconvert.csdnimg.cn/aHR0cDovL3VwbG9hZC1pbWFnZXMuamlhbnNodS5pby91cGxvYWRfaW1hZ2VzLzkxMzQ3NjMtMTlhZGNlZDIwNjI2ZTJhOA?x-oss-process=image/format,png)

--------------------------------------------

**该软件的 windows和mac版的 可以关注文末公众号后在后台回复【1】，加小助手微信索取。**

---------------------------------
