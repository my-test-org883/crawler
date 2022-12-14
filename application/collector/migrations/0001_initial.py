# Generated by Django 3.0.5 on 2020-11-26 19:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidOs',
            fields=[
                ('os_version', models.CharField(max_length=25, primary_key=True, serialize=False, unique=True)),
                ('os_code', models.CharField(max_length=3)),
            ],
            options={
                'verbose_name_plural': 'Android Os DB',
            },
        ),
        migrations.CreateModel(
            name='CarrierInformation',
            fields=[
                ('carrier_code', models.CharField(max_length=3, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Carrier Database',
            },
        ),
        migrations.CreateModel(
            name='ModelInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_model_name', models.CharField(max_length=15)),
                ('project', models.CharField(max_length=50, unique=True)),
                ('model_name', models.CharField(max_length=50)),
                ('os', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.AndroidOs')),
            ],
            options={
                'verbose_name_plural': 'Model Information',
            },
        ),
        migrations.CreateModel(
            name='TasksInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_code', models.CharField(max_length=50)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.ModelInfo')),
            ],
            options={
                'verbose_name_plural': 'Tasks Information',
                'unique_together': {('task_code', 'model')},
            },
        ),
        migrations.CreateModel(
            name='QueryHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=16)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.ModelInfo')),
                ('os', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.AndroidOs')),
            ],
            options={
                'verbose_name_plural': 'Query History',
                'unique_together': {('model', 'os')},
            },
        ),
        migrations.CreateModel(
            name='Changelists',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cl_number', models.CharField(max_length=15)),
                ('cl_source', models.CharField(max_length=15)),
                ('cl_type', models.CharField(max_length=5)),
                ('relevance', models.CharField(blank=True, max_length=50)),
                ('is_smr', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, max_length=500)),
                ('carrier_info', models.ManyToManyField(to='collector.CarrierInformation')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.ModelInfo')),
                ('os', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collector.AndroidOs')),
                ('task_list', models.ManyToManyField(to='collector.TasksInformation')),
            ],
            options={
                'verbose_name_plural': 'Changelists',
                'unique_together': {('cl_number', 'model', 'cl_type')},
            },
        ),
    ]
