from __future__ import absolute_import

from django.utils.html import format_html
from django import template
register = template.Library()

@register.simple_tag
def metric(module, metric):
    """
    Display a placeholder that the middleware converts to a particular summary metric
    """
    return format_html(u'<span data-module="{0}" data-metric="{1}"></span>', module, metric)