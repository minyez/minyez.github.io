---
author: Min-Ye Zhang
bibliography:
- etc/bibliography.bib
categories: science
comments: true
documentclass: article
header-includes:
- 
- 
- 
- 
math: true
tags:
- Numerical method
- 
title: Gaussian quadrature
---









## Introduction

Numerical integration of function is pervasive in scientific
computations. It is also termed as quadrature and is generally evaluated
on discretized grids. The simplest example would be

$$\begin{equation}
I = \int^1_{-1}\dd{x} f(x) \approx \sum^N_{n=1} w_n f(x_n)
\end{equation}$$

where $x_n \in [-1,1]$ with integration weights $w_n$. An $N$-point grid
with fixed $\\{x_n\\}$ points can be constructed to ensure exact
integration for functions with Taylor polynomials up to order $N-1$.
This can be shown by comparing the expansion of the exact and
approximated forms:

$$\begin{equation}\label{eq:gq-proof-1}
\begin{aligned}
I \equiv& \int^1_{-1}\dd{x} f(x)
= \int^1_{-1}\dd{x} \sum^{\infty}_{p=0} \frac{f^{(p)}(0)}{p!} x^{p}
= \sum^{\infty}_{p=0} \frac{f^{(p)}(0)}{p!} \int^1_{-1}\dd{x} x^{p} \\
\approx& \sum^N_{n=1} w_n f(x_n)
= \sum^N_{n=1} w_n \sum^{\infty}_{p=0} \frac{f^{(p)}(0)}{p!} x^{p}_{n}
= \sum^{\infty}_{p=0} \frac{f^{(p)}(0)}{p!} \sum^N_{n=1} w_n x^{p}_{n}
\end{aligned}
\end{equation}$$

It is exact if for any $p\in\mathbb{N}$, there exists

$$\begin{equation}\label{eq:gq-proof-2}
\sum^N_{n=1} w_n x^{p}_{n} = \int^1_{-1}\dd{x} x^{p}
\end{equation}$$

For a fixed $\\{x_n\\}$, this is equivalent to solving a set of linear
equations for $\\{\omega_n\\}$. A unique solution can be found when $p$
is truncated at $N-1$, i. e. $N$ equations for $N$ variables.

If we relax the constraint of fixed nodes $\\{x_n\\}$ and treat them as
unknown variables, the degrees of freedom becomes $2N$ and $p$ needs to
go to $2N-1$. This leads to a better estimate of an integral, as it now
can integrate exactly polynomials up to order of $2N-1$. It is proposed
by Gauss and hence called Gaussian quadrature.

## Gauss-Legendre quadrature

To determine the nodes $\\{x_n\\}$ and weights $\\{w_n\\}$ for Gaussian
quadrature, we consider the integration of polynomials up to $2N-1$
order. Such function can be written in the following form

$$\begin{equation*}
f(x) = Q(x) P_N(x) + R(x)
\end{equation*}$$

where $P_N(x)$ is the $N$-th-order Legendre polynomial, and $Q(x)$ and
$R(x)$ are general polynomials of $N-1$ or less order. According to the
orthogonality of Legendre polynomials

$$\begin{equation}
\int^1_{-1}\dd{x} P_{i}(x) P_{j}(x) = \frac{2}{2i+1}\delta_{ij},
\end{equation}$$

$P_N$ is orthogonal to $Q$ and $R$, therefore the formal integral

$$\begin{equation*}
I \equiv \int^1_{-1}\dd{x} f(x) = \int^1_{-1}\dd{x} \left[Q(x) P_N(x) + R(x)\right] = \int^1_{-1}\dd{x} R(x)
\end{equation*}$$

For the $n$-series, we assign the roots of $P_{N}(x)$ to $\\{x_n\\}$, so
that $P_N(x_n) = 0, \forall n = 1, \cdots N$

$$\begin{equation*}
\sum^N_{n=1} w_n f(x_n)
= \sum^N_{n=1} w_n \left[Q(x_n)P_N(x_n) + R(x_n)\right]
= \sum^N_{n=1} w_n R(x_n)
\end{equation*}$$

These two equations are the same as Eq. \eqref{eq:gq-proof-1} except
with $R(x)$ rather than $f(x)$. Since now the nodes are settled down, we
only have to solve the weights. They can be solved by letting

$$\begin{equation*}
f(x) = \frac{P_N(x)P'_{N}(x)}{x - x_n}
\end{equation*}$$

where $x_n$ is the $n$-th root of $P_N(x)$, and $P'_N$ being its
derivative. Insert it to the $n$-series

$$\begin{equation*}
\begin{aligned}
\sum^N_{n'=1} w_{n'} f(x_{n'})
=& \sum^N_{n'=1, n'\ne n} w_{n'} \frac{P_N(x_{n'})P'_{N}(x_{n'})}{x_{n'} - x_n} + w_n \lim_{x\to x_n} \frac{P_N(x)P'_{N}(x)}{x - x_n}
\end{aligned}
\end{equation*}$$

Each term in the summation over $n\ne n'$ is zero as we have chosen
$\\{x_n\\}$ be the roots of $P_{N}$ and the denominator is nonzero. The
limit, using L'Hospital's rule, is

$$\begin{equation*}
\begin{aligned}
\lim_{x\to x_n} \frac{P_N(x)P'_{N}(x)}{x - x_n}
= \lim_{x\to x_n} \left[P_N(x)P'_{N}(x)\right]'
= P'_N(x_n)P'_{N}(x_n) + P_N(x_n)P''_{N}(x_n)
= \left[P'_N(x_n)\right]^{2}
\end{aligned}
\end{equation*}$$

Therefore

$$\begin{equation}\label{eq:glq-proof-1}
\sum^N_{n'=1} w_{n'} f(x_{n'}) = w_n\left[P'_N(x_n)\right]^{2}
\end{equation}$$

On the other hand, the integral

$$\begin{equation*}
\begin{aligned}
\int^1_{-1}\dd{x} f(x) =& \int^1_{-1}\dd{x} \frac{P_N(x)P'_{N}(x)}{x - x_n}
= \int^1_{-1}\dd{\left[P_N(x)\right]} \frac{P_N(x)}{x - x_n} \\
=& \left.\frac{P^2_N(x)}{x - x_n} \right|^1_{-1} - \int^1_{-1} P_N(x) \dd{\frac{P_N(x)}{x - x_n}} \\
\end{aligned}
\end{equation*}$$

For the second term, as $x_n$ is a root of $P_N$, $P_N(x)/(x-x_n)$ must
be a polynomial of order $N-1$. Taking derivative will lead to a
polynomial of order $N-2$ in the integrand, which can always be
expressed as a linear combination using Legendre polynomials of order no
more than $N-2$. Thus the integral vanishes due to their orthogonality
with $P_N$, and

$$\begin{equation}\label{eq:glq-proof-2}
\begin{aligned}
\int^1_{-1}\dd{x} f(x)
=& \left.\frac{P^2_N(x)}{x - x_n} \right|^1_{-1}
= \frac{P^2_N(1)}{1-x_n} + \frac{P^2_N(-1)}{1+x_n}
= \frac{2}{1-x^2_n}
\end{aligned}
\end{equation}$$

where we have used the property of Legendre polynomials:
$P_N(1)=1, P_{N}(-1) = (-1)^N$. Equating Eqs. \eqref{eq:glq-proof-1} and
\eqref{eq:glq-proof-2} results in

$$\begin{equation}
w_{n} = \frac{2}{\left(1-x^2_n\right)\left[P'_N(x_n)\right]^{2}}
\end{equation}$$

which is the desired weight.

Gauss-Legendre quadrature is available in SciPy. The roots and weights
can be obtained by calling `roots_legendre` in the `scipy.special`
module. Below is an example to integrate $6x^8 + 4x^2 - 1$. The exact
integral between $[-1,1]$ is 2.

``` python
import scipy
import numpy as np

def f(x):
    return 6. * x ** 8 + 4. * x ** 2 - 1.

for n in [2, 3, 4, 5, 6]:
    xs, ws = scipy.special.roots_legendre(n)
    integral = np.sum(ws * f(xs))
    print("N = {:d}, 2N-1 = {:2d}, integral = {:.10f}"
          .format(n, 2 * n - 1, integral))
```

``` example
N = 2, 2N-1 =  3, integral = 0.8148148148
N = 3, 2N-1 =  5, integral = 1.5306666667
N = 4, 2N-1 =  7, integral = 1.9303401361
N = 5, 2N-1 =  9, integral = 2.0000000000
N = 6, 2N-1 = 11, integral = 2.0000000000
```

## Extension to any interval

For any function $f$ defined on closed interval $[a,b]$, we can do the
following change of variables

$$\begin{equation}
x = \frac{b-a}{2}t + \frac{a+b}{2},
\end{equation}$$

therefore

$$\begin{equation*}
I = \int^b_a\dd{x} f(x) =
\frac{b-a}{2}
\int^1_{-1}\dd{t} f(\frac{b-a}{2}t + \frac{a+b}{2}) =
\frac{b-a}{2}
\int^1_{-1}\dd{t} g(t).
\end{equation*}$$

The $t$ integral can then be approximated by the Gauss-Legendre
quadrature

$$\begin{equation*}
\begin{aligned}
I \approx& \frac{b-a}{2} \sum^{N}_{n=1} w_n g(x_n)
= \sum^{N}_{n=1} \left(\frac{b-a}{2} w_n\right) f(\frac{b-a}{2}x_n + \frac{a+b}{2})
\end{aligned}
\end{equation*}$$

Therefore for interval $[a,b]$, the nodes and weights are mapped to

$$\begin{equation}\label{eq:glq-weights-a-b}
\begin{aligned}
w_n \to& \frac{b-a}{2} w_n \\
x_n \to& \frac{b-a}{2}x_n + \frac{a+b}{2}
\end{aligned}
\end{equation}$$

It can be also extended to some open intervals. For example,

$$\begin{equation}
x = \frac{1+t}{1-t} + c
\end{equation}$$

can be used for semi-infinite integral $[c, \infty)$. In this case,

$$\begin{equation*}
\begin{aligned}
I =& \int^{\infty}_0\dd{x} f(x)
= \int^{\infty}_0 \dd{\left(\frac{1+t}{1-t}\right)} f(\frac{1+t}{1-t} + c) \\
=& \int^{1}_{-1} \dd{t} \frac{2}{\left(1-t\right)^{2}} f(\frac{1+t}{1-t} + c)
\approx \sum^N_{n=1} \frac{2w_n}{\left(1-x_{n}\right)^{2}} f(\frac{1+x_n}{1-x_n} + c) \\
\end{aligned}
\end{equation*}$$

therefore

$$\begin{equation}\label{eq:glq-weights-c-inf}
\begin{aligned}
w_n \to& \frac{2}{\left(1-x_{n}\right)^{2}} w_n \\
x_n \to& \frac{1+x_n}{1-x_n} + c
\end{aligned}
\end{equation}$$

In practice, the semi-infinite integral can be divided into separate
regions, and each region is integrated using its own Gauss-Legendre
grids. \[[1](#citeproc_bib_item_1)\]

## See also

- [Gaussian quadrature -
  Wikipedia](https://en.wikipedia.org/wiki/Gaussian_quadrature)
- [Legendre polynomials -
  Wikipedia](https://en.wikipedia.org/wiki/Legendre_polynomials)
- [Gauss-Legendre quadrature -
  Wikipedia](https://en.wikipedia.org/wiki/Gauss-Legendre_quadrature)
- [`roots_legendre` - SciPy
  Manual](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.roots_legendre.html)

## References

<span id="citeproc_bib_item_1"></span>\[1\] R. W. Godby, M. Schlüter,
and L. J. Sham, Phys. Rev. B **37**, 10159 (1988)
<a href="https://doi.org/10.1103/PhysRevB.37.10159"
target="_blank">[DOI]</a>.
