# Generated by Django 2.1.2 on 2019-02-18 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='username',
            field=models.CharField(default='admin', max_length=32, verbose_name='真实姓名'),
        ),
    ]