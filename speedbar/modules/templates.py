from __future__ import absolute_import

from django.template import defaulttags
from django.template.base import add_to_builtins, Library, Template
from django.template.response import TemplateResponse
from django.template.loader_tags import BlockNode

from .stacktracer import trace_method, trace_function

register = Library()


class DecoratingParserProxy(object):
    """
    Mocks out the django template parser, passing templatetags through but
    first wrapping them to include performance data
    """
    def __init__(self, parser):
        self.parser = parser

    def add_library(self, library):
        wrapped_library = Library()
        wrapped_library.filters = library.filters
        for name, tag_compiler in library.tags.items():
            wrapped_library.tags[name] = self.wrap_compile_function(name, tag_compiler)
        self.parser.add_library(wrapped_library)

    def wrap_compile_function(self, name, tag_compiler):
        def compile(*args, **kwargs):
            node = tag_compiler(*args, **kwargs)
            node.render = trace_function(node.render, ('TEMPLATE_TAG', 'Render tag: ' + name, {}))
            return node
        return compile


@register.tag
def load(parser, token):
    decorating_parser = DecoratingParserProxy(parser)
    return defaulttags.load(decorating_parser, token)


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def init():
    # Our eventual aim is to patch the render() method on the Node objects
    # corresponding to custom template tags. However we have to jump through
    # a number of hoops in order to get access to the object.
    #
    # 1. Add ourselves to the set of built in template tags
    #    This allows us to replace the 'load' template tag which controls
    #    the loading of custom template tags
    # 2. Delegate to default load with replaced parser
    #    We provide our own parser class so we can catch and intercept
    #    calls to add_library.
    # 3. add_library receives a library of template tags
    #    It iterates through each template tag, wrapping its compile function
    # 4. compile is called as part of compiling the template
    #    Our wrapper is called instead of the original templatetag compile
    #    function. We delegate to the original function, but then modify
    #    the resulting object by wrapping its render() function. This
    #    render() function is what ends up being timed and appearing in the
    #    tree.
    add_to_builtins('speedbar.modules.templates')

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
