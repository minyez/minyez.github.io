---
title: Migrate Hexo blog to Jekyll
date: 2023-05-20 18:46:44 +0200
categories: [tool, internet]
tags: [Jekyll, GitHub, Blog]
---

## Motivation

The first and main reason is very simple: I would like to pick up my personal
website. I feel like that many of my problems, both in work and life, actually
result from my laziness to put them into my own words.
Writing for myself is not enough for striving to express myself as best as
I can. However, writing in some SNS brings me kind of humiliation as I grow
up as a weak human.[^1]
This place, a public space with only few to none noticing, is still the best playground.
Meanwhile, some posts and information are obsolete, thus updates or archiving
would be favorable for my own and public (if any) interest.

Secondly, I cannot build my Hexo website on my old macOS laptop after I update
some brew taps (hexo itself, probably). The only one to blame is myself, being
unable to write more frequently to adapt any breaking changes as soon as
possible.

Thirdly, landing on [Qijing's website](http://staff.ustc.edu.cn/~zqj/) triggers my
interest in the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
theme with Jekyll. The theme is tidy but meanwhile very functional.
The [Jekyll](https://jekyllrb.com/) static site generator, although "older"
than Hexo and Hugo, is used by many and still actively developed by its
community.


## Theme

As implied above, I use the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme.
Instead of using the kickstart repository, I forked it by commit
[`1719d81`](https://github.com/cotes2020/jekyll-theme-chirpy/tree/1719d81d00b32b107c35b3903089be84a9b28a6c).
Update to the upstream can still be applied here by differing and patching,
but I would refrain from this unless necessary.

### Modification

Below is a list of modifications I made to the forked upstream commit,
other than the `_config.yml` configuration file

- Hide tags and categories pages by adding variable `sidebar_tabs` to `_config.yml`,
  and add filter in `_includes/sidebar.html ` (see [comment](https://github.com/cotes2020/jekyll-theme-chirpy/issues/651#issuecomment-1230532056))
- Comment out post preview part in `_layouts/home.html` for a cleaner home page
  (maybe introduce support of excerpt later)
- Justify post text by modifying `_sass/addon/commons.scss` according to
  [the comment from Chirpy's author](https://github.com/cotes2020/jekyll-theme-chirpy/issues/172#issuecomment-823987550)
- Add an ORCID social link in `_includes/sidebar.html` and switch it on in `_data/contact.yml`
- Modify foreground color of inline code in light mode by changing `--highlighter-rouge-color` in `_sass/colors/light-syntax.scss`
- Enable equation numbering by modifying `_includes/js-selector.html`

### Tool

A helper script for publishing/drafting posts `postu` is created under directory `tools`,
as a simple alternative to [jekyll-compose](https://github.com/jekyll/jekyll-compose).

---

[^1]: or rather, `age++`

