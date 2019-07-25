# Generated by Django 2.1.10 on 2019-07-25 08:30

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terra_crud', '0005_auto_20190724_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='crudview',
            name='settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='crudview',
            name='ui_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
