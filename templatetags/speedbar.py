from __future__ import absolute_import

from django import template
register = template.Library()

@register.simple_tag
def metric(module, metric):
    """
    Display a placeholder that the middleware converts to a particular summary metric
    """
    return '<span data-module="%s" data-metric="%s"></span>' % (module, metric)

@register.simple_tag
def speedbar_script():
    """
    Display a placeholder that the middleware replaces with a URL setter.
    """
    return '<script data-speedbar-panel-url-placeholder></script>'
