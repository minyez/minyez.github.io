---
title: Algorithm used in outwin in WIEN2k (CN)
date: 2019-05-24 16:14:53 +0800
categories: [scicomput, algorithm]
tags: [WIEN2k, Numerical method]
math: true
---

## 背景

outwin.f在WIEN2k各程序中出现, 它包含例程`outwin`. 之前大略知道它是用来计算原子球内的径向波函数的, 但对于其算法一直很模糊, 一方面由于它涉及相对论方程, 另一方面它除了输入参数的德语注释外一句注释也没有. 最近在研究局域基组生成的问题, 而这个例程出现频率非常高, 因此准备多啃一下这块代码.

不同SRC文件下的outwin.f版本也不尽同. SRC_nmr, SRC_lapw7等仍然使用Adams-Moulton四阶算法, SRC_lapw2对于第四个以外的格点允许用五阶算法. SRC_lapw7中的注释更多一些, 但仍然用的是四阶算法. 这里尝试对SRC_lapw7中的outwin.f源码进行解读.

## 原理

在Rydberg单位下, 具有量子数$\kappa$的大分量波函数$u(r)=G(r)/r$满足[^1]

$$
\begin{equation}\label{eq:r-GF}
\begin{aligned}
    \frac{d}{d r} G(r) &= \frac{G(r)}{r}+M(r) F(r) \\
    \frac{d}{d r} F(r) &= -\frac{F(r)}{r}+\left(\frac{\kappa(\kappa+1)}{r^{2}} \frac{1}{M(r)}-(E-V(r))\right) G(r)
\end{aligned}
\end{equation}
$$

[^1]: 参考这一篇[报告](https://users.wfu.edu/natalie/papers/pwpaw/notes/atompaw/scalarrelativistic.pdf)

其中

$$
\begin{equation}\label{eq:m}
M(r) \equiv 1+\left(\frac{\alpha}{2}\right)^{2}(E-V(r)) = 1+\frac{E-V(r)}{c^2}
\end{equation}
$$

$\alpha$为精细结构常数, 在Rydberg单位下$\alpha=2/c$, $c$为光速. 为在步长$h$的对数格点上进行数值计算, 作变量替换$r=r_0 e^x$, $\mathrm{d}r=r\mathrm{d}x$, 得到关于$x$的方程组

$$
\begin{equation}\label{eq:x-GF}
\begin{aligned}
    G' &= G + M r F \\
    F' &= - F + \left(\frac{\kappa(\kappa+1)}{rM}-r(E-V)\right) G
\end{aligned}
\end{equation}
$$

方便起见, 上式中略去了*G,F,M*的变量$r\equiv r(x)$, 撇号表示关于*x*求导.

## 源码解读

### 参数

### 行66-81

### 行83-91

从81行开始是对第四个及以后的格点的循环. `X`为*-h*, `DRDI`为*rh*. 其他一些的中间量与式 \eqref{eq:x-GF} 中量的关系是

$$
\begin{equation}
\begin{aligned}
\mathrm{PHI} &= rh\frac{E-V}{c}\\
\mathrm{U} &= rhc + \mathrm{PHI} = rhc\left[1+\frac{E-V}{c^2}\right] = rhcM \\
\mathrm{Y} &= -\kappa(\kappa+1)h^2/\mathrm{U} + \mathrm{PHI} = - \frac{h}{c}\left[\frac{\kappa(\kappa+1)}{rM} - r(E-V)\right]
\end{aligned}
\end{equation}
$$

从而可以将式 \eqref{eq:x-GF} 写成

$$
\begin{equation}\label{eq:UYGF}
\begin{aligned}
    G' &= G + \frac{\mathrm{U}}{hc}F \\
    F' &= - F - \frac{c}{h}\mathrm{Y} G
\end{aligned}
\end{equation}
$$

令$A=G, B=F/c$, $A'=G', B'=F'/c$, 得到

$$
\begin{equation}\label{eq:UYAB}
\begin{aligned}
    A' &= A + \frac{\mathrm{U}}{h}B \\
    B' &= - B - \frac{\mathrm{Y}}{h} A
\end{aligned}
\end{equation}
$$

### 行92-96

由行列式解线性方程的知识可知, 这部分求解的是这样一个矩阵方程

$$\begin{equation}\label{eq:mat-92-96}
\begin{bmatrix}
\frac{8}{3} + X & -U \\
Y & \frac{8}{3} - X \\
\end{bmatrix}
\begin{bmatrix}
A_c \\
B_c \\
\end{bmatrix}=
\begin{bmatrix}
B1 \\
B2 \\
\end{bmatrix}
\end{equation}$$

这里下标c表示在代码(code)中的定义. `B1`和`B2`在93和94行计算, 基于[Adams-Moulton算法](https://en.wikipedia.org/wiki/Linear_multistep_method#Adams%E2%80%93Moulton_methods), 因为8/3来自于四阶算法

$$
y_{n+3}=y_{n+2}+h\left(\frac{9}{24} f\left(t_{n+3}, y_{n+3}\right)+\frac{19}{24} f\left(t_{n+2}, y_{n+2}\right)-\frac{5}{24} f\left(t_{n+1}, y_{n+1}\right)+\frac{1}{24} f\left(t_{n}, y_{n}\right)\right)
$$

其中$f(t_n, y_n)=y'_n$为第n格点上y的导数. 利用上式可以将$A'_{n+3}$表示为

$$
hA'_{n+3} = \frac{8}{3}A_{n+3} - \frac{8}{3}A_{n+2} - \frac{19}{9}hA'_{n+2} + \frac{5h}{9}A'_{n+1} - \frac{h}{9}A'_n
$$

将式 \eqref{eq:UYAB} 两边乘以$h$后, 在格点$n+3$处的表达式为

$$
\begin{equation}\label{eq:n-3-UYAB}
\begin{aligned}
    \left[\frac{8}{3} - h\right]A_{n+3} - U_{n+3} B_{n+3} &= \frac{8}{3}A_{n+2} + \frac{19}{9}hA'_{n+2} - \frac{5}{9}hA'_{n+1} + \frac{1}{9}hA'_n \\
    \left[\frac{8}{3} + h\right]B_{n+3} + Y_{n+3} A_{n+3} &= \frac{8}{3}B_{n+2} + \frac{19}{9}hB'_{n+2} - \frac{5}{9}hB'_{n+1} + \frac{1}{9}hB'_n
\end{aligned}
\end{equation}
$$

如果把上式看成未知数$A_{n+3}$和$B_{n+3}$的二元一次方程, 其系数矩阵和 \eqref{eq:mat-92-96} 是相同的. 检查`DGn`和`DFn`的含义(见下面一节)以及系数`Rn`, 可以发现式子 \eqref{eq:n-3-UYAB} 右侧与`B1`和`B2`也是一致的. 因此我们定义的$A$和$B$与outwin.f中的含义是一致的.

### 行98-103

更新最外的三个点的导数值, 以用于计算下一个格点上的`B1`和`B2`. 其中`Dx1`和`Dx2`分别用`Dx2`和`Dx3`替代, 即97, 98, 101和102行, 在格点迭代的语境下很好理解. `DG3`的更新表达式

```fortran
DG3 = U*B(K) - X*A(K)
```

由式 \eqref{eq:UYAB} 和`X`等于*-h*, 可得

$$
DG3 = U_K B_K + h A_K = h(A_K + \frac{U_K}{h}B_K) = hA'_K
$$

因此`DG3`是$h$乘以A在格点K上的导数. 同理, `DF3`的更新表达式

```fortran
DF3 = X*B(K) - Y*A(K)
```

意味着$DF3 = -h B_K - Y_K A_K = h B'_K$. 因此`DF3`是$h$乘以B在格点K上的导数.

### 行107-109

这一个循环对*B*进行了scaling, $B \to cB/2= F/2=\alpha F$. 报告[^1]指出*F*与小分量有关, 但具体关系暂未推导.

### 行111-113

由于$A=G=ru$, 因此`VAL`就是最后一个格点上的波函数值. 而`SLO`的数学表示

$$
(h\frac{\mathrm{d}A}{hr\mathrm{d}x}-u)/r
=\frac{\mathrm{d}(ru)}{r \mathrm{d}r} - \frac{u}{r}
=\frac{r\mathrm{d}u}{r \mathrm{d}r} = \frac{\mathrm{d}u}{\mathrm{d}r}
$$

为波函数在边界上的导数.

## 总结

作者阅读WIEN2k v16.1版本中例程`outwin`源码并试图理解其所用到的算法.
outwin.f 中的`outwin`例程利用Adams-Moulton算法求解标量相对论方程 \eqref{eq:r-GF},
在对数格点上得到量子数$\kappa$下的大分量波函数, 以函数乘矢径长的形式存储在$A$中.

---
