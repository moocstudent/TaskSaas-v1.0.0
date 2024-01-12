from django.conf.urls import static
from django.urls import re_path, include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from TaskChat import chat_views, consumers
from TaskSaas.api import oauth_callback_api, user_api, collect_api, wx_api, calendar, project_user_api, reply_api
from web.views import account, home, project, manage, issues, cache, setting, file, wiki, dashboard, tool, module, \
    sentry, userinfo_view, glory, milestone, sys_config
from web.views.upload import FileUploadView

urlpatterns = [
    # scheduler.run(),

    re_path(r'^MP_verify_O7ZsD2KZoE5w9Usg.txt/', wx_api.wx_verify_txt, name='wx_verify_txt'),
    re_path(r'^wechat_entry_api/', wx_api.wx_entry_api, name='wechat_entry_api'),
    re_path(r'^wechat_callback_api/', wx_api.wx_callback_api, name='wechat_callback_api'),

    path('token_login', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token_refresh', TokenRefreshView.as_view(), name="token_refresh"),
    path('token_verify', TokenVerifyView.as_view(), name="token_verify"),

    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': 'web/static'}, name='static'),
    re_path(r'^register/', account.register, name='register'),
    re_path(r'^login/sms/', account.login_sms, name='login_sms'),
    re_path(r'^login/', account.login, name='login'),
    re_path(r'^login/', account.login, name='login'),

    re_path(r'^do_login/', account.do_login, name='do_login'),
    re_path(r'^do_profile/', userinfo_view.do_profile, name='do_profile'),
    re_path(r'^get_token/', account.get_token, name='get_token'),
    re_path(r'^get_user_by_openid/', userinfo_view.get_user_by_openid, name='get_user_by_openid'),
    re_path(r'^bind_user_with_openid/', userinfo_view.bind_user_with_openid, name='bind_user_with_openid'),



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
    # 项目列表json response
    re_path(r'^project_list/', project.project_list_json, name='project_list_json'),
    re_path(r'^do_issue_list/', issues.do_issue_list, name='do_issue_list'),

    re_path(r'^glory_list/', glory.GloryAPI.as_view(), name='glory_list'),
    re_path(r'^glory_detail/(?P<glory_id>\d+)', glory.glory_detail, name='glory_detail'),
    # dashboard json response
    re_path(r'^dashboard_json/$', dashboard.dashboard_json, name='dashboard_json'),

    re_path(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    re_path(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar,
            name='project_unstar'),

    re_path(r'^workbench_json/$', manage.workbench_json, name='workbench_json'),
    re_path(r'^remind_json/$', manage.remind_json, name='remind_json'),
    # 项目管理
    # 路由分发
    re_path(r'^sys_config/$', setting.sys_config, name='sys_config'),
    re_path(r'^sys_config_notify/$', sys_config.sys_config_notify, name='sys_config_notify'),
    re_path(r'^sys_config_template/$', sys_config.sys_config_template, name='sys_config_template'),
    re_path(r'^sys_config_notify_switch/$', sys_config.sys_config_notify_switch, name='sys_config_notify_switch'),

    re_path(r'^profile/$', user_api.profile, name='profile'),
    re_path(r'^profile_git/$', user_api.profile_git, name='profile_git'),

    re_path(r'^sentry_evt/', sentry.sentry_evt, name='sentry_evt'),
    re_path(r'^sentry_setup/', sentry.sentry_setup, name='sentry_setup'),

    re_path(r'^fileupload/$', file.uploadfile_common, name='fileupload'),
    re_path(r'^profileupload/$', file.uploadfile_profile, name='profileupload'),


re_path(r'^manage/(?P<project_id>\d+)/', include([

    re_path(r'^cache_set/', cache.cache_set, name='cache'),
    re_path(r'^day_cache_set/', cache.day_cache_set, name='day_cache'),
    re_path(r'^main_echart_legend_cache_set/', cache.main_echart_legend_cache_set, name='main_echart_legend_cache'),
    re_path(r'^echart_legend_cache_set/', cache.echart_legend_cache_set, name='echart_legend_cache'),
    re_path(r'^attention_cache_set/', cache.attention_cache_set, name='attention_cache'),

    re_path(r'^statistics/$', manage.statistics, name='statistics'),
    re_path(r'^milestone/$', milestone.milestone, name='milestone'),
    re_path(r'^milestone_add_or_update/$', milestone.milestone_add_or_update, name='milestone_add_or_update'),
    re_path(r'^milestone_del/$', milestone.milestone_del, name='milestone_del'),
    re_path(r'^git/$', manage.git, name='git'),
    re_path(r'^tool/$', manage.tool, name='tool'),
    re_path(r'^tool_generate_str/$', tool.generate_random_chinese_string, name='tool_generate_str'),
    re_path(r'^tool_encrypt_druid_password/$', tool.encrypt_druid_password, name='tool_encrypt_druid_password'),
    re_path(r'^resolve_mask_of_ipv4/$', tool.resolve_mask_of_ipv4, name='resolve_mask_of_ipv4'),
    # re_path(r'^color_picker/$', tool.color_picker, name='color_picker'),

    re_path(r'^workbench/$', manage.workbench, name='workbench'),
    re_path(r'^calendar/$', manage.calendar, name='calendar'),
    re_path(r'^remind/$', manage.remind, name='remind'),

    # 导出工作内容
    re_path(r'^calendar_time_range_export_works/$', calendar.calendar_time_range_export_works, name='calendar_time_range_export_works'),
    # 导出任务列表
    re_path(r'^calendar_time_range_export_tasks/$', calendar.calendar_time_range_export_tasks, name='calendar_time_range_export_tasks'),

    re_path(r'^remind_status/$', manage.remind_status, name='remind_status'),
    re_path(r'^collect/$', manage.collect, name='collect'),
    re_path(r'^make_collect/$', collect_api.make_collect, name='make_collect'),
    re_path(r'^wiki_collect/$', collect_api.wiki_collect, name='wiki_collect'),
    re_path(r'^file_collect/$', collect_api.file_collect, name='file_collect'),

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
    re_path(r'^setting/common/$', setting.setting_common, name='setting_common'),
    re_path(r'^setting/common_spider/$', setting.setting_common_spider, name='setting_common_spider'),
    re_path(r'^setting/module/$', module.setting_module, name='setting_module'),
    re_path(r'^setting/module_del/$', module.setting_module_del, name='setting_module_del'),

    re_path(r'^issues/$', issues.issues, name='issues'),
    re_path(r'^issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
    re_path(r'^issues/record/(?P<issues_pk>\d+)/$', issues.issues_record, name='issues_record'),
    re_path(r'^issues/change/(?P<issues_pk>\d+)/$', issues.issues_change, name='issues_change'),
    re_path(r'^issues/del/$', issues.issues_del, name='issues_del'),
    re_path(r'^issues/invite/url/$', issues.invite_url, name='invite_url'),

    #delete reply by id
    re_path(r'^del_reply/$', reply_api.del_reply, name='del_reply'),

    re_path(r'^dashboard/$', dashboard.dashboard, name='dashboard'),

    re_path(r'^send_private_hint_msg/$', consumers.send_private_hint_msg, name='send_private_hint_msg'),

    # work_record
    re_path(r'^add_work_record/$', manage.work_record, name='add_work_record'),
    re_path(r'^work_record_update/$',  manage.work_record_update, name='work_record_update'),
    re_path(r'^find_work_record/$',  manage.find_work_record, name='find_work_record'),
    re_path(r'^work_record_list/$',  manage.work_record_list, name='work_record_list'),


    #remove user from project by invitee
    re_path(r'^remove_user_from_project/$',  project_user_api.remove_user_from_project, name='remove_user_from_project'),








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
