import datetime

from django.db.models import Q

from TaskChat import constants
from TaskChat.consumers import push_message_to_group
from TaskSaasAPP import date_util
from utils import encrypt
from web.models import Issues, InfoLog


def run():
    print("hello,world")


# 这里是创建django_apscheduler 任务的固定代码
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job

# 1.实例化调度器
scheduler = BackgroundScheduler()

# 2.调度器使用DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), "default")

# 3.设置定时任务，选择方式为interval，时间间隔为10s　　date：希望在某个时间仅运行一次，# 例如在2023-04-14 20:12:00 仅执行一次
# 　　interval：要以固定的时间间隔运行作业时使用， # 任务隔10分钟执行一次，还可以设置days、hours、seconds参数也可以设置日期范围，start_date-end_date
# 　　cron：每天固定时间执行任务， 例如每天9点30分10秒 执行一次,
# @register_job(scheduler, 'cron', hour='9', minute='30', second='10',id='task_time')
try:
    @register_job(scheduler, "cron", hour='0',minute='30', id='deadline_task_job', replace_existing=True)
    def my_job():
        # 这里写你要执行的任务
        issues_today_deadline = Issues.objects.filter(end_date__exact=datetime.datetime.now())
        for i in issues_today_deadline:
            print('deadline task job : >> {}-{}-{}'.format(i.project_id, i.subject, i.end_date))
            if i.assign:
                proj_creator = i.project.creator
                msg = '你被指派的task:' + i.subject + ' 今日截止'
                push_message_to_group(encrypt.md5(i.assign.username) + '__' + str(i.project_id), msg,
                                      constants.push_message_key, proj_creator.username)
                info_log = InfoLog(content=msg, sender=proj_creator, receiver=i.assign, type=1, project_id=i.project,
                                   pure_link=('/manage/{}/issues/detail/{}/'.format(i.project_id,i.issue_id)), pure_content=msg)
                info_log.save()
            if i.attention:
                attentions = i.attention.all()
                proj_creator = i.project.creator
                msg = '你关注的task:' + i.subject + ' 今日截止'
                for at in attentions:
                    push_message_to_group(encrypt.md5(at.username) + '__' + str(i.project_id),
                                          msg,
                                          constants.push_message_key, proj_creator.username)
                    info_log = InfoLog(content=msg, sender=proj_creator, receiver=at, type=1,
                                       project_id=i.project,
                                       pure_link=('/manage/{}/issues/detail/{}/'.format(i.project_id, i.issue_id)),
                                       pure_content=msg)
                    info_log.save()

except Exception as e:
    print(e)
    # 遇到错误，停止定时器
    scheduler.shutdown()
# 4.开启定时任务
scheduler.start()
