---
title: fiddle-proof 与拖延症 
date: 2020-07-19 16:56:37 +0800
categories: [comment, work]
tags: [note-taking, TaskPaper, Org-mode, GTD]
comment: false
math: false
---

在捣鼓 Org-mode 的 $\rm\LaTeX$ 导出时偶然间被 refer 到一封 Org-mode 作者 Carsten Dominik 写的 [mail-list](https://orgmode.org/list/0277B507-1486-4172-B1C6-1B73B84148DD@science.uva.nl/) 下。原文主题是比较 Org 和另一个 GTD 软件 [TaskPaper](https://www.taskpaper.com/) (上一篇《{% post_link macos-float-window %}》就是为了这个软件). 大意是作为纯文本 GTD, Org-mode 就是 TaskPaper. Org-mode 诚然提供了大量功能，但这并非强迫用户去使用。用户更不需要从一开始就去 (学其他人) 构建一个繁杂的 GTD 系统。更好的办法是从最基本的 TODO 和 DONE 开始，根据自己需求慢慢扩展.

笔者是赞同这个观点的。复杂的待办系统要对待办分类，加优先级，加标签，周期重复等等。这么做的终极目的是把事务做清晰的划分，方便筛选以避开来自冗余信息的影响。然而这个复杂的系统本身就可能成为 "冗余信息". 别人的 GTD 系统，在自己身上可能完全是 nonsense. 与其从头理解然后套用，不如构建一个适合自己的系统。亲切和趁手比什么都重要.

让我感触最深的并不是这个观点，而是 Carsten 引出 Org-mode 高度可定制的优势时说的一句

> What is so great about taskpaper that it is (so far?) almost fiddle-proof. It is a list, and there is no way to fiddle with it. People who use fiddling with the TODO system as a way to procrastinate can clearly benefit from such a system.

"fiddle" 有摆弄、把玩 (瞎搞) 的意思，而 proof 后缀表示 "protecting against", 合起来就是 "不给瞎搞". 跟 org-mode 相比，TaskPaper 能鼓捣的内容确实少：它支持标签 (`@`), 但不支持多种 TODO 标记，也不支持事项的作业计时 (org-mode 下有 `org-clock-in/out`), 更不用提各种代码块、导出功能。第二句 "借鼓捣 GTD 系统来拖延的人显然可因此获益." 想起在 DDL 面前依然去折腾各种新旧工具和软件的自己，这一句十分扎心。特别当这些工具中的很多现在其实已经不怎么用的时候，当初 fiddling 只为拖延似乎就千真万确、难以辩驳了.

然而 TaskPaper 真的能帮助人不去 procrastinate 吗？即便是 Carsten 认为 "fiddle-proof" 的 TaskPaper, 我也折腾了 macOS 窗口置顶，花了不少时间做 CSS 定制，而不是去做那些 TODO 们。在看到 Org-mode 后转去鼓捣 Emacs 这一深坑，TaskPaper 自然而然被忘在了角落。

一个人如果想 procrastinate, 他总可以找到无数的办法。即使是 fiddle-proof 的东西他也能找到把玩的角度。要是手头上的东西不足以让他继续 procrastinate，他就会去找新的。今天云《对马岛之魂》时还听到这样一句话: "成事在人，而非刀剑." 可能不是非常恰当，但对于任何现代工具也是一样：工具始终只是工具，解决问题的只能是人。而 Procrastinator 不是不想解决问题。他们是对真正重要的问题选择了视而不见。
