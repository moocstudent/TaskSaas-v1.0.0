#!/bin/bash
# author zq

cmd="tasksaas:1.1.0"
docker build . -t $cmd -f Dockerfile


# 替换YAML文件中的image版本号部分 不管用

docker-compose build

docker-compose up -d