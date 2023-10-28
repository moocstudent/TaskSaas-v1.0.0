import datetime

from TaskChat import constants
from TaskChat.consumers import push_message_to_group
from utils import encrypt
from web.models import Issues, InfoLog

# remind the user if the task nearly deadline
def remind_deadline():
    print('remind_deadline invoked')
    issues_today_deadline = Issues.objects.filter(end_date__exact=datetime.datetime.now())
    for i in issues_today_deadline:
        print('deadline task job : >> {}-{}-{}'.format(i.project_id, i.subject, i.end_date))
        if i.assign:
            proj_creator = i.project.creator
            msg = '你被指派的task:' + i.subject + ' 今日截止'
            push_message_to_group(encrypt.md5(i.assign.username) + '__' + str(i.project_id), msg,
                                  constants.push_message_key, proj_creator.username)
            info_log = InfoLog(content=msg, sender=proj_creator, receiver=i.assign, type=1, project_id=i.project,
                               pure_link=('/manage/{}/issues/detail/{}/'.format(i.project_id, i.issue_id)),
                               pure_content=msg)
            if InfoLog.objects.filter(content=info_log.content,sender=info_log.sender,receiver=info_log.receiver,
                                      type=info_log.type,project_id=info_log.project_id,pure_link=info_log.pure_link,
                                      pure_content=info_log.pure_content).exists():
                print('deadline infolog already exists')
            else:
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
                if InfoLog.objects.filter(content=info_log.content, sender=info_log.sender, receiver=info_log.receiver,
                                          type=info_log.type, project_id=info_log.project_id,
                                          pure_link=info_log.pure_link,
                                          pure_content=info_log.pure_content).exists():
                    print('deadline infolog already exists')
                else:
                    info_log.save()

