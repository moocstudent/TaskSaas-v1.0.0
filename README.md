# 开源多人任务管理平台改造升级 TASK SAAS

### 预览:
http://8.136.81.58:3000/ (v1.0.0)

### 运行:（需docker)
docker build . -t tasksaas:3.0.0 -f Dockerfile(可选)
更改docker-compose.yml文件中services:web:image: tasksaas:3.0.0(可选)

docker-compose build
docker-compose up -d

### 运行2: (可选)
更改settings.py相关数据库、redis配置，运行：
```
python manage.py runserver
```

### 更新:
todo https://www.django-rest-framework.org/




