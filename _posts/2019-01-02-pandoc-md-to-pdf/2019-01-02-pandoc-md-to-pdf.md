---
title: 用 pandoc 将 markdown 转化为 pdf
date: 2019-01-02 15:28:44 +0800
tags: 
- pandoc
- latex
categories: tool
comments: true
description: 基于 html 和 latex 两种转换中介实现 markdown 到 pdf 渲染
---

需求之一来自于最近开始将读文献和看日语原版漫画时遇到的单词和用例记录在一个 markdown 笔记里.
在电脑上阅读这些 markdown 笔记完全没有问题, 但是在移动端中阅读就比较困难,
每次在 Typora 里手动导出也很麻烦, 于是就想着能不能把 markdown 转化成 pdf 的过程自动化.
自然就想到了在文件格式转换中非常有名的 [pandoc](https://pandoc.org/).

这里将以 html 和 latex 两种转换中介来讨论.
由于 latex 对学术写作有着更好的支持, 因此笔者将重点放在了后者上.
文中总结了一些模板变量的用法和注意事项.
最后以转换 `demo.md` 为例, 用 Makefile 展示了 `markdown+pandoc+xelatex+bibtex` 一整条工具链.

## 初步尝试

从 Homebrew 安装 pandoc

``` bash
brew install pandoc
```

然后用 pandoc 转换一个包含中文释义的笔记 demo.md (见[压缩包](demo.tar.gz))

``` bash
pandoc demo.md -o demo.pdf
```

返回错误

```
Error producing PDF.
! Package inputenc Error: Unicode character 因 (U+56E0)
(inputenc)                not set up for use with LaTeX.
...
Try running pandoc with --pdf-engine=xelatex.
```

照错误信息换用 `xelatex` 则出现了一大堆中文字符的 `Missing character` 警告

```
[WARNING] Missing character: There is no 因 in font [lmroman10-regular]:mapping=tex-text;!
[WARNING] ...
```

生成的 pdf 里这些中文字符都消失了, 只有孤零零的英文. 看来事情没这么简单.

## 基于 html 向 pdf 转化

一开始转化单词笔记的时候就是想转成 GitHub Favored Markdown 风格的 pdf,
于是第一反应是找了一个类似 GFM 的 [CSS](https://gist.github.com/killercup/5917178),
下载为 `gfm.css`, 和 md 存放在一个文件夹下, 运行

```bash
# wrong command
pandoc note.md -o note.pdf --css gfm.css
```

进行转化, 但这样仍然会报最开始的错误. 其原因是 pandoc 默认使用 latex 作为 pdf 生成引擎, 在这种情况 css 显然是没有效果的.

html 转到 pdf 的转换引擎的一种选择是开源工具[wkhtmltopdf](https://wkhtmltopdf.org/), 用 Homebrew 安装后, 执行

```bash
pandoc note.md -o note.pdf --css gfm.css --pdf-engine wkhtmltopdf -t html5
```

就能正常转换了! 上面去掉 `-t html5` 也可以正常运行.
除 [wkhtmltopdf](https://wkhtmltopdf.org/) 外也可以用 [prince](http://www.princexml.com/), 但它太贵了…

`gfm.css` 对自己来说不是特别好看, 尤其没有 GitHub 那样的浅蓝色代码背景以及对行间代码的渲染,
所以对 css 稍微做了一些修改.
`pre code` 部分参考了这个 [css](https://github.com/sindresorhus/github-markdown-css).

```css
/* 在一级标题前面加上朝右的蓝色三角 */
h1:before {
  content: "\25B6\2005";
  color: #0645ad;
  font-size: 60%;
  vertical-align: middle;
}
pre {
  padding: 16px;
  overflow: auto;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}
code {
  padding: 0.2em 0.4em;
  margin: 0;
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
}
pre>code {
  display: inline;
  max-width: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}
```

2019-04-30 补充: 后来又陆续做了其他改进, 转化了北大超算的使用教程, 最终效果大概是下面这样

![pandoc-html-pdf](pandoc-html-pdf.png)
_css 渲染效果_

## 借助模板的基于 latex 的转化

如果 markdown 只是写一些代码片断和非常简单的数学公式, 那么上面的 html 转换完全足够了.
但在 markdown 里写复杂的 latex 公式仍然非常要命, 有如下两个原因

- 在编辑多次出现的复杂记号上有困难. 最简单的例如算符矩阵元尖括号环境, Bloch 函数 `\varphi_{n\mathbf{k}}(\mathbf{r})`, 还有其他上下标特别多的记号.
  这种情况下显然没有在 latex 里直接调 `physics` 包和 `\newcommand` 自定义来得方便好用,
  而重复写很长的 latex 源码显然使得 markdown 失去了它原有的便携性.
- 用 html 作为中介产生包含数学公式的 pdf 需要使用诸如 MathJax、MathML 或者 KaTeX 来渲染, 而这些工具的渲染效果在应对复杂公式方面远远不及原生 latex.

所以对于公式密集的笔记还是得用 latex 作为 pdf 引擎.

### 使用模板

在通过 latex 进行 pdf 格式转化时, 为了使得转化的 latex 能够正常编译, 需要用`--template`选项套用模板. 不借助模板转化得到的 tex 是无法正常编译的, 例如

```bash
pandoc.note.md -o note_no_template.tex # unable to compile
pandoc note.md -o note.tex --template default # compile ok
```

其中 `default` 表示使用默认 templates 文件夹下后缀对应输出格式、文件名为 `default` 的文件作为模板.
macOS 默认模板文件的位置在 `share/x86_64-osx-ghc-8.4.4/pandoc-2.4/data/templates/`. 在那里可以看到一个 `default.latex`, 就是第二行命令所用的模板.
除 latex 外, 有其他输出格式的默认模板.

通过修改模板, 加入想要的 latex 指令, 可以将 markdown 转成包含合适的 `tex` 文件,
进而得到目标的 pdf 输出. 要利用编辑好的自定义模板 `abc.latex` 有两种办法

1. 把它放在和 `note.md` 同一文件夹下, 将 `default` 改为 `./abc.latex`.
2. 把 `abc.latex` 移动到默认 templates 文件夹下, 将 `default` 改为 `abc`.

### 编辑模板

接下来的问题就是怎么写出自己想要的模板.
默认的模板对我来说很复杂, 而且它同不少 latex 的高级指令有关, 直接看模板会晕.
所以还是从 pandoc 的 [templates 手册](https://pandoc.org/MANUAL.html#templates)开始.

latex 模板主要包含序言部分和 `document` 环境.
比如我想在序言里包含 `amsmath` 包, 那就在模板中序言部分加一句

```tex
\usepackage{amsmath}
```

那它就会出现在被转换的`tex`文件里.

### 文件元数据控制

为了应对多种情境 (handout, slides, book, thesis), 默认模板里通常包含许多 pandoc 变量.
由这些变量值和一些条件语法, 可以在产生对应于情境的添加文本,
这样就可以用一个模板通吃了. (然而通吃又好用的模板很难维护. )

这些变量值都可以在一个遵循 yaml 语法的元数据块 (metadata block) 中定义.
yaml 块可以以 `---` 开头, `...` 或 `---` 结尾的形式写在被转化的文档里,
也可以写在一个单独的 `.yaml` 文件里, 转化时一并作为输入.

pandoc 所利用的文件元数据可以在 yaml 元数据块中定义如下(从 manual 改编)

```yaml
---
title: A Fake Thesis
author:
- name: Aristotle
  affiliation: The Academy
- name: minyez
  affiliation: PKU
date: 2019-01-02
subtitle: a Pandoc Template Example
abstract: |
  Just a non-existing thesis for pandoc test.
  The abstract can have multiple lines.
  
  Also can have multiple paragraphs.
keywords:
- pandoc
- markdown
---

```

做一点解释

- 若用如上 `author` 写法, 在模板中使用时需要用 `author.name` 和 `author.affiliation` 来获取对应的姓名和单位, 并对 `author` 遍历. 否则这么写是不会在 tex 中正确产生 author 的.
- `abstract` 可以有多行和多段.

这些元数据会被包含在生成的 pdf 元数据中. 下面几节总结一些其他常用的 pandoc 变量.

### 目录和文档首尾

可以用 `toc` 变量产生目录页

```yaml
---
toc: true
toc-title: "Custom TOC title"
include-before:
- "In default template, "
- "we are in the document part, "
- "right after abstract and before TOC"
include-after:
- "we are next to the end of the document."
- "Yep."
---
```

一些解释

- `toc` 只需要是一个非空值, 就可以显示目录.

- `include-before` 和 `include-after `的内容会出现 document 环境内.

- 有 `header-includes`, 可用来在元数据块中定义序言命令.
  需要使用 latex 的源代码环境标记起来, 否则会被当作 markdown 代码进行转换.
  实际使用的时候一般是把需要的宏包和自定义命令都写在 template 里面,
  比较少用 `header-includes` 来定义, 这里就不展开了.

### 语言

``` yaml
---
lang: en
dir: ltr
---
```

`lang` 标识文档的主要语言, 语言代码符合 [BCP 47](https://tools.ietf.org/html/bcp47)(BCP: Best Current Practices). 虽说要符合, 但是这个网站并没有直接给出所有可用的语言标签. 暂时只用英语 en.

`dir` 控制文字从左向右(ltr)还是从右向左(rtl). 只有 `xelatex` 作为 pdf 引擎使才能完全支持 `dir`.
测试发现 rtl 在 `--pdf-engine=pdflatex` 下不会报错, 但也没有效果.

### 可用的 latex 变量

这一节总结一些针对 latex 转换的 pandoc 变量, 按照用途不同做了简单分类.

#### 排版布局

| 变量名          | 含义                                            |
| --------------- | ----------------------------------------------- |
| `papersize`     | 纸张大小, `letter`,`a4`                         |
| `fontsize`      | 字体大小                                        |
| `documentclass` | 文档类型, `article`, `report`, `book`, `memoir` |
| `beameroption`  | beamer 选项                                     |
| `geometry`      | 设置 geometry 包的选项, 可设多个值              |
| `linestretch`   | 使用`setspace`包调节行间距                      |
| `subparagraph`  | 禁用 latex 模板中将段落重定义为节的行为         |
| `lof`, `lot`    | 包含图和表的列表                                |
| `thanks`        | 在标题后添加致谢内容                            |

使用`ctexart`文档类型可以解决字体问题, 因为这个宏包中包含了字体设置

```yaml
---
documentclass: ctexart
---
```

也可以通过改变下面的字体变量手动调节.

#### 字体

| 变量名              | 含义                                                      |
| ------------------- | --------------------------------------------------------- |
| `fontfamily`        | 设置 `pdflatex` 使用的字体包, 默认为 Latin Modern (lm).   |
| `fontfamilyoption`  | 对应 `fontfamily` 的选项                                  |
| `mainfont` 等       | `xelatex` 使用的字体. 利用 `fontspec` 包, 可使用系统字体. |
| `mainfontoption` 等 | 对应于 `mainfont` 等的字体选项                            |
| `fontenc`           | 字体编码. 默认 `T1` 应该够用.                             |

`mainfont` 等中包含字体变量 `mainfont`, `romanfont`, `sansfont`, `monofont`,
`mathfont` 和 `CJKmainfont`. `CJKmainfont` 的使用需要有 `xecjk` 包.
每一个都对应一个 `fontoption` 字体选项变量.
系统中可用的中文字体可通过 `fc-list:lang=zh-cn` 查看. 日语字体用`:lang=ja` .
做以下改动

```yaml
---
CJKmainfont: Songti SC
mainfont: Times New Roman
---
```

将 `CJKmainfont` 设为 `Songti SC` 后上面的字体缺失报警就没有了.
如果直接把 `mainfont` 改成 `Songti SC` 也可以解决问题,
但如此一来英文字体也会应用宋体, 看上去比较奇怪 (用 Word 应该很有体验). [Pandoc Wiki](https://github.com/jgm/pandoc/wiki/Pandoc-With-Chinese-\(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87\))上说用应该把 `mainfont` 设为中文字体, 我觉得并不必要.

#### 颜色

| 变量名       | 含义         |
| ------------ | ------------ |
| `colorlinks` | 链接颜色开关 |
| `linkcolor`  | 内链颜色     |
| `filecolor`  | 外链颜色     |
| `citecolor`  | 引用颜色     |
| `urlcolor`   | URL 链接颜色 |
| `toccolor`   | TOC 链接颜色 |

颜色选项由 `xcolor` 提供, 链接颜色由 `hyperref` 包及 `\hypersetup{}` 命令设置. 
`xcolor` 手册 Section 4 中给出了基本颜色和通过 `dvipsnames`, `svgnames`,
`x11names` 选项可用的颜色名字. 比如

```yaml
---
colorlinks: true
linkcolor: red
filecolor: Cyan
urlcolor: Navy
toccolor: Ivory3
---
```

Navy 和 Ivory3 分别是 `svgnames` 和 `x11names` 里的颜色名字.
使用 `svgnames` 和 `x11names` 里的颜色时, 由于默认模板里关于 `xcolor` 的语句是

```tex
\usepackage[dvipsnames,svgnames*,x11names*]{xcolor}
```

此时要使用这两种颜色必须用 `\definecolors{}` 事先激活. 比如在模板里 `xcolor` 包后添加

```tex
\definecolors{Navy}
\definecolors{Ivory3}
```

否则会报错

```
! Package xcolor Error: Undefined color `Navy'.
```

用相对路径、`file://`加相对路径或直接绝对路径的本地文件和 URL 链接都是 Navy 色. 用`run:`可以产生 Cyan 色的文件链接(file link), 但是这样的链接对 markdown 没有意义.

#### 参考文献

因为暂时还不会考虑加入参考文献(目前至多考虑脚注), 而且想要用 markdown+模板达到和用期刊模板一样的参考文献效果似乎不是那么简单, 所以暂不做深入讨论, 可以参考最后的例子和其他网络资源.

| 变量名            | 含义                    |
| ----------------- | ----------------------- |
| `bibliograph`     | 包含参考文献的 bib 文件 |
| `biblio-style`    | 参考文献风格            |
| `biblio-title`    | 参考文献标题            |
| `biblatexoptions` | biblatex 选项           |
| `natbiboptions`   | natbib 选项             |
| `csl`             | 引用和参考文献风格文件  |

使用 `--filter pandoc-citeproc` 工具来处理文献时, 会从 bib 文件中根据 markdown
提取所需要的参考文献, 再通过 CSL 文件进行剪裁后加入. 引用的语法为 `[@bibkey]`.
如果脚注上出现引用, 选择. 另外还有一个比较重要的问题是, 直接用 `pandoc-citeproc`
无法建立到文献的链接.

另一种做法是使用 `--biblatex` , 但 pandoc manual 上注明它不是面向直接转化为 pdf
的, 而是在产生 tex 文件后手动编译 tex. 为了确认这一点, 我尝试直接输出到 pdf,
发现尽管 `[@bibkey]` 引用可以正常转化成 `\cite{bibkey}`, 但实际在文档里只显示出加粗的
`[bibkey]`, 且 `\printbibliography` 指令也打印不出参考文献,
跟[这个链接描述的现象](https://tex.stackexchange.com/questions/135484/still-biblatex-will-not-print-bibliography)一模一样.
这是由于交叉引用需要执行一整套工具链, 而 pandoc 只运行一步 latex.

`biblatex` 默认使用 `biber` 为后端, 若使用 `bibtex` 来处理参考文献, 需要在元数据块中添加

```yaml
---
biblatexoptions:
- backend=bibtex
---
```

这个选项只会在 `--biblatex` 开启时有用. 另外[手册指出](https://pandoc.org/MANUAL.html#citations),
在 `--bibliography` 选项中使用 `.bibtex` 扩展名的文件时会强制使用 `bibtex` (force bibtex),
但不应该误解: 这里我仍然用的是 biblatex, 只是用 bibtex 而不是 biber 作为其后端.

参考文献和引用格式可以通过 `biblio-style` 变量设定, 比如 `-M biblio-style=nature` 选择 nature 引用风格.
可以到 [CTAN 的 biblatex-contrib](https://www.ctan.org/tex-archive/macros/latex/exptl/biblatex-contrib) 查看有哪些可用的风格, 或者在 Tex Live Utility 搜索 biblatex, 查看每个相关包的说明,
又或者查看这个 overleaf 链接:
[Biblatex citation styles](https://www.overleaf.com/learn/latex/Biblatex_citation_styles).

### 插入图表

除了直接用 makrdown 语法插入图片外, pandoc 支持属性和名称引用, 包含在花括号内

```markdown
![This is my website logo.](icon.jpg){width=50% #fig:favicon}
```

可在正文中插入 `+@fig:favicon` 以引用. 为了得到正确的交叉引用链接,
需要安装 [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) 作为过滤器.

在制作表格时, pandoc 支持单元格含多行文字的表格, 也能非常方便的调整列的对齐方式, 比如以下三列分别是左中右对齐的.

```markdown
| left | center | right |
| :--- | :----: | ----: |
| l    |   c    |     r |

Table: demo left-center-right table {#tbl:demo-tbl}
```

| left | center | right |
| :--- | :----: | ----: |
| l    |   c    |     r |

在正文中插入 `+@tbl:demo-tbl` 以引用.
类似的, 转化时用 [pandoc-tablenos](https://github.com/tomduck/pandoc-tablenos) 
过滤后才能得到正确的交叉引用链接.

## 实例: `demo.md` 到 `demo.pdf`

最后放一个用 `markdown+pandoc+xelatex+bibtex` 的实际例子, 所需文件都在[压缩包](demo.tar.gz)里.
`make` 编译需要有 pandoc 和 TeXLive 等 latex 发行版.

- `demo.md`：markdown 源文件
- `Makefile`: 产生需要的 `template.tex` 和` HW.md`, 执行 latex 工具链
- `demo.bib`: 用到的参考文献
- `icon.jpg`: 要插的图片, 就是我的网站图标啦.

作为参考, 在[这个 gist](https://gist.github.com/maxogden/97190db73ac19fc6c1d9beee1a6e4fc8)
里作者也详细介绍了如何将 markdown 转化成 paper. 但对于其中的 pizza 图片, markdown 下用的`![It's a pizza]`作为图片注释, 转化到 pdf 后图片注释却变成了 `Figure 1`. 我这里倒是没有这个问题.

另外, 由于用 html 的转化比较直接, 所需要的就是找个喜欢的 css, 就不展示了.

## 总结

本文整理了笔者在第一次尝试用 pandoc 转化 markdown 文件为 pdf 的过程中学到的技巧, 并提供了一个简单的 `pandoc+latex` 转换 pdf 的样例输入.
