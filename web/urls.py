from django.conf.urls import static
from django.urls import re_path, include, path

from TaskChat import chat_views, consumers
from TaskSaasAPP import settings
from web.views import account, home, project, manage, issues, cache, setting, file, wiki, dashboard

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': 'web/static'}, name='static'),
    re_path(r'^register/', account.register, name='register'),
    re_path(r'^login/sms/', account.login_sms, name='login_sms'),
    re_path(r'^login/', account.login, name='login'),
    re_path(r'^logout/', account.logout, name='logout'),
    re_path(r'^image/code/', account.image_code, name='image_code'),
    re_path(r'^send/sms/', account.send_sms, name='send_sms'),
    re_path(r'^index/', home.index, name='index'),
    path('', home.index, name=''),
    re_path(r'^cache_set/', cache.cache_set, name='cache'),
    re_path(r'^day_cache_set/', cache.day_cache_set, name='day_cache'),
    re_path(r'^echart_legend_cache_set/', cache.echart_legend_cache_set, name='echart_legend_cache'),
    # re_path(r'^issues_status_cache_set/', cache.issues_status_cache_set, name='issues_status_cache'),
    # 项目列表
    re_path(r'^project/list/', project.project_list, name='project_list'),
    re_path(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    re_path(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar,
            name='project_unstar'),

    re_path(r'^workbench_json/$', manage.workbench_json, name='workbench_json'),
    # 项目管理
    # 路由分发
    re_path(r'^sys_setting/$', setting.sys_setting, name='sys_setting'),

    re_path(r'^manage/(?P<project_id>\d+)/', include([

        re_path(r'^statistics/$', manage.statistics, name='statistics'),
        re_path(r'^git/$', manage.git, name='git'),
        re_path(r'^workbench/$', manage.workbench, name='workbench'),

        re_path(r'^wiki/$', wiki.wiki, name='wiki'),
        re_path(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        re_path(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        re_path(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        re_path(r'^wiki/upload/', wiki.wiki_upload, name='wiki_upload'),
        re_path(r'^wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),

        re_path(r'^file/$', file.file, name='file'),
        re_path(r'^file/delete/$', file.file_delete, name='file_delete'),
        re_path(r'^cos/credential/$', file.cos_credential, name='cos_credential'),
        re_path(r'^file/post/$', file.file_post, name='file_post'),
        re_path(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),

        re_path(r'^setting/$', setting.setting, name='setting'),
        re_path(r'^setting/delete/$', setting.setting_delete, name='setting_delete'),

        re_path(r'^issues/$', issues.issues, name='issues'),
        re_path(r'^issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
        re_path(r'^issues/record/(?P<issues_pk>\d+)/$', issues.issues_record, name='issues_record'),
        re_path(r'^issues/change/(?P<issues_pk>\d+)/$', issues.issues_change, name='issues_change'),
        re_path(r'^issues/invite/url/$', issues.invite_url, name='invite_url'),

        re_path(r'^dashboard/$', dashboard.dashboard, name='dashboard'),

    ], None)),

    re_path(r'^chat/', include([
        path('', chat_views.chat, name='chat-url'),
        # path('<str:room_name>/', chat_views.room, name='room'),
        path('ws/', consumers.ChatConsumer.as_asgi()),
    ], None)),

    # 邀请页面
    re_path(r'^invite/join/(?P<code>\w+)/$', issues.invite_join, name='invite_join'),

]
