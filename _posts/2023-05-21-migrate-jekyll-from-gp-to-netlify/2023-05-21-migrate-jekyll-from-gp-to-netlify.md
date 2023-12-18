---
title: Migrate blog from GitHub Pages to Netlify
date: 2023-05-21 19:20:38 +0200
categories: [tool, internet]
tags: [Jekyll, Netlify, GitHub, Blog]
---

## Introduction

The Jekyll plugin [jekyll-postfiles](https://github.com/nhoizey/jekyll-postfiles)
is handy when writing posts.
When building, it copies files in the post directory to the right place in
the site build, so that image or file links, e.g. `![fig](fig.png)` in post
markdown, works after converting to HTML. It meanwhile keeps the original
`![](/assets/fig.png)` way to refer to assets.
One needs to add following to `Gemfile` to install this plugin
```ruby
source "https://rubygems.org"

gem 'jekyll'

group :jekyll_plugins do
  gem 'jekyll-postfiles'
end
```

My current site is built and deployed on GitHub Pages through page action.
However, the author of `jekyll-postfiles` suggests that GitHub Pages doesn't
support thirt-party plugins.
I guess the page action will check `:jekyll_plugins` in the `Gemfile` and will
fail if any. Searching on Google gives me an impression that few tries to
use `jekyll-postfiles` with GitHub Pages.

To use `jekyll-postfiles` for remote building, use of site services is suggested.
I decide to give [Netlify](https://www.netlify.com/) a shot.
I have actually opened a Netlify account quite a while before by connecting to
my GitHub account, when I saw one of my friends deploying his site there.

Below is a quick memo for myself of the migration process.

## Update setting of repository

- Change the Website in the repository details (the gear near About)
- Stop building from action in Setting: in `Actions->General` tab, select `Disable actions`
- To make sure that the page will not be built, in `Pages` tab of Setting,
  select "Deploy from a branch" for source, and select `None` as branch.

## Handle Gem dependencies

[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme itself has a Gemfile
and install its dependencies through `gemspec` command.
In `jekyll-theme-chirpy.gemspec`, `jekyll` is mentioned as a runtime dependency.
Thus simply adding the plugin somewhere in Gemfile should suffice.
```ruby
group :jekyll_plugins do
  gem 'jekyll-postfiles'
end
```
Then commit this change and push to GitHub.

## Set new site on Netlify

On Netlify, import the blog project by "Add new site". Connect to the GitHub
account, choose the site repository. Netlify is clever enough to find that this
is a Jekyll website, and reminds me of missing the `jekyll` dependency in
Gemfile. However, this can be safely ignored, since `jekyll` is handled in the
gemspec file as mentioned above.

In the build setting session, change the command to `jekyll build` and click
"Deploy site". Since the site is still rather small, the build finishes only in
a minute.
A random name will be dispatched to the site.
Go to "Site setting" tab of the site project,
click "Change site name" and type in a meaningful site name.
For my case, the site name is `minyez`, making the website `minyez.netlify.app`.

I am not bothering with custom domain at present.

## Summary

Migrating from GitHub Pages to Netlify appears to be very straightforward under
the Chirpy theme. With `jekyll-postfiles` plugin, refering to images and files
becomes very intuitive, which makes me look forward to future writing.

## References

The official site provides a rather old
[tutorial](https://www.netlify.com/blog/2017/05/11/migrating-your-jekyll-site-to-netlify)
for migrating from GitHub Pages. It basically works for me as of the writing,
while it seems not necessary to include full `github-pages` gem or have a
`.ruby-version` file.
