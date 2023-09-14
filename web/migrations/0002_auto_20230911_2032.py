# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-09-11 20:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issues',
            name='priority',
            field=models.CharField(choices=[('warning', '中'), ('success', '低'), ('danger', '高')], default='danger', max_length=12, verbose_name='优先级'),
        ),
        migrations.AlterField(
            model_name='issues',
            name='status',
            field=models.SmallIntegerField(choices=[(3, '已解决'), (1, '新建'), (6, '已关闭'), (7, '重新打开'), (5, '待反馈'), (4, '已忽略'), (2, '处理中')], default=1, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='pricepolicy',
            name='category',
            field=models.SmallIntegerField(choices=[(2, '收费版'), (3, '其他'), (1, '免费版')], default=2, verbose_name='收费类型'),
        ),
        migrations.AlterField(
            model_name='project',
            name='color',
            field=models.SmallIntegerField(choices=[(2, '#f28033'), (7, '#20bfa3'), (3, '#ebc656'), (5, '#20bFA4'), (6, '#7461c2'), (1, '#56b8eb'), (4, '#a2d148')], default=1, verbose_name='颜色'),
        ),
    ]
