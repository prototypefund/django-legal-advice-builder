# Generated by Django 3.1.7 on 2021-07-17 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0007_auto_20210712_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='condition',
            name='message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='condition',
            name='then_question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='legal_advice_builder.question'),
        ),
        migrations.AlterField(
            model_name='condition',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='legal_advice_builder.question'),
        ),
    ]