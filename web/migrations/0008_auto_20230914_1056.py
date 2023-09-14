# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-09-14 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20230913_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issues',
            name='mode',
            field=models.SmallIntegerField(choices=[(2, '隐私模式'), (1, '公开模式')], default=1, verbose_name='模式'),
        ),
        migrations.AlterField(
            model_name='issues',
            name='status',
            field=models.SmallIntegerField(choices=[(1, '新建'), (2, '处理中'), (4, '已忽略'), (6, '已关闭'), (5, '待反馈'), (3, '已解决'), (7, '重新打开')], default=1, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='pricepolicy',
            name='category',
            field=models.SmallIntegerField(choices=[(3, '其他'), (2, '收费版'), (1, '免费版')], default=2, verbose_name='收费类型'),
        ),
        migrations.AlterField(
            model_name='project',
            name='color',
            field=models.SmallIntegerField(choices=[(2, '#f28033'), (5, '#20bFA4'), (3, '#ebc656'), (6, '#7461c2'), (4, '#a2d148'), (7, '#20bfa3'), (1, '#56b8eb')], default=1, verbose_name='颜色'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.SmallIntegerField(choices=[(2, '已支付'), (1, '未支付')], verbose_name='状态'),
        ),
    ]
