---
title: Keynote 备忘 (CN)
date: 2023-05-31 22:21:24 +0200
categories: [tool, ]
tags: [Keynote, macOS]
math: false
comment: false
---

## 在幻灯片放映时显示鼠标指针

默认在幻灯片放映时不显示鼠标指针。
需要在 `偏好设置->幻灯片放映` 中选择 “使用鼠标或触控板时显示指针”。

## 实现格式为 “当前页/总页数” 的页码

Keynote 本身只提供当前页码，没有总页数。
要实现该功能，可编辑幻灯片布局，在要修改的布局的页码后面手动添加一个文本框，
输入总页码，例如 `/XX`.

## 上下标

- 上标 `Ctrl Shift CMD +`
- 下标 `Ctrl CMD -`

总觉得要按 `option`.

## 透明度动画效果

1. 如果要让动画对象最终处于不透明状态，就先在 Style 中调低它的透明度。
2. 选取对象，在 `Animate` 的 `Action` 标签中 `Add an Effect`, 选择 Opacity.
3. 调整透明度到最终想要的效果。
4. 调整 Build Order 使协同改变透明度的对象

[Youtube](https://www.youtube.com/watch?v=fXgcwCpiBQI)
