#!/bin/bash

if [ "$TRAVIS_PYTHON_VERSION" == "3.6" ];
then

	openssl aes-256-cbc -K $encrypted_51741ccedff4_key -iv $encrypted_51741ccedff4_iv -in github_deploy_key.enc -out github_deploy_key -d
	chmod 600 github_deploy_key
	eval `ssh-agent -s`
	ssh-add github_deploy_key

	python setup.py build_sphinx

	cp -r ./build/sphinx/html ~/out

	cd ~/out
	git init
	git remote add origin git@github.com:$TRAVIS_REPO_SLUG
	git config user.name "TRAVIS CI"
	git config user.email "deploybot@fact-project.org"

	git add .
	git commit -m "Deploy to GitHub Pages"

	git push --force --quiet -u origin master:gh-pages > /dev/null 2>&1
fi
