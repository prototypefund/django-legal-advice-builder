from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from legal_advice_builder.utils import clean_html_field

from .law_case import LawCase


class Answer(models.Model):
    law_case = models.ForeignKey(LawCase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                null=True, on_delete=models.SET_NULL)
    answers = models.JSONField(null=True, default=dict, blank=True, encoder=DjangoJSONEncoder)
    rendered_document = models.TextField(blank=True, verbose_name=_('Rendered Document'))
    extra_info = models.JSONField(default=dict, blank=True, null=True)
    external_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        date = str(self.created_at.date())
        return '{} {} ({})'.format(date, self.law_case.title, self.creator)

    def save(self, *args, **kwargs):
        self.rendered_document = clean_html_field(self.rendered_document)
        return super().save(*args, **kwargs)

    def save_rendered_document(self):
        if not self.rendered_document:
            self.rendered_document = self.template
            self.save()

    @property
    def template(self):
        return self.law_case.document.template_with_answers(self.answers)
