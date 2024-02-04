#!/bin/bash
# author zq

cmd="tasksaas:1.0.16"
docker build . -t $cmd -f Dockerfile


# 替换YAML文件中的image版本号部分 不管用
#sed -i "s/tasksaas:[[:digit:]].[[:digit:]].[[:digit:]]*/$cmd/" docker-compose.yml

docker-compose build

docker-compose up -d