from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase, RequestFactory


class TemplateTagsTest(TestCase):
    def test_templatetags_loaded(self):
        request = RequestFactory().get('/')
        request.user = User.objects.create(username='test')
        Template('{% load speedbar %}{% metric "overall" "time" %}').render(Context({'request': request}))

