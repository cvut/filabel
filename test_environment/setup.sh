#!/usr/bin/bash -eux

# this var is used by hub, it will use the same token = same user
export GITHUB_TOKEN=${GH_TOKEN}

for I in {1..4}; do
  mkdir filabel-testrepo${I}
  cd filabel-testrepo${I}
  git init
  git commit --allow-empty -m'Initial commit'
  hub create
  git push -u origin master
  cd ..
done


cd filabel-testrepo1
git checkout -b pr1
touch aaaa bbbb cccc dddd
git add .
git commit -m'Add some files'
git push -u origin pr1
hub pull-request -m'Add some files'

git checkout master
git checkout -b pr2
touch file{1..222}
git add .
git commit -m'Add many files'
git push -u origin pr2
hub pull-request -m'Add many files'
cd ..


cd filabel-testrepo2
git checkout -b pr1
touch radioactive waste
git add .
git commit -m'Add radioactive waste'
for B in {2..111}; do
  git checkout -b pr${B}
done
git push -u origin --all
for B in {1..111}; do
  git checkout pr${B}
  hub pull-request -m"Add radioactive waste take ${B}"
done
cd ..


# filabel-testrepo3 is deliberately empty


cd filabel-testrepo4
for B in pr_closed, pr_open; do
  git checkout master
  git checkout -b ${B}
  touch aaaa
  git add .
  git commit -m'Add some files'
  git push -u origin ${B}
  hub pull-request -m'Add some files'
done
git checkout -b pr2pr
touch bbbb
git add .
git commit -m'Add some other files'
git push -u origin pr2pr
hub pull-request -m'Add some other files' -b pr_open
cd ..

curl --header "Authorization: token ${GH_TOKEN}" -X PATCH \
  "https://api.github.com/repos/${GH_USER}/filabel-testrepo4/pulls/1" \
  --data '{"state": "closed"}'


hub clone hroncok/filabel-testrepo-everybody
cd filabel-testrepo-everybody
hub fork
git checkout -b mypr
touch aaaa bbbb cccc dddd
git add .
git commit -m'Add some files'
git push -u ${GH_USER} mypr
hub pull-request -m"Pull Request of ${GH_USER}"
cd ..


rm filabel-testrepo{1..4} filabel-testrepo-everybody -rf
