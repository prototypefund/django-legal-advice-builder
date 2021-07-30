import json

from django import forms
from django.forms import fields
from django.forms.models import model_to_dict
from django.utils import dateformat
from tinymce.widgets import TinyMCE

from .models import Answer
from .models import Condition
from .models import Document
from .models import DocumentType
from .models import LawCase
from .models import Question
from .models import Questionaire
from .widgets import ChoiceWidget
from .widgets import ConditionsWidget
from .widgets import CustomCheckboxSelect
from .widgets import CustomRadioSelect


class DispatchQuestionFieldTypeMixin:

    def get_field_for_question_type(self, question, options, form_fields, required=True):
        if question.field_type in [question.SINGLE_OPTION, question.YES_NO]:
            form_fields['option'] = fields.ChoiceField(
                choices=options.items(),
                widget=CustomRadioSelect,
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.MULTIPLE_OPTIONS:
            form_fields['option'] = fields.MultipleChoiceField(
                choices=options.items(),
                widget=CustomCheckboxSelect,
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.SINGLE_LINE:
            form_fields['text'] = fields.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.TEXT:
            form_fields['text'] = fields.CharField(
                widget=forms.Textarea(attrs={'class': 'form-control'}),
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.DATE:
            form_fields['date'] = fields.DateField(
                required=required,
                label=question.text,
                help_text=question.help_text,
                widget=forms.DateTimeInput(attrs={'type': 'date',
                                                  'class': 'form-control'})
            )


class FormControllClassMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}


class WizardForm(forms.Form, DispatchQuestionFieldTypeMixin):

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.options = kwargs.pop('options') or {}
        super().__init__(*args, **kwargs)

        if self.question:
            self.get_field_for_question_type(self.question, self.options, self.fields)
            self.fields['question'] = fields.CharField(
                initial=self.question.id,
                widget=forms.HiddenInput()
            )


class RenderedDocumentForm(forms.ModelForm):
    answer_id = fields.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Answer
        fields = ['rendered_document', 'answer_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if TinyMCE:
            self.fields['rendered_document'].widget = TinyMCE(
                attrs={'cols': 80, 'rows': 30})
        self.fields['answer_id'].initial = self.instance.id


class PrepareDocumentForm(forms.Form):
    name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        super().__init__(*args, **kwargs)
        if not self.document:
            self.fields['document_type'] = forms.ModelChoiceField(
                queryset=DocumentType.objects.all())
        else:
            self.initial = model_to_dict(self.document)

    def save(self):
        if not self.document:
            document = Document.objects.create(
                **self.cleaned_data
            )
            return document
        else:
            name = self.cleaned_data.get('name')
            self.document.name = name
            self.document.save()
            return self.document


class QuestionForm(forms.Form, DispatchQuestionFieldTypeMixin):
    question = fields.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = Question.objects.get(id=self.initial.get('question'))
        self.get_field_for_question_type(self.question, self.question.options, self.fields, False)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            return dateformat.format(date, "m.d.Y")


class QuestionConditionForm(forms.ModelForm):
    conditions = forms.CharField(required=False)

    class Meta:
        model = Question
        fields = ('conditions',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['conditions'].widget = ConditionsWidget(
            question=self.instance)

    def save(self, commit=True):
        if self.cleaned_data['conditions']:
            self.instance.conditions.all().delete()
            conditions = json.loads(self.cleaned_data.pop('conditions'))
            for condition in conditions:
                if 'id' in condition:
                    condition.pop('id')
                condition['question'] = self.instance
                if condition.get('then_value'):
                    if 'question' in condition.get('then_value'):
                        question_id = condition.get('then_question')
                        question = Question.objects.filter(
                            id=question_id).first()
                        if question:
                            condition['then_value'] = 'question'
                            condition['then_question'] = question
                    else:
                        if 'then_question' in condition:
                            condition.pop('then_question')
                    condition = Condition.objects.create(**condition)
        return self.instance


class QuestionUpdateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = Question
        fields = ('text', 'field_type', 'options', 'information')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['options'].widget = ChoiceWidget()
        question = self.instance
        if question.field_type not in [Question.SINGLE_OPTION,
                                       Question.YES_NO,
                                       Question.MULTIPLE_OPTIONS]:
            del self.fields['options']

    def save(self, commit=True):
        options = self.cleaned_data.get('options').keys()
        question = super().save(commit=commit)
        question.clean_up_conditions(options)
        return question


class QuestionCreateForm(FormControllClassMixin, forms.ModelForm):
    parent_question = fields.CharField(required=False,
                                       widget=forms.HiddenInput)

    class Meta:
        model = Question
        fields = ('text', 'field_type')

    def __init__(self, **kwargs):
        if 'parent_question' in kwargs:
            self.parent_question = kwargs.pop('parent_question')
        super().__init__(**kwargs)
        if hasattr(self, 'parent_question') and self.parent_question:
            self.fields['parent_question'].initial = self.parent_question


class LawCaseCreateForm(FormControllClassMixin, forms.ModelForm):
    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(),
                                           required=False)

    class Meta:
        model = LawCase
        fields = ('title', 'document_type', 'description')


class LawCaseUpdateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = LawCase
        fields = ('title', 'description')


class QuestionaireForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = Questionaire
        fields = ('title', 'success_message')
