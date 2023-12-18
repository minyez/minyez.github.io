# deploy local
default:
		bundle exec jekyll serve --livereload

# build assest, from tools/init, maybe necessary after sync to a new commit
build:
		npm i && npm run build

# build gem necessary for Jekyll and the theme
gem:
		bundle config set --local path "$(HOME)/.gem"
		bundle
