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

### 剩余可更新:
todo https://www.django-rest-framework.org/

- 1.对gitlab配置对GitInfoRelation的CRUD操作，主要是对于对接Gitlab而言，在每个项目下可能存在多个Gitlab仓库（或其他git仓库，但暂不支持除gitlab的其他仓库对接）   
- 2.对项目的在线或预上线版本的日志的管理，之前打算的是用sentry进行接入，并将日志展示在"提醒"  
- 3.聊天室里的视频聊天功能，已经选好了对应的webrtc方案:(mediasoup,jitsi,janus其中一个)，目的主要是实现聊天室的实时互动，加之可以进行电脑屏幕投屏     
- 4.对Tasks、Issues进行数据分析处理，将关键字和相关Tasks、Issues关联分类，并可以提供给类似问题解决方案  
- 5.对任务的优先级、紧急程度、重要程度进行分类，可以对任务进行前面分类的排序，可以对任务进行批量操作，比如批量标记为已解决   




