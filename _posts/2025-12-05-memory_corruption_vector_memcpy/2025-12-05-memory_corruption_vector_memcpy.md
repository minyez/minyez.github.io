---
title: An example of memory corruption with C++ `std::vector` and `memcpy`
date: 2025-12-05 13:33:48 +0100
categories: programming
tags: [Cpp, "memory corruption", "debugging", "Valgrind", "Fortran"]
author: Min-Ye Zhang
comments: true
math: false
description: Lesson learned from a random crash
---

Recently I have been writing Fortran binding for my C++ project.
To test the bindings, I wrote a small Fortran test program alongside the main C++ driver.

Interestingly, the Fortran test would fail **randomly** after setting up inputs and starting calculation,
either with heap corruption or with an assertion failure from a manual dimension check (roughly once every 40 runs).
The C++ driver, on the other hand, worked fine with my existing test case.

After a few rounds of discussion with ChatGPT, I still couldn’t pinpoint the issue.
So I turned to [Valgrind](https://valgrind.org/)’s [Memcheck](https://valgrind.org/docs/manual/mc-manual.html):

```bash
valgrind --tool=memcheck --leak-check=full ./test_fortran_binding
```

It pointed to something suspicious:

```
==18743== Invalid write of size 8
==18743==    at 0x48CB82C: __GI_memcpy (vg_replace_strmem.c:1147)
==18743==    by 0x4EB9763: set_ibz_mapping (input.cpp:296)
==18743==    by 0x491239F: __lib_MOD_set_ibz_mapping (lib.f90:829)
==18743==    by 0x41116B: MAIN__ (test_lib_binding.f90:106)
==18743==    by 0x411E37: main (test_lib_binding.f90:3)
==18743==  Address 0x816c3c8 is 8 bytes inside a block of size 12 alloc'd
==18743==    at 0x48C1040: operator new(unsigned long) (vg_replace_malloc.c:483)
==18743==    by 0x4EC913F: std::__new_allocator<int>::allocate(unsigned long, void const*) (new_allocator.h:151)
==18743==    by 0x4EC39EB: allocate (alloc_traits.h:482)
==18743==    by 0x4EC39EB: std::_Vector_base<int, std::allocator<int> >::_M_allocate(unsigned long) (stl_vector.h:378)
==18743==    by 0x4EC042F: std::_Vector_base<int, std::allocator<int> >::_M_create_storage(unsigned long) (stl_vector.h:395)
==18743==    by 0x4EBDFCB: std::_Vector_base<int, std::allocator<int> >::_Vector_base(unsigned long, std::allocator<int> const&) (stl_vector.h:332)
==18743==    by 0x4EBC0AF: std::vector<int, std::allocator<int> >::vector(unsigned long, std::allocator<int> const&) (stl_vector.h:554)
==18743==    by 0x4EB9733: set_ibz_mapping (input.cpp:295)
==18743==    by 0x491239F: __lib_MOD_set_ibz_mapping (lib.f90:829)
==18743==    by 0x41116B: MAIN__ (test_fortran_binding.f90:106)
==18743==    by 0x411E37: main (test_fortran_binding.f90:3)
```

The invalid write happened while setting up the mapping between the full k-point set and the irreducible sector. Looking at the code, I quickly noticed the bug: the `memcpy` size should use `sizeof(int)`, not `sizeof(double)`.

```cpp
void set_ibz_mapping(int nkpts, const int* map_ibzk)
{
    std::vector<int> map(nkpts);
    memcpy(map.data(), map_ibzk, nkpts * sizeof(double)); // BUG
    // ...
}
```

This explains the random failures: on most platforms, `double` is twice the size of `int`, so this call copies **twice as many bytes** as the destination buffer can hold. The program sometimes still ran because:

1. `std::vector` may allocate more memory than requested (its [capacity](https://en.cppreference.com/w/cpp/container/vector/capacity) can exceed its size). If the extra space happened to be large enough, the overwrite stayed within the same allocation.
2. The overwrite landed in heap memory that wasn’t touched again during the run—until it suddenly was.

The fix is simple: use the correct element size, or better, avoid `memcpy` entirely and use a range constructor

```cpp
void set_ibz_mapping(int nkpts, const int* map_ibzk)
{
    std::vector<int> map(map_ibzk, map_ibzk + nkpts);
    // ...
}
```

This immediately resolved the mysterious “random break” in the Fortran test.
The test case with the C++ driver did not break mainly because it had only one k-point,
so the `map` vector could tolerate the oversized copy as long as its capacity happened to have room for just one more `int`.

(Text polished by ChatGPT)
