# Generated by Django 3.1.7 on 2021-07-17 18:25

from django.db import migrations


def add_question_fk_to_condition(apps, schema_editor):
    Condition = apps.get_model('legal_advice_builder', 'Condition')
    Question = apps.get_model('legal_advice_builder', 'Question')
    for condition in Condition.objects.all():
        if condition.then_value and 'question' in condition.then_value:
            question_id = condition.then_value.split('_')[1]
            questions = Question.objects.filter(id=question_id)
            if questions.exists():
                condition.then_value = 'question'
                condition.then_question = questions.first()
                condition.save()


class Migration(migrations.Migration):

    dependencies = [
        ('legal_advice_builder', '0008_auto_20210717_1549'),
    ]

    operations = [
        migrations.RunPython(add_question_fk_to_condition)
    ]
