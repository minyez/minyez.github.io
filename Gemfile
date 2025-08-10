# frozen_string_literal: true

source "https://rubygems.org"

gemspec

group :jekyll_plugins do
  gem 'jekyll-postfiles'
  gem 'jekyll-twitter-plugin'
end

gem "html-proofer", "~> 5.0", group: :test

platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.2.0", :platforms => [:windows]
