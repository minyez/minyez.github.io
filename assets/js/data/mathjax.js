---
layout: compress
# WARNING: Don't use '//' to comment out code, use '{% comment %}' and '{% endcomment %}' instead.
---

{%- comment -%}
  See: <https://docs.mathjax.org/en/latest/options/input/tex.html#tex-options>
{%- endcomment -%}

MathJax = {
  {%- if site.mathjax.extensions -%}
  loader: {load: [
    {%- for ext in site.mathjax.extensions -%}
    '[tex]/{{ ext }}'{%- unless forloop.last -%},{%- endunless -%}
    {%- endfor -%}
  ]},
  {%- endif -%}
  tex: {
    {%- comment %} macros {% endcomment -%}
    {%- if site.mathjax.macros -%}
    macros: {
      {%- for macro in site.mathjax.macros -%}
      {%- if macro.nargs -%}
      {{ macro.name }}: ["{{ macro.command }}", {{ macro.nargs }}]
      {%- else -%}
      {{ macro.name }}: "{{ macro.command }}"
      {%- endif -%}
      {%- unless forloop.last -%},{%- endunless -%}
      {%- endfor -%}
    },
    {%- endif -%}
    {% if site.mathjax.extensions %}
    packages: {'[+]': [
      {%- for ext in site.mathjax.extensions -%}
      '{{ ext }}'{%- unless forloop.last -%},{%- endunless -%}
      {%- endfor -%}
    ]},
    {%- endif -%}
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
