---
layout: compress
# WARNING: Don't use '//' to comment out code, use '{% comment %}' and '{% endcomment %}' instead.
---

{%- comment -%}
  See: <https://docs.mathjax.org/en/latest/options/input/tex.html#tex-options>
{%- endcomment -%}

MathJax = {
  loader: {load: [
    '[tex]/physics'
  ]},
  tex: {
    {%- comment %} macros {% endcomment -%}
    macros: {
      bvec: ["\\mathbf{#1}", 1],
      br: "\\bvec{r}",
      bR: "\\bvec{R}",
      bk: "\\bvec{k}",
      ii: "\\mathrm{i}",
      ee: "\\mathrm{e}"
    },
    packages: {'[+]': [
      'physics'
    ]},
    {%- comment -%} start/end delimiter pairs for in-line math {%- endcomment -%}
    inlineMath: [
      ['$', '$'],
      ['\\(', '\\)']
    ],
    {%- comment -%} start/end delimiter pairs for display math {%- endcomment -%}
    displayMath: [
      ['$$', '$$'],
      ['\\[', '\\]']
    ],
    {%- comment -%} equation numbering {%- endcomment -%}
    tags: 'ams'
  }
};
