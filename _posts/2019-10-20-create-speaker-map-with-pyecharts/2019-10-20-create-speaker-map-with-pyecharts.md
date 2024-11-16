---
title: 用 pyecharts 制作统计地图
comments: true
date: 2019-10-20 22:47:28 +0800
tags:
- Python
- pyecharts
categories: tool
description: 以会议报告人所在机构的分布为例, 介绍如何基于 pyecharts 制作地理分布图.
---

## 前言

前段时间去深圳参加一个研究方向有关的会议, 国内做实验和理论研究的老师都来了,
于是心血来潮想有没有可能做一个统计来看看老师们所在机构的地理分布.
虽然报告人并不多, 但应该也能提供一些定性的信息, 也算是学习一种图片制作和数据展示技巧.
经过一番搜索, 决定采用 Python 包 `pyecharts` 中的地理图标 `Geo` 类来制作.
使用 Python 版本为 3.7.1, pyecharts 版本为 1.5.1.

## 准备

首先通过 pip 安装 pyecharts

```shell
pip install pyecharts
```

同时安装中国省市地图包

```shell
pip echarts-china-provinces-pypkg echarts-china-cities-pypkg
```

为方便直接输出图片, 安装 `snapshot_selenium` 或者 `snapshot_phantomjs`

```shell
pip snapshot_selenium snapshot_phantomjs
```

## 初步尝试

简化一下存放在 `site-packages/example` 里的 `geo_example.py`, 得到下面的代码

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pyecharts import options as opts
from pyecharts.charts import Geo, Page
from pyecharts.faker import Collector
from pyecharts.render import make_snapshot
#from snapshot_selenium import snapshot
from snapshot_phantomjs import snapshot

# speaker.json 存储了以 speaker 老师名字为 key 的字典
# 包含"省份"和"方向"两个 key-value.
with open("speaker.json", 'r') as h:
    speaker = json.load(h)
provs = [s["省份"] for s in speaker.values()]
data = [[p, provs.count(p)] for p in set(provs)]

C = Collector

@C.funcs
def geo_speakermap() -> Geo:
    c = (
        Geo()
        .add_schema(maptype="china")
        .add("", data)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_=0, max_=15, type_="size"),
            title_opts=opts.TitleOpts(title="报告人分布"),
        )
    )
    return c

make_snapshot(snapshot, Page().add(*[fn() for fn, _ in C.charts]).render(),
              "speakermap.png", browser='Safari')
```

得到分布图如下

![Speaker distribution map](speakermap.png)
_报告人分布地图_

报告人主要分布在沿海城市的大学和研究所, 除了 bug 的帝都.

## 实现细节

下面就作图涉及的几个细节具体说明

### Collector 类

`Collector` 是 pyechart 提供的一个 convenient function, 源码很短,
提供了一个列表属性和一个静态方法用 `Collector.funcs` 装饰后,
函数返回的 `Geo` 实例会加入到列表 `Collector.charts` 中.

```python
class Collector:
    charts = []

    @staticmethod
    def funcs(fn):
        Collector.charts.append((fn, fn.__name__))
```

`Geo` 类及其方法的调用利用了方法链语法, 不需要换行符来强制换行.

### 全局变量控制

用 `set_global_opts` 方法调整 echarts 图片的全局设置. 这个方法继承自 `Chart` 类.
参数 `visualmap_opts` 控制左下角标尺, 需要以 `pyecharts.options.VisualMapOpts` 实例作为输入.
这里因为总人数比较少, 所以调整了最大范围为 15, 并用图标尺寸而非颜色来表示数值大小 (`type_`), 加强对比.
其他全局变量设置可以参考[官网](https://pyecharts.org/#/zh-cn/global_options).

### 图片生成

`pyecharts.render.snapshot` 提供了 `make_snapshot` 函数. `make_snapshot` 实际是 selenium 或 phantomjs 的 `snapshot` 同名函数的包装.

这里用 phantomjs 直接渲染更快一些, 且不会跳出 Safari.

## 总结

本文基于 pyecharts 的 `Geo` 类制作了报告人所在机构的地理分布.
文中所描述的图片制作是一些简单尝试, 还有很多应该可以调教的地方,
比如标记的颜色, 标尺和主图的相对位置.
不过统计数据太少, 机构地点还只限制在省级, 所得到的结论比较 trivial.

echarts 还提供了包括全球和国内省市地图在内的其他地图以及 word cloud 等不同类型的图片呈现方式,
并有现成的例子可供参考, 为地理数据统计和展示提供了一种方便的选择.

## 参考资料

- [知乎 - Python 绘制中国地图](https://zhuanlan.zhihu.com/p/45202403): 引导我使用 pyecharts. 但是这个教程及其中链接的官方网站的 API 不适用于 1.5.1 版本.
- [pyecharts 官网](https://pyecharts.org/#/zh-cn/intro)
- [Creating a Choropleth Map of the World in Python using GeoPandas](https://ramiro.org/notebook/geopandas-choropleth/): 做全球数据统计看上去很不错
