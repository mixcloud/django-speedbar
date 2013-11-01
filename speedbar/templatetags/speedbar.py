from __future__ import absolute_import

from django import template
register = template.Library()

@register.simple_tag
def metric(module, metric):
    """
    Display a placeholder that the middleware converts to a particular summary metric
    """
    return '<span data-module="%s" data-metric="%s"></span>' % (module, metric)
