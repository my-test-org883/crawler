# Generated by Django 3.0.5 on 2020-12-09 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collector', '0004_changelists_branch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelists',
            name='cl_source',
            field=models.CharField(max_length=50),
        ),
    ]