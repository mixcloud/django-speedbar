from __future__ import absolute_import

from django.template.base import Template
from django.template.response import TemplateResponse
from django.template.loader_tags import BlockNode

from .stacktracer import trace_method


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def init():
    @trace_method(Template)
    def __init__(self, *args, **kwargs):
        name = args[2] if len(args) >= 3 else '<Unknown Template>'
        return ('TEMPLATE_COMPILE', 'Compile template: ' + name, {})

    @trace_method(Template)
    def render(self, *args, **kwargs):
        return ('TEMPLATE_RENDER', 'Render template: ' + self.name, {})

    @trace_method(BlockNode)
    def render(self, *args, **kwargs):
        return ('BLOCK_RENDER', 'Render block: ' + self.name, {})

    @trace_method(TemplateResponse)
    def resolve_context(self, *args, **kwargs):
        return ('TEMPLATE_CONTEXT', 'Resolve context', {})
