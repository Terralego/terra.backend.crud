# Generated by Django 2.1.12 on 2019-09-02 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terra_crud', '0010_auto_20190830_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crudview',
            name='templates',
            field=models.ManyToManyField(blank=True, related_name='crud_views', to='template_model.Template'),
        ),
    ]
