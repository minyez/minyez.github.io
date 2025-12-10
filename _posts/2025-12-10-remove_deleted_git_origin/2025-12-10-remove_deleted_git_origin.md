---
title: git 移除对已失效 origin 远端的追踪
date: 2025-12-10 12:20:58 +0100
categories: tool
tags: [git, remove server]
lang: zh-CN
math: false
comments: true
---

## 问题 {#problem}

本机 git 仓库拥有 `origin` (默认) 和 `upstream` 两个追踪的远端。
`origin` 是 `upstream` 早期的一个 fork，但长期没有维护。
最近发现 `origin` 对应 URL 已经失效 (作者删除了)，我打算

1. 备份 `origin` 的主分支内容到 `upstream` 的新分支下，
2. 移除对原有 `origin` 的追踪，将 `upstream` 的 URL 设定为 `origin`.

(1) 很容易做到，但在第二步移除对 `origin` 的追踪时报错
```
$ git remote remove origin
error: could not delete references: cannot lock ref 'refs/remotes/origin/head': Unable to create '/Users/minyez/software/xxxxx/.git/refs/remotes/origin/head.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
```

但实际上所提到的路径下面并没有 `head.lock` 文件或其大小写变体。

## 解决方案 {#solution}

来自 ChatGPT

```bash
# 1) Kill any stale locks (check both spellings)
find .git -name '*.lock' -print
rm -f .git/refs/remotes/origin/HEAD.lock .git/refs/remotes/origin/head.lock
rm -f .git/packed-refs.lock .git/index.lock

# 2) Remove the problematic HEAD file, then delete origin/head
rm -f .git/refs/remotes/origin/HEAD
git update-ref -d refs/remotes/origin/HEAD 2>/dev/null || true
git update-ref -d refs/remotes/origin/head 2>/dev/null || true

# 3) Delete all remaining origin/* remote-tracking refs (packed + loose)
git for-each-ref --format='%(refname)' refs/remotes/origin \
  | xargs -n 1 git update-ref -d

# 4) Remove leftover directories/logs (optional but tidy)
rm -rf .git/refs/remotes/origin .git/logs/refs/remotes/origin

# 5) Verify
git show-ref | grep refs/remotes/origin || echo "origin refs are gone"
```

这五步后，查看 `.git/config` 仍能看到 `origin` 远端，此时再执行

```bash
git remote remove origin
```

即可成功移除 `origin`. 重新设置 `origin` URL 就是轻而易举的了

```bash
git remote add origin git@xxx:yyy/zzz.git
# Checkout new master
git fetch origin
git checkout origin/master -b master
# or
git checkout --track origin/master
```
