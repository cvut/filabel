#!/usr/bin/bash -eu

for I in {1..4}; do
  echo "HTTP DELETE https://api.github.com/repos/${GH_USER}/filabel-testrepo${I}"
  curl --header "Authorization: token ${GH_TOKEN}" -X DELETE https://api.github.com/repos/${GH_USER}/filabel-testrepo${I}
done
