---
title: Build FHI-aims on macOS Sonoma using GNU compilers
date: 2023-12-18 16:57:49 +0100
categories: [software, simulation]
tags: [Build, FHIaims, macOS]
math: false
comment: false
---

Recently I upgraded my M2 Max MBP to Sonoma and somehow broke the Intel oneAPI suite,
which I have been using to build FHIaims on this laptop for last half year.
Since I need to tweak FHIaims and re-build it from time to time, I have to switch to GNU compilers.
Here I record my procedure to do this.

## Prerequisites

### GCC and MPI compiler from Homebrew

```shell
brew install gcc
brew install mpich
```

Instead of MPICH, one can use OpenMPI (`open-mpi`) for MPI parallelization.
But since I have been using Intel MPI for quite a while and MPICH is more similar to it than OpenMPI,
I prefer to stick with MPICH. Since I also have OpenMPI installed and used as the default MPI wrapper,
I have to unlink it before proceeding

```shell
brew unlink open-mpi
brew link mpich
```

### OpenBLAS from Homebrew

```shell
brew install openblas
```

Of course, one can use the accelerate framework shipped by Apple.
However, I met some issue with the `zdotu` vector product subroutine when calculating GW,
and the performances of these two options did not differ too much.

### ScaLAPACK

In `SLmake.inc`
```makefile
FC            = mpifort
CC            = mpicc -cc=gcc-13
NOOPT         = -O0 -fallow-argument-mismatch
FCFLAGS       = -O3 -fallow-argument-mismatch
CCFLAGS       = -O3 -std=c99 -Wno-implicit-function-declaration
FCLOADER      = $(FC)
CCLOADER      = $(CC)
FCLOADFLAGS   = $(FCFLAGS) -Wl,-ld_classic
CCLOADFLAGS   = $(CCFLAGS) -Wl,-ld_classic
```

`mpifort` is using `gfortran` for compiling Fortran source.
By default, the C compiler used by `mpicc` is Apple LLVM Clang.
To be consistent, `-cc` option is invoked and set as `gcc-13`.
The `-ld_classic` option is passed to the linker by the compiler (`-Wl`), to resolve
the `ld: unknown options: -commons` error at the linking stage after Xcode 15.

Then trigger `make` (or `make -j` to use all cores to compile).
If everything goes smoothly, `libscalapack.a` will be generated under the root path.
I move it to some path like `scalapack/2.2.0/gcc-13.2.0-mpich-4.1.2-openblas`
so that I can identify later how this library was compiled.

Note that if OpenMPI is used instead, this step can be skipped by installing it from Homebrew

```shell
brew install scalapack
```

If you prefers to build it on your own, you have to remove the `-cc` option because OpenMPI doesn't support it.
To still ensure the use of GNU C compiler, you need to specify environment variable `OMPI_CC`
```shell
export OMPI_CC=gcc-13
```
before triggering `make`.

## Compiling FHI-aims

First one has to unarchieve the FHIaims tarball or clone the gitlab repository.
At the top directory, create a build directory, say `build_mpich_openblas` and
prepare the following `inital_cache.cmake`

```cmake
set(CMAKE_Fortran_COMPILER "mpifort" CACHE STRING "" FORCE)
set(CMAKE_Fortran_FLAGS "-O3 -fallow-argument-mismatch -ffree-line-length-none -Wl,-ld_classic,-lstdc++" CACHE STRING "" FORCE)
set(Fortran_MIN_FLAGS "-O0 -fallow-argument-mismatch -ffree-line-length-none -Wl,-ld_classic" CACHE STRING "" FORCE)
set(CMAKE_C_COMPILER "mpicc" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS "-cc=gcc-13 -O3 -Wl,-ld_classic" CACHE STRING "" FORCE)
set(CMAKE_CXX_COMPILER "mpicxx" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS "-cxx=g++-13 -O3 -Wl,-ld_classic" CACHE STRING "" FORCE)
set(LIB_PATHS "/opt/packages/scalapack/2.2.0/gcc-13.2.0-mpich-4.1.2-openblas /opt/homebrew/Cellar/openblas/0.3.25/lib" CACHE STRING "")
set(LIBS "scalapack openblas" CACHE STRING "" FORCE)

# Switched on greenx for minimax grids
set(USE_GREENX ON CACHE BOOL "" FORCE)
set(USE_MPI ON CACHE BOOL "" FORCE)
set(USE_SCALAPACK ON CACHE BOOL "" FORCE)
set(USE_LIBXC ON CACHE BOOL "" FORCE)
set(USE_HDF5 OFF CACHE BOOL "" FORCE)
set(USE_RLSY ON CACHE BOOL "" FORCE)
set(ELPA2_KERNEL "" CACHE STRING "Change to AVX/AVX2/AVX512 if running on Intel processors" FORCE)
```

Then build the executable by
```shell
cd build_mpich_openblas
cmake -C ../inital_cache.cmake .. && make -j 8
```

## Test
```shell
OMP_NUM_THREADS=1 python3 ./regressiontools.py full --force \
    --exclude="version" --exclude="libaims ASI" --exclude="ASE" --mpiexe "mpirun" --cpus 4 \
    --batch ./references_lastrelease ../build_mpich_openblas/aims.231208.scalapack.mpi.x
```

If everything is green, we are good to proceed to our calculations.
Thanks to the large unified memory, we can actually do some decent calculation with M2.
