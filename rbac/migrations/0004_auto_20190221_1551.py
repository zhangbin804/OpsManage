# Generated by Django 2.0.5 on 2019-02-21 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0003_auto_20190218_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='url',
            field=models.CharField(max_length=64, verbose_name='带正则的url'),
        ),
    ]
