# Generated by Django 3.1.7 on 2021-08-06 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0018_auto_20210806_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textblock',
            name='document_fields',
        ),
    ]