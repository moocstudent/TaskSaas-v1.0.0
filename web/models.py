from django.db import models


# Create your models here.
class UserInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    """
    用户信息
    """
    username = models.CharField(verbose_name="用户名", max_length=100, db_index=True)  # db_index=True 索引
    nick_name = models.CharField(verbose_name="昵称", default='', max_length=100, db_index=True,null=True,blank=True)  # db_index=True 索引
    git_username = models.CharField(verbose_name="Git用户名", max_length=100, default='',
                                    db_index=True,null=True,blank=True)  # db_index=True 索引
    email = models.EmailField(verbose_name="邮箱", max_length=100,default='',blank=True,null=True)
    # git 头像或者其他设置的头像
    git_avatar = models.CharField(verbose_name="Git头像", default='', max_length=300,null=True,blank=True)
    mobile_phone = models.CharField(verbose_name="手机号码", max_length=32,null=True,blank=True,default='')
    password = models.CharField(verbose_name="密码", max_length=100)
    git_password = models.CharField(verbose_name="Git密码", default='', max_length=100,null=True,blank=True)
    wechat_openid = models.CharField(verbose_name="微信小程序获取的用户openid", default='', max_length=100,null=True,blank=True)
    wechat_unionid = models.CharField(verbose_name="微信小程序获取的用户unionid", default='', max_length=100,null=True,blank=True)
    wechat_nickname = models.CharField(verbose_name="微信昵称", default='', max_length=100,null=True,blank=True)
    wechat_avatar = models.CharField(verbose_name="微信头像url地址", default='', max_length=150,null=True,blank=True)
    # max_digits 表示整数部分有至多几位，decimal_places表示小数点后最多几位
    forward_score = models.DecimalField(verbose_name="进取分数",default=0.00,max_digits=9,decimal_places=2,null=True,blank=True)

    sys_avatar = models.CharField(verbose_name="系统头像", default='', max_length=300,null=True,blank=True)

    glory_wearing = models.ForeignKey(verbose_name="佩戴的荣誉", null=True, blank=True, to="Glory",
                                on_delete=models.SET_NULL)

    avatar_frame_wearing = models.ForeignKey(verbose_name="佩戴的头像框", null=True, blank=True, to="AvatarFrame",
                                on_delete=models.SET_NULL)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True,null=True)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True,null=True)


    # price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', null=True, blank=True)
    def __str__(self):
        return self.username


# git信息，不同项目关联的不同的git信息
class GitInfoRelation(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(verbose_name="项目id", default=0, null=True, blank=True, to="Project",
                                on_delete=models.SET_NULL)
    git_project_id = models.BigIntegerField(verbose_name="Git项目id", default=0, null=True, blank=True)
    git_access_token = models.CharField(verbose_name="Git访问Token", default='', null=False, blank=False, max_length=60)
    desc = models.CharField(verbose_name="简介", default='', null=True, blank=True, max_length=100)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', null=True, on_delete=models.SET_NULL)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


class PricePolicy(models.Model):
    id = models.BigAutoField(primary_key=True)
    """
    价格策略
    """
    category_choices = {
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    }

    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格')

    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间', help_text='G')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小', help_text='M')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    """
    交易记录
    """
    status_choice = {
        (1, '未支付'),
        (2, '已支付')
    }

    status = models.SmallIntegerField(verbose_name='状态', choices=status_choice)

    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)  # 唯一索引

    user = models.ForeignKey(verbose_name='用户', to='UserInfo', null=True, on_delete=models.SET_NULL)
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', null=True, on_delete=models.SET_NULL)

    count = models.IntegerField(verbose_name='数量(年)', help_text='0表示无限期')

    price = models.IntegerField(verbose_name='实际支付价格')

    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)

    create_datetime = models.DateTimeField(verbose_name='结束时间', auto_now_add=True)


class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    """
    项目表
    """
    COLOR_CHOICES = {
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20bFA4'),
        (6, '#7461c2'),
        (7, '#20bfa3'),
    }

    name = models.CharField(verbose_name='项目名', max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色', choices=COLOR_CHOICES, default=1)
    remark = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    user_space = models.BigIntegerField(verbose_name='项目已使用空间', default=0, help_text='字节')
    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', null=True, on_delete=models.SET_NULL)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='COS桶', max_length=128)
    region = models.CharField(verbose_name='COS区域', max_length=32)


class WorkRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField(verbose_name="主要工作内容",null=True,blank=True)
    project = models.ForeignKey(verbose_name="项目",to="Project",null=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', null=True, related_name='work',
                             on_delete=models.SET_NULL)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    calendar_day = models.CharField(verbose_name="日期时间",max_length=10)
    calendar_day_date = models.DateField(verbose_name="日期时间date",null=False,blank=False,default=None)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now_add=True)



class ProjectUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    """
    项目参与者
    """
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', null=True, related_name='projects',
                             on_delete=models.SET_NULL)

    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)

    invitee = models.ForeignKey(verbose_name='邀请人', to='UserInfo', related_name='invites', on_delete=models.SET_NULL,
                                null=True, blank=True)

    star = models.BooleanField(verbose_name='星标', default=False)

    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)


class Wiki(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容')
    depth = models.IntegerField(verbose_name='深度', default=1)

    # 自关联
    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, related_name='children',
                               on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

class Collect(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    issues = models.ForeignKey(verbose_name='问题',to="Issues",null=True, on_delete=models.SET_NULL)
    wiki = models.ForeignKey(verbose_name='Wiki',to="Wiki",null=True, on_delete=models.SET_NULL)
    file = models.ForeignKey(verbose_name='File',to="FileRepository",null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey(verbose_name='收藏人',to='UserInfo',null=True,on_delete=models.SET_NULL)
    title = models.CharField(verbose_name='标题', max_length=256)
    link = models.CharField(verbose_name='链接',max_length=256)
    type_choices = {
        (1, 'issue'),
        (2, 'wiki'),
        (3, 'file')
    }
    type = models.SmallIntegerField(verbose_name='类型',default=None, choices=type_choices)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    def __str__(self):
        return self.link


class Glory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(verbose_name='荣誉名称', max_length=256)
    desc = models.TextField(verbose_name='荣誉介绍', null=True, blank=True)
    COLOR_CHOICES = {
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20bFA4'),
        (6, '#7461c2'),
        (7, '#20bfa3'),
        (7, '#998899'),
    }
    color = models.SmallIntegerField(verbose_name='颜色', choices=COLOR_CHOICES, default=1)
    pic_url = models.CharField(verbose_name="荣誉图片地址",max_length=256,null=True)
    required_score = models.DecimalField(verbose_name="需要的至少的forward_score分数，不扣分",default=0.00,max_digits=9,decimal_places=2)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

class AvatarFrame(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(verbose_name='荣誉名称', max_length=256)
    desc = models.TextField(verbose_name='荣誉介绍', null=True, blank=True)
    pic_url = models.CharField(verbose_name="荣誉图片地址",max_length=256,null=True)
    cost_score = models.DecimalField(verbose_name="需要花费的forward_score分数，花费后直接扣掉",default=0.00,max_digits=9,decimal_places=2)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

def upload_to(filename):
    return '/'.join(['uploads', filename])


class FileRepository(models.Model):
    id = models.BigAutoField(primary_key=True)
    """文件库对象"""
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    file_type_choices = {
        (1, '文件'),
        (2, '文件夹'),
        (3, 'EditorUpload')
    }
    file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    file_mime_type = models.CharField(verbose_name='文件类型', null=True, blank=True, max_length=80)
    name = models.CharField(verbose_name='文件夹名称', max_length=500, help_text="文件/文件夹名")
    key = models.CharField(verbose_name='文件存储在COS中的KEY', max_length=128, null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True, help_text='字节')
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    file_url = models.CharField(verbose_name='网络路径', max_length=255, null=True, blank=True)
    ab_file_path = models.CharField(verbose_name='服务器绝对路径', max_length=255, null=True, blank=True)
    file = models.FileField(null=True, upload_to=upload_to, max_length=500)

    parent = models.ForeignKey(verbose_name='父级目录', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    update_user = models.ForeignKey(verbose_name='最近更新者', null=True, to='UserInfo', on_delete=models.SET_NULL)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


class Issues(models.Model):
    id = models.BigAutoField(primary_key=True)
    issue_id = models.BigIntegerField(default=0, null=True, blank=True)
    """问题"""
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', null=True, on_delete=models.SET_NULL)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.SET_NULL)

    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述', null=True, blank=True)
    priority_choices = {
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    }
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建/处理中/已解决/已忽略/待反馈/已关闭/重新打开
    status_choices = {
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    }
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True,
                               on_delete=models.SET_NULL)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)

    mode_choices = {
        (1, '公开模式'),
        (2, '隐私模式'),
    }
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='create_problems')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    using_time = models.CharField(verbose_name='用时从创建到已解决到用时format',max_length=30,default=None,null=True,blank=True)

    def __str__(self):
        return self.subject


class IssuesLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    issues = models.ForeignKey(to="Issues", null=True, blank=True, on_delete=models.SET_NULL)
    """问题"""
    creator = models.ForeignKey(verbose_name='更新者', to='UserInfo', null=True, blank=True, on_delete=models.SET_NULL)
    record = models.TextField(verbose_name='更新记录', null=True, blank=True)

    type_choices = {
        (1, '新建'),
        (2, '更新'),
        (3, '回复'),
        (4, '删除'),
    }

    log_type = models.SmallIntegerField(verbose_name='日志类型', choices=type_choices, default=2)
    # 或之前issues再次更改，会再产生一条新的issuesChangeLog，create_datetime对应其latest_update_datetime
    create_datetime = models.DateTimeField(verbose_name='创建时间,将等同于当时更新issues的更新时间,', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.issues


class Module(models.Model):
    id = models.BigAutoField(primary_key=True)
    """模块(里程碑)"""
    project = models.ForeignKey(verbose_name='项目', null=True, to='Project', on_delete=models.SET_NULL)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class InfoLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    type_choices = {
        (1, '系统信息'),
        (2, '提醒信息'),
        # (3, '回复'),
        # (4, '删除'),
    }
    project_id = models.ForeignKey(verbose_name="项目",to="Project",null=True,on_delete=models.SET_NULL)
    type = models.SmallIntegerField(verbose_name='信息类型', choices=type_choices, default=2)
    content = models.TextField(verbose_name="信息内容", default='')
    pure_content = models.TextField(verbose_name="信息内容取净值，如去掉a标签", default='',null=True,blank=True)
    pure_link = models.CharField(verbose_name="链接指向",default='',max_length=300,null=True,blank=True)
    sender = models.ForeignKey(verbose_name='发送者', related_name='sender',to='UserInfo', null=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey(verbose_name='接受者', to='UserInfo',related_name='receiver', null=True, on_delete=models.SET_NULL)
    status_choices = {
        (1, '未读'),
        (2, '已读'),
        # (3, '回复'),
        # (4, '删除'),
    }
    status = models.SmallIntegerField(verbose_name="信息状态",choices=status_choices,default=1)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    def __str__(self):
        return self.content


class IssuesType(models.Model):
    id = models.BigAutoField(primary_key=True)
    """问题类型 例如：任务，功能，Bug，需求确认"""

    PROJECT_INIT_LIST = ["任务", "功能", "Bug", "需求确认"]

    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', null=True, to='Project', on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class IssuesReply(models.Model):
    id = models.BigAutoField(primary_key=True)
    """ 问题回复"""

    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)

    issues = models.ForeignKey(verbose_name='问题', db_column='issues_pk', to="Issues", null=True,
                               on_delete=models.SET_NULL)
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', null=True, related_name='create_reply',
                                on_delete=models.SET_NULL)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复', to='self', null=True, blank=True, on_delete=models.SET_NULL)


class ProjectInvite(models.Model):
    id = models.BigAutoField(primary_key=True)
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count = models.PositiveIntegerField(verbose_name='限制数量', null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', null=True, related_name='create_invite',
                                on_delete=models.SET_NULL)


class ConfigSetting(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(verbose_name='项目', to='Project', null=True, on_delete=models.SET_NULL)
    config_choices = (
        ('spider','taskSpider开启task网络爬虫'),
    )
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    user = models.ForeignKey(verbose_name='谁的配置', to='UserInfo', null=True, related_name='whos_conf',
                                on_delete=models.SET_NULL)

