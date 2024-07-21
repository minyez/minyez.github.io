---
title: 用 GNU/Make 构建项目 - 以一个质数判断代码为例
date: 2017-10-12 19:41:20 +0800
categories: [programming, ]
tags: [GNU/Make]
comment: false
math: true
---

本文从编译一个简单的质数判断程序入手, 介绍如何利用 GNU/Make 方便地编译较复杂的代码项目。

## 背景

### 目标

如果我们希望用 C 语言实现判断一个从外部输入的正整数 `a` 是否是质数的程序(要求
`a` 小于一预设值 `intmax`), 那么我们需要在程序中实现以下功能：

- 读取外部输入`a`，并判断`a`是否为整数且小于`intmax`;
- 求不大于`a`的平方根的正整数`b`；
- 判断是否存在小于等于`b`且不等于 1 的整数`c`能整除`a`。若存在，则`a`为合数，否则为质数。

### 实现

上述功能由三个函数实现，分别保存在三个.c 文件中，由 main.c 中`main()`统一调用。各函
数功能见表格，具体代码见最后一节附录。通过编译.c 产生.o 文件，然后将所有.o 链接起来，
产生可执行程序`prime`。注意到这里需要`math.h`中的函数`sqrt`，因此需要用`-lm`链接
数学库。

| 文件名     | 函数名    | 形参  | 功能                                 | 返回值  |
|------------|-----------|-------|--------------------------------------|---------|
| main.c     | `main`    |       | 流程控制                             |         |
| read\_a.c  | `read_a`  |       | 从外部读取`a`                        | `a`; -1 |
| isqrt.c    | `isqrt`   | `a`   | 求不大于$\sqrt{\texttt{a}}$的整数`b` |         |
| judge\_p.c | `judge_p` | `a,b` | 循环判断`a`是否质数                  |         |
| prime.h    |           |       | 头文件, 声明函数                     |         |

## GNU/Make 基本

### 什么是`make`

比较大的工程通常包含很多源文件，需要逐个编译并链接才能得到目标执行程序。手动编译
和链接不仅操作麻烦，每次链接时还要重新输入所有目标文件以及需要的函数库，浪费时间
精力。`make`是一种帮助我们自动编译与构建大型工程的工具。通过将**规则（rule）**写
入 Makefile 文件，`make`就会根据规则中的依赖关系逐层编译目标文件，最后链接得到执行
程序。`make`在 Linux 上的标准实现是 GNU/Make，以下所有`make`指令均为 GNU make。

事实上，除了编译程序外，`make`也可以帮助我们完成其他的工作，具体内容由规则决定。

### 规则

`make`需要 Makefile 来告诉它以什么样的顺序去编译和链接程序。Makefile 中最核心的概念是规则，一个 Makefile 里可以包含多个规则。规则一般写成如下形式

```makefile
[目标]: [前提]
	[命令 1]
	# ...
	[命令 n]
```

其中

- **目标文件（Target）**可以是一个.o 文件，或者可执行程序，也可以仅仅是一个标签
  （比如 clean 目标是清除所以已编译的.o 文件和可执行程序）。
- **前提文件（Prerequisites）**是完成该目标所需要的文件或者目标。目标文件和前提
  文件之间用冒号分开。命令（Command）为该目标下执行的 Shell 命令，**必须**用 Tab
  对命令缩进。这一系列命令统一称为规则的 recipe。如果你不喜欢用 Tab 缩进，那么需
  要修改`.RECIPEPREFIX`换成你想要的符号。比如

```makefile
.RECIPEPREFIX := :
all:
	:@echo "Recipe prefix symbol set to $(.RECIPEREFIX)"
```

### `make`运行机制

在命令行输入`make`后,一般会按次序发生以下事件：

1. `make`在当前文件夹下搜索 Makefile 和 makefile（GNU make 还会包括 GNUmakefile）
   文件并读取。搜寻顺序是 GNUmakefile、makefile、Makefile，先找到哪个文件读哪个；
2. 找到 Makefile 后，读取 Makefile 中`include`包含的文件；
3. 初始化变量值，展开所有需要立即展开的变量；
4. 以第一个规则中的目标作为最终目标，根据最终目标以及依赖关系，建立依赖关系列表；
5. 执行除最终目标以外的所有目标的规则：规则中前提文件不存在，或者前提文件比目标文件新，则执行规则下的命令重建目标；
6. 执行最终目标所在规则。

## Makefile 具体写法

接下来以构造可执行程序`prime`为例，讲解 Makefile 的写法和`make`的运行。

### 最直接的 Makefile

```makefile
prime: read_a.o isqrt.o judge_p.o main.o
	gcc -o prime read_a.o isqrt.o main.o judge_p.o -lm

read_a.o: read_a.c
	gcc -c read.c

isqrt.o: isqrt.c
	gcc -c isqrt.c

judge_p.o: judge_p.c
	gcc -c judge_p.c

main.o: main.c
	gcc -c main.c

clean:
	rm -f prime read_a.o isqrt.o judge_p.o  main.o
```

此时在命令行输入

```shell
make
```

即可编译所有.o 文件和`prime`。基本流程是：

1. 确定最终目标 "prime"，确认前提文件.o 是否存在；
2. 初始时.o 文件均未编译，因此`make`搜寻以 read.o 为目标的规则。这一规则只依赖于
   read\_a.c，而 read\_a.c 存在，因而执行该规则内的指令`gcc -c read_a.c`, 编译得
   到`read_a.o`；
3. 同上，编译`isqrt.o, judge_p.o`和`main.o`；
4. `.o`全部编译完成后，回到`prime`目标执行链接的命令，产生可执行程序`prime`。

注意，`make`只会执行第一个规则，如果把 prime 放到后面，那么`make`将只会编译`read_a.c`，此时需要输入
```shell
make prime
```
在`make`后加上`-d`选项，可以查看`make`运行的具体流程
```shell
make -d
```

### 改进 Makefile

#### 定义显式变量

在 Makefile 中定义变量`objects`

```makefile
objects = read_a.o isqrt.o judge_p.o main.o
```

用`$()`展开`objects`可以得到所有目标。

#### 利用预定义隐式规则

`make`对一系列程序的编译预定义了隐式规则，例如 C 程序编译的隐式规则为

```makefile
$(CC) -c main.c $(CFLAGS) $(CPPFLAGS)
```

且自动包含`.c`文件为前提文件。其中`CC,CFLAGS`和`CPPFLAGS`是`make`针对 C 程序编译的内建变量，其他的还有`CXX,FC,FFLAGS,LDFLAGS`等等。因此 Makefile 可以进一步简化为

```makefile
objects = read_a.o isqrt.o judge_p.o main.o

prime: $(objects)
	gcc -o prime $(objects) -lm

.PHONY: clean
clean:
	rm -f prime $(objects)
```

事实上在`main.o`中我们省去了`prime.h`，这是因为它被包含在`main.c`中，`make`会将其自动加入前提文件。从而显式规则只剩下以`prime`和`clean`为目标的规则。

这里用`.PHONY`声明 **伪规则（Phony rules）**, 里面包含 `clean` 以避免执行 `make` 时以 `clean` 作为最终目标。
在这里并不是必要的，因为第一个目标是`prime`。但当工程较大、规则较多较杂时，声明伪规则可以避免不必要的问题。

#### 修改内置变量

`CC,CFLAGS,CXX,FC,FFLAGS,LDFLAGS` 等等是 `make` 中内置的变量，在隐式规则中使用。
我们同样可以修改它们，配合 `%` 匹配来自定义程序编译的隐式规则。
例如在 `makefile.include` 里定义

```makefile
CC = icc
CFLAGS = -Wall -g
LDFLAGS = -lm
```

此时.o 文件的隐式规则中执行的命令实际就变成了

```shell
icc -c -o main.o main.c -Wall -g
```

在目标`prime`的规则中，用`$(LDFLAGS)`变量来包含数学库，编译器`$CC`

```makefile
prime:
	$(CC) -o prime $(objects) $(CFLAGS) $(LDFLAGS)
```

#### 模式规则

我们看到对于.o 文件我们可以利用隐式规则来编译，但是当我们需要使用比较复杂的编译选项时，隐式规则就不适用了。此时可以利用%进行模式匹配来定义隐式规则，如`prime.h`在`include`文件夹内，需要用`-I`选项将该文件夹加入头文件搜索路径

```makefile
INC= -I./include
%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS) $(INC)
```

其中`%.o: %.c`等价于以`stem.c`为前提产生目标文件`stem.o`。这样的规则称为模式规则(Pattern
rule)。我们可以用这种方法自定义执行命令，使之符合我们的需求。

#### 自动变量

上面的命令中用到的`$@`和`$<`是`make`的一个特殊功能，称为自动变量（automatic variable）。`make`中常用的自动变量见下表

| 自动变量 | 含义                                   |
| -------- | -------------------------------------- |
| `$@`     | 目标文件名                             |
| `$<`     | 第一个前提文件的名字                   |
| `$^`     | 所有前提文件，以空格分隔               |
| `$?`     | 所有比目标文件新的前提文件，以空格分隔 |

#### 通配符

包括一般的 Shell 通配符, 如`*,?,[],[!]`。例如`clean`目标中

```makefile
clean:
	rm -f prime *.o
```

此外更为常用的通配符是 wildcard 和 patsubst 函数. 使用 wildcard 函数扩展通配符以及 patsubst 函数替换通配符。patsubst 需要３个参数，第一个是个需要匹配的式样，第二个表示用什么来替换它，第三个是个需要被处理的由空格分隔的字列。以下`objects`定义的方法与显式定义等价

```makefile
sources = $(wildcard *.c)
objects = $(patsubst %.c,%.o,$(sources))
```

第一个`%`匹配非空字符串，每次匹配的字符串叫做"柄"（stem），第二个`%`将被解读为第一参数所匹配的柄。该命令中，`patsubst`将`$(sources)`中的`.c`文件列表替换成对应的`.o`文件。这里的`%`不能用`*`来代替。

### include 外部文件

创建`makefile.include`文件，在里面定义变量：

```makefile
# makefile.include
sources = $(wildcard *.c)
objects = $(patsubst %.c,%.o,$(sources))
CC      = icc
CFLAGS  = -Wall -g
LDFLAGS = -lm
INC     = -I./include
```

在 Makefile 里加入`include`指令把 makefile.include 中的变量包含进来。此时 Makefile 写成

```makefile
include makefile.include

prime: $(objects)
	$(CC) -o prime $(objects) $(CFLAGS) $(LDFLAGS)

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS) $(INC)

.PHONY: clean
clean:
	rm -f prime *.o
```

#### 条件语法

`make`支持条件控制`ifeq..else..endif`，例如

```makefile
debug=no
ifeq ($(debug),no)
    CFLAGS += -O3
else
    CFLAGS += -O0
endif
```

直接用`make`编译时将默认执行激进的 O3 优化。可在命令行增加宏 debug 定义来覆盖 Makefile 里定义好的值，如

```bash
make debug=yes
```

此时不会对程序进行优化。这样方便随时调试和比较优化带来的效率改进。

## 附录

### 代码附录

`main.c`

```c
/* decide if an integer a is a prime number */
#include "prime.h"

int main()
{
    int a,b;
    a = read_a();
    b = isqrt(a);
    judge_p(a,b);
    return 0;
}
```

`read_a.c`

```c
#include "prime.h"
#define intmax 100
int read_a()
{
    int a;
    printf(" Type the number a (4<=a<%d): ",intmax);
    scanf("%d",&a);
    if (a < 4 || a > intmax)
    {
        printf("%d is not in range. Exit\n",a);
        exit(1);
    }
    else
        return a;
}
```

`isqrt.c`
```c
#include "prime.h"
int isqrt(int a)
{
    int t;
    t = sqrt(a);
    return t;
}
```

`judge_p.c`
```c
#include "prime.h"
void judge_p(int a, int a_sqrt)
{
    int i;
    for (i=2;i<=a_sqrt;i++)
    {
        if (a%i == 0)
        {
            printf(" %d is not prime.\n",a);
            break;
        }
    }
    if (i==(a_sqrt+1))
        printf(" %d is prime.\n",a);
}
```

`prime.h`
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef __FUNC_H
#define __FUNC_H
int read_a();
int isqrt(int a);
void judge_p(int a,int b);
#endif
```

### TeX 文件编译的 Makefile 举例

```makefile
# 编译 about_make.tex
FILE = about_make.tex
TEX  = xelatex

all:
	$(TEX) $(FILE);
	$(TEX) $(FILE); # 需要连续编译两次以获得交叉引用的编号
```

## Reference
GNU manual of make: <https://www.gnu.org/software/make/manual/make.html>
