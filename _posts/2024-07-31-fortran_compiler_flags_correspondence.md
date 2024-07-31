---
author: Min-Ye Zhang
categories: programming
comments: true
date: "2024-07-31 18:14:44 +0200"
description: Cheat sheet for flags of Fortran compilers from different
  vendors.
math: false
tags: Fortran GCC Intel
title: Fortran compiler flags correspondence
---

## Compiler vendors checked here

-   gfortran: Fortran compiler for the GCC project.
-   ifort: Intel\'s classical Fortran compiler.
-   ifx: Intel\'s new Fortran compiler based on
    [LLVM](https://llvm.org/).

## List of selected flags

| Usage | gfortran | ifort | ifx |
|----|----|----|----|
| Inter-procedure optimization | `-flto` | `-ip` | `-qip` |
| Backtrace generation | `-fbacktrace` | `-traceback` | as ifort |
| Check out-of-bounds | `-fcheck=bounds` | `-check bounds` | as ifort |
| Check uninitialized variables | `-Wuninitialized` [^1] | `-check uninit` | as ifort |
| Check pointer issues | `-fcheck=pointer` | `-check pointers` | as ifort |

---

[^1]: Included in `-fcheck=all`
