#!/usr/bin/env ruby
#
# Check for changed posts

Jekyll::Hooks.register :posts, :post_init do |post|
  set_lastmod_date(post)
end

Jekyll::Hooks.register :tabs, :post_init do |tab|
  set_lastmod_date(tab)
end

def set_lastmod_date(doc)
  commit_num = `git rev-list --count HEAD "#{ doc.path }"`

  if commit_num.to_i > 1
    lastmod_date = `git log -1 --pretty="%ad" --date=iso "#{ doc.path }"`
    doc.data['last_modified_at'] = lastmod_date
  end
end
