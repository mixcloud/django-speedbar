from __future__ import absolute_import

from django import template
register = template.Library()

@register.simple_tag
def query_count():
    return '<span id="query-count"></span>'

@register.simple_tag
def query_time():
    return '<span id="query-time"></span>'

@register.simple_tag
def query_details_script():
    return '<script id="query_details_script"></script>'
