# Generated by Django 3.1.7 on 2021-07-12 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0006_auto_20210712_1453'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='failure_conditions',
        ),
        migrations.RemoveField(
            model_name='question',
            name='parent_option',
        ),
        migrations.RemoveField(
            model_name='question',
            name='success_conditions',
        ),
        migrations.RemoveField(
            model_name='question',
            name='unsure_options',
        ),
    ]
