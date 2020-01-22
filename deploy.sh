#!/bin/bash

git_version=$(git rev-parse --short HEAD)

docker build -t "kjwon15/qdon-prefetch:${git_version}" .
docker push "kjwon15/qdon-prefetch:${git_version}"

sed -e "s#image: kjwon15/qdon-prefetch.*\$#image: kjwon15/qdon-prefetch:${git_version}#" docker-compose.yml > docker-stack.yml
docker stack deploy qdon-pfetch -c docker-stack.yml
