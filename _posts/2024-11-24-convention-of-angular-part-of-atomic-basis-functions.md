---
author: Min-Ye Zhang
bibliography:
- etc/bibliography.bib
categories: science
comments: true
date: "2024-11-24 02:00:20 +0200"
description: Summary of real spherical harmonics used in different
  first-principles programs.
documentclass: article
header-includes:
- 
- 
- 
- 
math: true
tags:
- OpenMX
- FHI-aims
- PySCF
- ABACUS
- Spherical harmonics
- Atomic orbitals
title: Convention of angular part of atomic basis functions
---









## Introduction

Unlike plane-wave, atomic basis functions appear in different formats
and conventions among various *ab initio* or first-principles codes. The
most obvious difference is in the radial part, which can be Gaussian
type, Slater type or strictly localized numerical orbitals. The angular
part, however, is more subtle and often overlooked. Instead of the
complex spherical harmonics (CSH), real spherical harmonics (RSH) are
generally used as the angular part to reduce the computational cost,
each of which is a linear combination of CSH. As long as the
transformation is complete, RSH can take different conventions. For one
thing, the sign (or phase) of each function is not fixed. For the other,
each code can choose their own way to align the RSH in the same angular
momentum channel.

The choice of RSH convention should not affect the final results of
observables, but can result in difference in intermediate matrices
expanded in the atomic orbitals, such as the Hamiltonian and overlap
matrices. This sometimes makes the comparison and conversion of matrices
between different codes tricky. In this post, I will try to summarize
the conventions of RSH used in several programs with atomic basis
functions.

## Definition

Here we use Condon-Shortley (C-S) convention for

$$\begin{equation*}
Y^m_l(\theta,\phi) = (-1)^m \sqrt{\frac{2l+1}{4\pi} \frac{(l-m)!}{(l+m)!}}
P^m_l(\cos\theta) \ee^{\ii m \phi}
\equiv (-1)^m K^m_l P^m_l(\cos\theta) \ee^{\ii m \phi}
\end{equation*}$$

where $P^m_l$ is the associated Legendre polynomials without the C-S
phase $(-1)^m$,

$$\begin{equation}
P_{l}^{m}(\cos\theta)=\left(\sin\theta\right)^{m} \cfrac{d^{m}}{d (\cos\theta)^{m}}\left(P_{l}(\cos\theta)\right),
\end{equation}$$

polar angles $\theta\in[0, \pi]$, azimuth $\phi\in[0, 2\pi)$, and

$$\begin{equation}
K^m_l \equiv \sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}}
\end{equation}$$

For real spherical harmonics, we use the notation of $S^m_l$, which can
be represented by CSH as

$$\begin{equation}
S^m_l = \sum_{mm'} Y^{m'}_l \Delta^l_{m'm},
\end{equation}$$

where

$$\begin{equation}
\Delta^l_{m'm} = \braket{Y^{m'}_l}{S^m_l}
\end{equation}$$

is the unitary transformation matrix from $\\{Y^m_l\\}$ to
$\\{S^m_l\\}$. For positive $m$, the polar angle part has the following
parity of $m$

$$\begin{equation}
\begin{aligned}
K^{-m}_l P^{-m}_l =& \sqrt{\frac{2l+1}{4\pi}\frac{(l+m)!}{(l-m)!}} P^{-m}_l \\
=& \sqrt{\frac{2l+1}{4\pi}\frac{(l+m)!}{(l-m)!}} (-1)^m \frac{(l-m)!}{(l+m)!} P^m_l \\
=& (-1)^m K^m_l P^m_l \\
\end{aligned}
\end{equation}$$

Hence

$$\begin{equation}
\begin{aligned}
Y^{-m}_l(\theta,\phi) =& (-1)^m K^{-m}_l P^{-m}_l(\cos\theta) \ee^{-\ii m \phi} \\
=& (-1)^m \left[(-1)^m K^{m}_l P^{m}_l(\cos\theta) \ee^{\ii m \phi}\right]^{*} \\
=& (-1)^m Y^{m *}_l(\theta,\phi)
\end{aligned}
\end{equation}$$

From this we can derive the real and imaginary parts

$$\begin{equation}\label{eq:ylm-re}
\begin{aligned}
\mathrm{Re} Y^{m}_l =& \frac{1}{2}\left[ Y^{m}_l + Y^{m*}_l \right] =
\frac{1}{2}\left[Y^{m}_l + (-1)^m Y^{-m}_l \right]
\end{aligned}
\end{equation}$$

$$\begin{equation}\label{eq:ylm-im}
\begin{aligned}
\mathrm{Im} Y^{m}_l =& \frac{1}{2\ii}
\left[Y^{m}_l - Y^{m*}_l \right]
= \frac{1}{2\ii}
\left[Y^{m}_l - (-1)^m Y^{-m}_l \right]
\end{aligned}
\end{equation}$$

## Conventions in different codes

### FHI-aims

Appendix J of [FHI-aims](https://fhi-aims.org/) manual mentions that a
partly C-S phase is adopted in the code (computed using
`src/basis_set/SHEval.f90`)

$$\begin{equation}
S_l^{m} =
\begin{cases}
\sqrt{2} K^{\abs{m}}_l \sin(\abs{m}\phi) P^{\abs{m}}_l(\cos\theta) & m < 0 \\
K^m_l P^m_l(\cos\theta) & m = 0 \\
(-1)^{m} \sqrt{2} K^m_l \cos(m\phi) P^m_l(\cos\theta) & m > 0 \\
\end{cases}
\end{equation}$$

Its equivalent expression as mentioned in the comments of
`src/external/ylm_real.f90` is

$$\begin{equation}
S_l^{m} =
\begin{cases}
-\sqrt{2} \mathrm{Im} Y^m_l & m < 0 \\
Y^0_l & m = 0 \\
\sqrt{2} \mathrm{Re} Y^m_l & m > 0\\
\end{cases}.
\end{equation}$$

Using Eqs. \eqref{eq:ylm-re} and \eqref{eq:ylm-im}, we can obtain the
transformation from CSH

$$\begin{equation}\label{eq:csh-trans-aims}
S_l^{m} =
\begin{cases}
\frac{\ii}{\sqrt{2}} \left[ Y^m_l - (-1)^m Y^{-m}_l \right] & m < 0 \\
Y^0_l & m = 0 \\
\frac{1}{\sqrt{2}} \left[ Y^m_l + (-1)^m Y^{-m}_l \right]  & m > 0\\
\end{cases},
\end{equation}$$

Basis functions in the same shell and *l* channel are aligned with
ascending azimuth quantum number, i. e. -*l*, -(*l*-1), ..., -1, 0, 1,
2, ..., *l*.

### ABACUS

The real spherical harmonics in
[ABACUS](https://abacus.ustc.edu.cn/main.htm) are defined as (from Sec.
3.2.1 of Chen Liao\'s thesis)

$$\begin{equation}\label{eq:csh-trans-abacus}
S^m_l =
\begin{cases}
\frac{\ii}{\sqrt{2}} \left[ (-1)^m Y^m_l - Y^{-m}_l \right] & m < 0 \\
Y_l^0 & m = 0 \\
\frac{1}{\sqrt{2}} \left[ Y^m_l + (-1)^m Y^{-m}_l \right] & m > 0 \\
\end{cases}
\end{equation}$$

Comparing with \eqref{eq:csh-trans-aims}, we can see that RSH with
$m\ge0$ are the same in ABACUS and FHI-aims, but those with $m<0$ differ
by $(-1)^m$. Furthermore, RSH in ABACUS are stored in the order of 0, 1,
-1, 2, -2, ..., which is different from FHI-aims.

### OpenMX

From [this
thread](https://www.openmx-square.org/forum/patio.cgi?mode=view&no=2871)
of the [OpenMX](https://www.openmx-square.org/) forum, it seems that
OpenMX uses the RSH defined on the [wikipedia
page](https://en.wikipedia.org/wiki/Spherical_harmonics#Real_form)

$$\begin{equation}\label{eq:csh-trans-wiki}
S^m_l =
\begin{cases}
\frac{\ii}{\sqrt{2}} \left[ Y^m_l - (-1)^m Y^{-m}_l \right] & m < 0 \\
Y_l^0 & m = 0 \\
\frac{1}{\sqrt{2}} \left[ (-1)^m Y^m_l + Y^{-m}_l \right] & m > 0 \\
\end{cases}
\end{equation}$$

With this convention, RSH in OpenMX differ from those in ABACUS, i.e. Eq
\eqref{eq:csh-trans-abacus}, by the Condon-Shortley phase $(-1)^m$. RSH
in OpenMX are same as those in FHI-aims for $m<0$, but differ by the C-S
phase for $m>0$.

The order is slightly tricky. Looking into function `Set_Comp2Real` in
`SetPara_DFT.c`, where the transformation matrix from CSH to RSH is
computed,[^1] the order of azimuth number for $l$ from 1 to 3 can be
summarized in the table below.

| array index | 0   | 1   | 2   | 3   | 4   | 5   | 6   |
|-------------|-----|-----|-----|-----|-----|-----|-----|
| *p*         | 1   | -1  | 0   |     |     |     |     |
| *d*         | 0   | 2   | -2  | 1   | -1  |     |     |
| *f*         | 0   | 1   | -1  | 2   | -2  | 3   | -3  |

For higher channels, the pattern follows that of *f* as can be derived
from the rest code in this function. Therefore, ABACUS and OpenMX have
the same order of azimuth number for $l \ge 3$.

### PySCF

As mentioned in the
[documentation](https://pyscf.org/user/gto.html#ordering-of-basis-functions),
[PySCF](https://pyscf.org) follows the same phase convention and
ordering as given in the Wikipedia (thus the same phase as OpenMX, same
ordering as FHI-aims), with single exception: for the p functions,
$p_x(1), p_y(-1), p_z(0)$ is used (same as OpenMX) instead of
$p_y(-1), p_z(0), p_x(1)$.

### ORCA

The convention of the solid spherical harmonics in ORCA is documented
[here](https://www.faccts.de/docs/orca/6.0/manual/contents/detailed/orca_2json.html#definition-of-the-real-solid-harmonic-gaussian-orbitals).
It seems to share the same order as ABACUS, but the phase and
transformation matrix from CSH are not clear at first glance.
[MOKIT](https://gitlab.com/jxzou/mokit/-/blob/master/mokit/lib/py2orca.py)
provides an `py2orca` API to call ORCA\'s utility program
[`orca_2mkl`](https://www.faccts.de/docs/orca/6.0/manual/contents/detailed/utilities.html#orca-2mkl-old-molekel-as-well-as-molden-inputs).
To fully understand the order and phase convention, I am afraid that one
has to dive into this tool.

------------------------------------------------------------------------

[^1]: <https://www.openmx-square.org/forum/patio.cgi?mode=view&no=1336>
