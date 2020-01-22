#!/bin/bash

git_version=$(git rev-parse --short HEAD)
IMAGE="kjwon15/qdon-prefetch"
IMAGE_TAG="${IMAGE}:${git_version}"

if ! docker inspect --type image "${IMAGE_TAG}" &>/dev/null; then
    docker build -t "${IMAGE_TAG}" .
fi
docker push "${IMAGE_TAG}"

sed -e "s#image: ${IMAGE}.*\$#image: ${IMAGE_TAG}#" docker-compose.yml > docker-stack.yml
docker stack deploy qdon-pfetch -c docker-stack.yml
