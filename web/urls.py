from django.conf.urls import static
from django.urls import re_path, include, path

from TaskChat import chat_views, consumers
from TaskSaas.api import oauth_callback_api, user_api, collect_api
from web.views import account, home, project, manage, issues, cache, setting, file, wiki, dashboard, tool, module, \
    sentry
from web.views.upload import FileUploadView
from TaskSaasAPP import scheduler

urlpatterns = [
    # scheduler.run(),

    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': 'web/static'}, name='static'),
    re_path(r'^register/', account.register, name='register'),
    re_path(r'^login/sms/', account.login_sms, name='login_sms'),
    re_path(r'^login/', account.login, name='login'),
    re_path(r'^logout/', account.logout, name='logout'),
    re_path(r'^image/code/', account.image_code, name='image_code'),
    re_path(r'^send/sms/', account.send_sms, name='send_sms'),
    re_path(r'^index/', home.index, name='index'),
    re_path(r'^callback/gitlab/$', oauth_callback_api.callback, name='callback'),
    # re_path(r'^callback/gitlab/token/', oauth_callback_api.callback_token, name='callback_token'),
    re_path(r'^gitlab/myprofile/$', oauth_callback_api.callback_userpassword, name='git_myprofile'),
    re_path(r'^webhook/gitlab/$', oauth_callback_api.webhook_callback, name='webhook_callback'),
    path('', home.index, name=''),

    re_path(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view()),
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

    re_path(r'^profile/$', user_api.profile, name='profile'),
    re_path(r'^profile_git/$', user_api.profile_git, name='profile_git'),

    re_path(r'^sentry_evt/', sentry.sentry_evt, name='sentry_evt'),
    re_path(r'^sentry_setup/', sentry.sentry_setup, name='sentry_setup'),

re_path(r'^manage/(?P<project_id>\d+)/', include([

    re_path(r'^cache_set/', cache.cache_set, name='cache'),
    re_path(r'^day_cache_set/', cache.day_cache_set, name='day_cache'),
    re_path(r'^main_echart_legend_cache_set/', cache.main_echart_legend_cache_set, name='main_echart_legend_cache'),
    re_path(r'^echart_legend_cache_set/', cache.echart_legend_cache_set, name='echart_legend_cache'),
    re_path(r'^attention_cache_set/', cache.attention_cache_set, name='attention_cache'),

    re_path(r'^statistics/$', manage.statistics, name='statistics'),
    re_path(r'^git/$', manage.git, name='git'),
    re_path(r'^tool/$', manage.tool, name='tool'),
    re_path(r'^tool_generate_str/$', tool.generate_random_chinese_string, name='tool_generate_str'),
    re_path(r'^tool_encrypt_druid_password/$', tool.encrypt_druid_password, name='tool_encrypt_druid_password'),

    re_path(r'^workbench/$', manage.workbench, name='workbench'),
    re_path(r'^calendar/$', manage.calendar, name='calendar'),
    re_path(r'^remind/$', manage.remind, name='remind'),
    re_path(r'^remind_status/$', manage.remind_status, name='remind_status'),
    re_path(r'^collect/$', manage.collect, name='collect'),
    re_path(r'^make_collect/$', collect_api.make_collect, name='make_collect'),

    re_path(r'^wiki/$', wiki.wiki, name='wiki'),
    re_path(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
    re_path(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
    re_path(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
    re_path(r'^wiki/upload/', wiki.wiki_upload, name='wiki_upload'),
    re_path(r'^wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),

    re_path(r'^file/$', file.file, name='file'),
    re_path(r'^file/delete/$', file.file_delete, name='file_delete'),
    re_path(r'^cos/credential/$', file.cos_credential, name='cos_credential'),
    re_path(r'^file/post/$', file.upload_file, name='file_post'),
    re_path(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),

    re_path(r'^setting/$', setting.setting, name='setting'),
    re_path(r'^setting/delete/$', setting.setting_delete, name='setting_delete'),
    re_path(r'^setting/module/$', module.setting_module, name='setting_module'),
    re_path(r'^setting/module_del/$', module.setting_module_del, name='setting_module_del'),

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

    # re_path('tool/',include([
    #     path('', manage.tool, name='tool'),
    #     re_path(r'^generate/(?P<str_length>\d+)/$', tool.generate_random_chinese_string,name='tool_generate_str'),
    # ],None)),

    # 邀请页面
re_path(r'^invite/join/(?P<code>\w+)/$', issues.invite_join, name='invite_join'),

]
