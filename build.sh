#!/bin/bash
# author zq

cmd=$1
docker build . -t $cmd -f Dockerfile

# 新的镜像版本号
NEW_IMAGE_VERSION=$cmd

# 替换YAML文件中的image版本号部分
sed -i "s/tasksaas:[[:digit:]].[[:digit:]].[[:digit:]]*/tasksaas:${NEW_IMAGE_VERSION}/" docker-compose.yml

docker-compose build

docker-compose up -d