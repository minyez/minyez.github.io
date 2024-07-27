# vim: tabstop=4 shiftwidth=4 noexpandtab

.PHONY: default build gem proof

# deploy local
default:
	bundle exec jekyll serve --livereload --trace
	# bundle exec jekyll serve --livereload --trace --port 18028

# build assets, from tools/init, maybe necessary after sync to a new commit
build:
	npm i && npm run build

# build gem necessary for Jekyll and the theme
gem:
	bundle config set --local path "$(HOME)/.gem"
	bundle

# https://talk.jekyllrb.com/t/chirpy-theme-a-tag-is-missing-a-reference/8731/6
proof:
	bundle exec jekyll b
	bundle exec htmlproofer _site \
		\-\-disable-external \
		\-\-ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
