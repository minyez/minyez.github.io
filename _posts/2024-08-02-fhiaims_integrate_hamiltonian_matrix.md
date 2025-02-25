---
author: Min-Ye Zhang
bibliography:
- etc/bibliography.bib
categories: science
comments: true
date: "2024-08-02 20:46:04 +0200"
description: A quick dive into the implementation.
documentclass: article
header-includes:
- 
math: true
tags:
- FHI-aims
- Grid-based integration
title: Grid-based integration for Hamiltonian matrix in FHI-aims (CN)
---



## 问题背景 {#problem}

最近需要在 [FHI-aims](https://fhi-aims.org) 里实现 Kohn-Sham DFT
本征值的各项贡献，即

$$\begin{equation}
\begin{aligned}
\epsilon_{n\bk} =& \mel{\psi_{n\bk}}{\hat{H}(\bk)}{\psi_{n\bk}} \\
=& \mel{\psi_{n\bk}}{\hat{T}(\bk) + \hat{V}_{\mathrm{H}}(\bk) + \hat{V}_{\mathrm{ext}}(\bk) + \hat{V}^{\mathrm{local}}_{\mathrm{xc}}(\bk) + \hat{V}^{\mathrm{HF}}_{\mathrm{x}}(\bk) }{\psi_{n\bk}} \\
\equiv& t_{n\bk} + v_{\mathrm{H}, n\bk} + v_{\mathrm{ext}, n\bk} + v^{\mathrm{local}}_{\mathrm{xc}, n\bk} + v^{\mathrm{HF}}_{\mathrm{x}, n\bk}
\end{aligned}
\end{equation}$$

每一项可以由 SCF 收敛本征态的展开系数和算符表示得到

$$\begin{equation}
A_{n\bk} = \mel{\psi_{n\bk}}{\hat{A}(\bk)}{\psi_{n\bk}}
= \sum_{ij} c^{i*}_{n}(\bk) \braket{\varphi_{i}(\bk)}{\hat{A}(\bk)\varphi_{j}(\bk)} c^{j}_{n}(\bk)
= \sum_{ij} c^{i*}_{n}(\bk) A_{ij}(\bk) c^{j}_{n}(\bk)
\end{equation}$$

展开系数很容易获得，但除了最后一项 Fock
交换外四个倒空间矩阵都沒有现成的数组可供使用， 要单独构造。
而倒空间矩阵由实空间矩阵作傅里叶变换得到

$$\begin{equation}
\begin{aligned}
A_{ij}(\bk) = \sum_{\bR} \ee^{\ii\bk\cdot\bR} \braket{\varphi_{i,\mathbf{0}}}{\hat{A}\varphi_{j,\bR}}
= \sum_{\bR} \ee^{\ii\bk\cdot\bR} A_{ij,\bR}
\end{aligned}
\end{equation}$$

其中

$$\begin{equation}\label{eq:real-space-int}
\begin{aligned}
A_{ij,\bR} = \braket{\varphi_{i,\mathbf{0}}}{\hat{A}\varphi_{j,\bR}} = \int\dd{\br} \varphi_{i,\mathbf{0}}(\br) A(\br) \varphi_{j,\bR}(\br)
\end{aligned}
\end{equation}$$

$\varphi_{i,\mathbf{0}}$ 代表中心晶胞中的基函数 i, $\varphi_{j,\bR}$
代表距离中心晶胞位矢为 $\bR$ 的晶胞中的基函数 j.
这个变换是有通用接口可以调用的。 因此问题就落到了构造实空间矩阵
$A_{ij,\bR}$ 上。

作为数值原子基程序，FHI-aims 采用格点积分的方法， 取离散的实空间格点
$\\{\br_{p}\\}$ 来逼近积分式 \eqref{eq:real-space-int}.

$$\begin{equation}
\begin{aligned}
A_{ij,\bR} \approx \sum_{p} w_{p} \varphi_{i,\mathbf{0}}(\br_{p}) A(\br_{p}) \varphi_{j,\bR}(\br_{p})
\end{aligned}
\end{equation}$$

$\\{w_{p}\\}$ 是每个格点的权重。总 Hamiltonian 实空间矩阵的格点积分是由
`integrate_real_hamiltonian_matrix_p2`
实现的。只需要理解它，就可依葫芦画瓢， 分别构造四个算符的矩阵形式。

## 参数 {#arguments}

`integrate_real_hamiltonian_matrix_p2`, 有以下参数：

-   `hartree_potential_std`: 格点 Hartree 势。 周期边界条件下的格点
    Hartree 势包含了 nu-el 和 el-el 两部分， 即将 $V_{\mathrm{H}}$ 和
    $V_{\mathrm{ext}}$ 放在了一起。 以下仍然使用 $V_{\mathrm{H}}$
    来表示这一项。
-   `rho_std`: 格点电子密度。
-   `rho_gradient_std`: 格点电子密度梯度。
-   `kinetic_density_std`: 动能密度，用于 meta-GGA.
-   `partition_tab_std`: 格点的积分权重即 $\\{w_p\\}$。 在 FHI-aims
    里称为 partition function, 要区别于统计力学中的配分函数。
-   `basis_l_max`: 各元素基函数的最大角动量值。
-   `en_xc`: 交换关联总能量。
-   `en_pot_xc`: 交换关联势能。
-   `hamiltonian`: 稀疏格式的实空间哈密顿量。
-   `en_vdw`: 范德华作用总能。
-   `en_pot_vdw`: 范德华作用势能。

其中有五个输出参数。 `en_xc`, `en_pot_xc`, `en_vdw` 和 `en_pot_vdw`
是浮点数输出。 `hamiltonian` 是以稀疏格式存储的
$H_{\sigma,ij}(\mathbf{R})$, 包含了基函数、自旋和周期单胞的格矢指标。

格点相关的数组参数，最后一维都是 `(n_full_points)`. `rho_std` 和
`kinetic_density_std` 前置维度 `(n_spin)`, `rho_gradient_std` 前置维度
`(3,n_spin)`

## 流程 {#workflow}

为了提高并行计算效率，aims 当中有一些全局的流程控制变量，例如 `use_gpu`,
`use_local_index`, `use_load_balancing`, `use_batch_permutation` 和
`use_scalapack` 等，用来控制中间数组和输出数组的大小和指标范围。
这里先以上述变量均为 `.false.`
时这一最简单的例子来说明，且只考虑标量相对论 (ZORA) 情形。
其中有一些矩阵是 TDDFT 相关的，暂时也不考虑。

FHI-aims 的实空间格点积分是分批次计算的 (batch-based integration).
 \[[1](#citeproc_bib_item_1),[2](#citeproc_bib_item_2)\] 每个 batch
包含一定数量的实空间格点，抽象为一个衍生类 `batch_of_points`. 循环时以
batch 为最外层循环进行，每次计算这批格点对矩阵元的贡献，加总到
Hamiltonian 上。 Hamiltonian 的维数和每个进程需要处理的 batch
根据并行设置的不同而有所差别，但整体流程是一样的。

具体流程如下：

1.  分配临时数组。
2.  对进程上 batch $\mathbb{B}$ 循环:
    1.  计算 batch 内所有点到基组中心的距离
        (`tab_atom_centered_coords_p0`)
    2.  筛选[相关基函数](#relevant-basis) (`prune_basis_p2`),
        确定这些基函数的中心 (`collect_batch_centers_p2`)
    3.  当需要计算的基组数大于 0 时，对 batch 内格点
        $\mathbf{r}_{p} \in \mathbb{B}$ 循环
        1.  筛选相关的径向函数，并返回径向函数的样条插值表
            (`prune_radial_basis_p2`). 下面的操作仅对这些相关函数进行。

        2.  计算格点到基函数的位矢，并求方位角的三角函数表
            (`tab_local_geometry_p2` 和 `tab_trigonom_p0`)

        3.  <span id="mark1"></span>由样条插值，计算径向函数上在该格点的值
            $u_{i}(\abs{\br_{p} - \boldsymbol{\tau}_{I}})$
            (`evaluate_radial_functions_p0`)

        4.  进一步由角量子数，计算基函数在该格点上的值
            $\varphi_{i}(\br_{p})$, 保存在 `wave` 中用于左乘。
            (`evaluate_waves_p2`)

        5.  计算该格点的 XC 能量密度、XC 势 local
            部分、密度梯度偏导和动能密度偏导 (`evaluate_xc`).

        6.  构造该点的局域势 `local_potential_parts`

            $$\begin{equation}
                       \begin{aligned}
                       v_{\mathrm{H}}(\br_p) + v_{\sigma,\mathrm{xc}}(\br_p) + v_{\mathrm{vdW}}(\br_p)
                       \end{aligned}
                       \end{equation}$$

            “局域”指只与该格点电子密度有关。

        7.  若打开了 GGA, 计算径向函数和函数在格点上的导数。
            前者用的是和 [2.3.3](#mark1) 一样的子程序，后者用的
            `evaluate_wave_gradient_p2`. 函数导数存储在
            `gradient_basis_wave` 里。

        8.  同样用 `evaluate_radial_functions_p0`,
            传入基函数二阶导样条，计算格点处的动能项， 保存在
            `kinetic_wave` 中。

        9.  <span id="mark2"></span>将 `kinetic_wave` 和局域势
            `local_potential_parts` 传给 `evaluate_H_psi_p2`, 计算不包含
            GGA 密度梯度贡献的 $\hat{H}\varphi_{j\bR}(\br_p)$. 存储在
            `H_times_psi` 里。

        10. <span id="mark3"></span>若打开了 GGA, 将梯度贡献加到
            `H_times_psi` 中 (`add_gradient_part_to_H_p0`).
            到这一步，除了 HF exchange 外的贡献都已经包括进来了。 而 HF
            exchange 是直接加到 $H_{\sigma,ij}(\mathbf{k})$ 上的，
            不在这个函数中处理。

        11. 对 `H_times_psi` 左乘波函数 `wave`,
            得到格点对哈密顿子矩阵的贡献
            (`evaluate_hamiltonian_shell_p1`). 保存在
            [`hamiltonian_shell`](#shell-suffix-array) 中。

        12. <span id="mark4"></span>调用 `add_zora_matrix_p1`, 加入 ZORA
            标量相对论贡献。

        13. 将子矩阵 `hamiltonian_shell` 加到完整矩阵 `hamiltonian` 上。
3.  将所有进程上的 `hamiltonian` 加总。
4.  释放临时数组，结束程序。

## 回到问题 {#back-to-the-problem}

根据上面流程，为了达到拆分 Hamiltonian 的目的，只需

1.  模仿 `hamiltonian_shell`, 构造多个 `_shell` 数组，保存不同的贡献。
2.  在步骤 [2.3.9](#mark2) 中，将 `kinetic_wave` 及
    `local_potential_parts` 中的 Hartree 和 XC 两项分开传给
    `evaluate_H_psi_p2`, 将结果保存到对应的 `_shell` 数组下。
3.  在步骤 [2.3.10](#mark3) GGA 情况下，将梯度贡献加到 `xc_shell`
    数组中。
4.  将步骤 [2.3.12](#mark4) 的 ZORA 标量相对论贡献加到 `kinetic_shell`
    数组中。
5.  将 `_shell` 数组的子矩阵加到各自的完整矩阵中。

这样就完成了实空间矩阵构造。之后再做傅里叶变换，酉变换到 Kohn-Sham
空间，mission complete.

## References

<span id="citeproc_bib_item_1"></span>\[1\] V. Blum et al., Comput.
Phys. Commun. **180**, 2175 (2009)
<a href="https://doi.org/10.1016/j.cpc.2009.06.022"
target="_blank">[DOI]</a>.

<span id="citeproc_bib_item_2"></span>\[2\] V. Havu et al., J. Comput.
Phys. **228**, 8367 (2009)
<a href="https://doi.org/10.1016/j.jcp.2009.08.008"
target="_blank">[DOI]</a>.

## 注记 {#notes}

### 相关基函数 {#relevant-basis}

由于截断势的存在，数值原子基在实空间上是严格局域的（相比而言 Gaussian 有
long tail）。
对于远离某一原子的格点，以该原子为中心的基函数在该格点上的值为 0.
这就意味着这一格点对这部分基函数所对应的 $H_{s,ij}$ 子矩阵的贡献为 0.
因此为了减少内存消耗，在分配临时数组时可以排除这些基函数，
而只计算格点贡献非零的部分，即所谓的“相关”。

每个格点都有对应贡献非零的基函数的数目, `n_max_compute_ham`
是遍历格点得到的这一数目的最大值， 由 `get_n_compute_maxes_p1`
确定。类似的维数变量还有 `n_max_compute_fns_ham` (径向函数数量) 等.

### `_shell` 数组 {#shell-suffix-array}

以 `_shell` 后缀标注的数组，比如 `hamiltonian_shell`, 代表了 Hamiltonian
的一个子矩阵。 长度为 `n_max_compute_ham*n_max_compute_ham`.
