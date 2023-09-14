# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-09-13 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20230913_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filerepository',
            name='file_type',
            field=models.SmallIntegerField(choices=[(1, '文件'), (2, '文件夹')], verbose_name='类型'),
        ),
        migrations.AlterField(
            model_name='issues',
            name='priority',
            field=models.CharField(choices=[('danger', '高'), ('success', '低'), ('warning', '中')], default='danger', max_length=12, verbose_name='优先级'),
        ),
        migrations.AlterField(
            model_name='issues',
            name='status',
            field=models.SmallIntegerField(choices=[(6, '已关闭'), (2, '处理中'), (7, '重新打开'), (4, '已忽略'), (3, '已解决'), (5, '待反馈'), (1, '新建')], default=1, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='pricepolicy',
            name='category',
            field=models.SmallIntegerField(choices=[(3, '其他'), (2, '收费版'), (1, '免费版')], default=2, verbose_name='收费类型'),
        ),
        migrations.AlterField(
            model_name='project',
            name='color',
            field=models.SmallIntegerField(choices=[(3, '#ebc656'), (6, '#7461c2'), (7, '#20bfa3'), (5, '#20bFA4'), (4, '#a2d148'), (1, '#56b8eb'), (2, '#f28033')], default=1, verbose_name='颜色'),
        ),
    ]
