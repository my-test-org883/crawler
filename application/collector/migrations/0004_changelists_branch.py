# Generated by Django 3.0.5 on 2020-12-03 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0003_auto_20201201_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelists',
            name='branch',
            field=models.CharField(default='N/R', max_length=100),
            preserve_default=False,
        ),
    ]
