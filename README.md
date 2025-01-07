[![Netlify Status](https://api.netlify.com/api/v1/badges/c431871d-54ce-4a40-8894-d2848364e94b/deploy-status)](https://app.netlify.com/sites/minyez/deploys)

Personal site, forked from [jekyll-theme-chirpy](https://github.com/cotes2020/jekyll-theme-chirpy).
Synced to commit [`e44c048`](https://github.com/cotes2020/jekyll-theme-chirpy/tree/e44c048aef1ab3201eff05450614a32e6ce4b6bb).

Build memo
```shell
# build assest, from tools/init
# maybe necessary after sync to a new commit
npm i && npm run build
# or use Makefile: make npm

# build gem necessary for Jekyll and the theme
bundle config set --local path "$HOME/.gem"
bundle
# or use Makefile: make gem

# deploy local
bundle exec jekyll serve --livereload
# or use Makefile: make
```

Note
- Remove local browser cache if there exists inconsistency between pages (see for example Chirpy issue [#1236](https://github.com/cotes2020/jekyll-theme-chirpy/issues/1236))
- When building using netlify or GitHub Pages, build command should include `npm run build`, like `npm run build && jekyll build`, to generate necessary files under `_sass/dist` and `assets/js/dist`, which are ignored by git.

Update Chirpy by rebasing
```shell
# backup
git checkout master
git branch master_backup_<date>
git remote add upstream https://github.com/cotes2020/jekyll-theme-chirpy.git
git branch upstream upstream/master
git rebase upstream
git branch -d upstream
```

Below is the original readme

---

<!-- markdownlint-disable-next-line -->
<div align="center">

  <!-- markdownlint-disable-next-line -->
  # Chirpy Jekyll Theme

  A minimal, responsive, and feature-rich Jekyll theme for technical writing.

  [![CI][badge-ci]][ci]&nbsp;
  [![Codacy Badge][badge-codacy]][codacy]&nbsp;
  [![GitHub license][badge-license]][license]&nbsp;
  [![Gem Version][badge-gem]][gem]&nbsp;
  [![Open in Dev Containers][badge-open-container]][open-container]

  [**Live Demo** →][demo]

  [![Devices Mockup](https://chirpy-img.netlify.app/commons/devices-mockup.png)][demo]

</div>

## Features

- **Design & UX** - Responsive layout, Dark/Light modes, Localized UI language,
  and Dark mode images.
- **Content Management** - Pinned posts, Hierarchical categories, Trending tags,
  Auto-generated Table of Contents, and Last modified dates.
- **Rich Text Support** - Syntax highlighting, Mathematical expressions, Mermaid
  diagrams & flowcharts, and Embedded media.
- **Interactivity & Outreach** - Built-in search, Multiple comment systems, and
  Atom feeds.
- **System & Optimization** - PWA support, integrated Web analytics, and
  advanced SEO performance.

## Documentation

To learn how to use, develop, and upgrade the project, please refer to the
[Wiki][wiki].

## Contributing

Contributions (_pull requests_, _issues_, and _discussions_) are what make the
open-source community such an amazing place to learn, inspire, and create. Any
contributions you make are greatly appreciated.
For details, please refer to our [Contributing Guidelines][contribute-guide].

## Credits

This project is built on the [Jekyll][jekyllrb] ecosystem and integrates a
collection of [excellent libraries][lib]. Its avatar and favicon are sourced
from [ClipartMAX][clipartmax].

Furthermore, thanks to everyone who contributed to the development of this project!

[![all-contributors][contributors-avatar]][contributors]

## License

This project is licensed under the [MIT License][license].

[badge-ci]: https://img.shields.io/github/actions/workflow/status/cotes2020/jekyll-theme-chirpy/ci.yml?logo=github
[badge-codacy]: https://img.shields.io/codacy/grade/4e556876a3c54d5e8f2d2857c4f43894?logo=codacy
[badge-license]: https://img.shields.io/github/license/cotes2020/jekyll-theme-chirpy?color=goldenrod
[badge-gem]: https://img.shields.io/gem/v/jekyll-theme-chirpy?&logo=RubyGems&logoColor=ghostwhite&label=gem&color=orange
[badge-open-container]: https://img.shields.io/badge/Dev_Containers-Open-deepskyblue?logo=linuxcontainers
[gem]: https://rubygems.org/gems/jekyll-theme-chirpy
[ci]: https://github.com/cotes2020/jekyll-theme-chirpy/actions/workflows/ci.yml?query=event%3Apush+branch%3Amaster
[codacy]: https://app.codacy.com/gh/cotes2020/jekyll-theme-chirpy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade
[license]: https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/LICENSE
[open-container]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/cotes2020/jekyll-theme-chirpy
[jekyllrb]: https://jekyllrb.com/
[clipartmax]: https://www.clipartmax.com/middle/m2i8b1m2K9Z5m2K9_ant-clipart-childrens-ant-cute/
[demo]: https://cotes2020.github.io/chirpy-demo/
[wiki]: https://github.com/cotes2020/jekyll-theme-chirpy/wiki
[contribute-guide]: https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/docs/CONTRIBUTING.md
[contributors]: https://github.com/cotes2020/jekyll-theme-chirpy/graphs/contributors
[contributors-avatar]: https://contrib.rocks/image?repo=cotes2020/jekyll-theme-chirpy&columns=16&max=112
[lib]: https://github.com/cotes2020/chirpy-static-assets
