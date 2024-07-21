---
title: Numerov method on linear and logarithmic grids (CN)
date: 2019-03-03 14:00:00 +0800
categories: [science, ]
tags: [Numerical Method, Python, Algorithm]
math: true
---

## 背景

[Numerov方法](https://en.wikipedia.org/wiki/Numerov%27s_method)是数值求解常微分方程(ODE)的一种方法, 适用于不含一阶项的二阶ODE

$$\begin{equation}\label{eq:numerov-ode}
y'' + f(r)y = s(r).
\end{equation}
$$

在物理上有很多方程满足这种形式, 其中与我最为相关的是薛定谔方程(SE), 更确切的是三维有心势下的径向薛定谔方程(rSE). 原子单位下, rSE写成

$$
\left[-\frac{d^2}{d r^2} + \frac{l(l+1)}{r^2} + 2V(r)\right]R_l(r) = E_lR_l(r)
$$

其中$R_l$是定义在一维实空间$r$上的波函数$u_l$与矢径长$r$的积, $R_l(r)=ru_l(r)$, $E_l$是能量, $l$是角量子数. 这个方程满足Numerov方程要求的ODE形式

$$
\begin{cases}
f(r) = -\frac{l(l+1)}{r^2} - 2V(r) + E_l \\
s(r) = 0
\end{cases}
$$

因此可以用该方法数值求解. 本文首先在两种格点方案, 均匀格点和对数格点上推导Numerov方法的核心方程, 即格点递推公式, 然后给出简单的Python实现.

## 推导

### 线性均匀格点

首先在线性均匀格点上推导一下Numerov方法. 在$r$点附近对函数$y$作Taylor展开

$$
\begin{equation}\label{eq:deriv-1}
y(r\pm h) = y(r) \pm hy'(r) + \frac{h^2}{2}y''(r) \pm \frac{h^3}{6}y'''(r) + \frac{h^4}{24}y''''(r) + \cdots
\end{equation}
$$

将正负两式相加

$$
\begin{equation}\label{eq:deriv-2}
y(r-h)+y(r+h) = 2y(r) + h^2y''(r) + \frac{h^4}{12}y''''(r) + \mathcal{O}(h^6)
\end{equation}
$$

由于

$$
y''''(r) = \frac{d^2}{d r^2}\left[f(r)y(r)-s(r)\right],
$$

定义$p(r):=f(r)y(r)-s(r), p=y'', p''=y''''$, 可以采用与式 \eqref{eq:deriv-1} \eqref{eq:deriv-2} 类似的办法处理$p$, 得到

$$
\begin{equation}\label{eq:deriv-3}
p(r-h)+p(r+h) = 2p(r) + h^2 p''(r) + \frac{h^4}{12}p''''(r) + \mathcal{O}(h^6).
\end{equation}
$$

把$p, p^{''}$表达式 \eqref{eq:deriv-3} 回代到式 \eqref{eq:deriv-2} 中,

$$
y(r-h)+y(r+h) = 2y(r) + h^2p(r) + \frac{h^4}{12}\left[p(r-h)+p(r+h)-2p(r)\right] + \mathcal{O}(h^6).
$$

稍作整理, 得到

$$
\begin{aligned}
\left[1+\frac{h^2}{12}f(r-h)\right]y(r-h) +& \left[1+\frac{h^2}{12}f(r+h)\right]y(r+h) = \\
&2\left[1+\frac{h^2}{12}f(r)\right]y(r) - h^2f(r)y(r) + \frac{h^2}{12}\left[s(r-h)+10s(r)+s(r+h)\right] + \mathcal{O}(h^6).
\end{aligned}
$$

这就是 Numerov 方法的一般方程. 特别的, 对于齐次方程, $s=0$, 式子可以化简成

$$
\left[1+\frac{h^2}{12}f(r+h)\right]y(r+h) = 2\left[1+\frac{h^2}{12}f(r)\right]y(r) - \left[1+\frac{h^2}{12}f(r-h)\right]y(r-h) - h^2f(r)y(r) + \mathcal{O}(h^6).
$$

取间距为 $h$ 的均匀格点, 此时上式化成三点递推方程,

$$
(1+\frac{h^2}{12}f_{n+1})y_{n+1} = 2(1+\frac{h^2}{12}f_n)y_n - (1+\frac{h^2}{12}f_{n-1})y_{n-1} - h^2f_n y_n
$$

精确到步长的六次方. 实际应用当中, 我们需要先确定前两个格点上的值, 然后就可以用上式推出第三点及之后所有格点上的函数值.

### 对数均匀格点

除了实空间均匀格点, 我们也可以使用对数均匀格点 (logarithmic grid), 其上第 n 个实空间格点为

$$
r_n = r_0 e^{nh}
$$

上面的 Numerov 方法不能直接用于格点$\{r_n\}$,
因为这种情况下格点 $r$ 的间距是随格点指标变化的,
但是我们可以通过代数变换使之成为可能.

首先定义变量替换$x\mapsto r$

$$
r(x) = r_0e^x
$$

及定义 $Y(x)$ 为

$$\begin{equation}\label{eq:log-trans-y}
y(r) = r_0e^{x/2}Y(x).
\end{equation}$$

从而

$$
\begin{aligned}
\frac{d^2}{d r^2}y(r) &= \frac{1}{r_0e^x}\frac{d}{dx}\left[\frac{1}{e^x}\frac{d}{d x}\left(e^{x/2}Y(x)\right)\right] \\
&=\frac{1}{r_0e^x}\left[-\frac{1}{4}e^{-x/2}Y(x) + e^{-x/2}Y''(x)\right] \\
\end{aligned}
$$

其中撇号代表对$x$求导而非$r$. 代回到式 \eqref{eq:numerov-ode} 的ODE中

$$
\begin{aligned}
\frac{1}{r_0}e^{-3x/2}\left[-\frac{1}{4}Y(x) + Y''(x)\right] + f(r)r_0e^{x/2}Y(x) &= s(r)\\
Y'' + \left[f(r)r^2_0e^{2x}-\frac{1}{4}\right]Y(x) &= r_0e^{3x/2}s(r).
\end{aligned}
$$

令

$$\begin{equation}\label{eq:log-trans-f-s}
\begin{aligned}
F(x):=&f(r)r^2_0e^{2x}-\frac{1}{4}= f(r(x))r(x)^2-\frac{1}{4} \\
S(x):=&r_0e^{3x/2}s(r) = \sqrt{\frac{r(x)^3}{r_0}}s(r(x))
\end{aligned}
\end{equation}$$

于是得到 ODE

$$
Y''(x) + F(x)Y(x) = S(x)
$$

这与原始ODE \eqref{eq:numerov-ode} 相似, 但它定义在变量$x$上而非实空间$r$上. 由于格点$x$是均匀的, 我们可以应用前面均匀格点的算法解出$Y(x)$, 然后再通过式 \eqref{eq:log-trans-y} 变换回 $y(r)$.

## Python实现

以下是忽略了s后, Numerov方法在线性格点和对数格点上的Python实现.
Numba 装饰器用于编译优化.

首先是线性均匀格点上的实现`numerov`.
这里参考了[Kristjan Haule](https://www.physics.rutgers.edu/grad/509/src_prog/hmw/Hydrogen.html)的代码.

```python
@numba.njit
def numerov(f, h, y0, dy0):
    '''Solve y''(r) + f(r)y(r)=0 by Numerov method on a linear r grid

    Args:
        f (1d-array): f
        h (float): the step size of linear grid
        y0 (float): y value at the first grid point
        dy0 (float): first-order derivaitve at the first grid point
    '''
    y = np.zeros(len(f))
    y[0] = y0
    y[1] = y0 + h * dy0
    h2 = h**2
    h2d12 = h2/12.0
    w0 = y0 * (1 + h2d12 * f[0])
    w1 = y[1] * (1 + h2d12 * f[1])
    yn = y[1]
    fn = f[1]
    for n in range(2, len(f)):
        w2 = 2 * w1 - w0 - h2 * fn * yn
        fn = f[n]
        yn = w2 / (1 + h2d12 * fn)
        y[n] = yn
        w0, w1 = w1, w2
    return y
```

然后是对数均匀格点上的实现`numerov_log`:

```python
@numba.njit
def numerov_log(r, f, y0, dy0):
    '''Solve y''(r) + f(r)y(r) = 0 by Numerov method on a logarithmic r grid

    Args:
        r (1d-array): the logarithmic grid
        f (1d-array)
        y0 (float): y at the first grid
        dy0 (float): first-order derivaitve at the first grid
    '''
    r0 = r[0]
    # calculate F(x)
    F = np.multiply(f, np.power(r, 2)) - 0.25E0
    x = np.log(r/r0)
    # step size in x
    hx = x[1] - x[0]
    # convert boundary condition of y to Y
    Y0 = y0 / r0
    dY0 = - Y0/2 + dy0 * r0
    # call Numerov on linear grid x
    Y = numerov(F, hx, Y0, dY0)
    return Y * np.sqrt(r * r0)
```

## 总结

本文在两种数值格点(均匀格点和对数格点)上推导了Numerov方法的递推方程,
给出了简单的Python实现.

