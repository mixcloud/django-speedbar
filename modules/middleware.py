from __future__ import absolute_import

from .stacktracer import StackTracer

from functools import wraps


def trace(function, action_type, label):
    @wraps(function)
    def wrapper(*args, **kwargs):
        stack_tracer = StackTracer.instance()
        stack_tracer.push_stack(action_type, label)
        try:
            return function(*args, **kwargs)
        finally:
            stack_tracer.pop_stack()
            pass
    return wrapper

def patch_function_list(functions, action_type, format_string):
    for i, func in enumerate(functions):
        functions[i] = trace(func, action_type, format_string % (func.im_class.__name__),)

def wrap_middleware_with_tracers(request_handler):
    patch_function_list(request_handler._request_middleware, 'MIDDLEWARE_REQUEST', 'Middleware: %s (request)')
    patch_function_list(request_handler._view_middleware, 'MIDDLEWARE_VIEW', 'Middleware: %s (view)')
    patch_function_list(request_handler._template_response_middleware, 'MIDDLEWARE_TEMPLATE_RESPONSE', 'Middleware: %s (template response)')
    patch_function_list(request_handler._response_middleware, 'MIDDLEWARE_RESPONSE', 'Middleware: %s (response)')
    patch_function_list(request_handler._exception_middleware, 'MIDDLEWARE_EXCEPTION', 'Middleware: %s (exeption)')

def monkey_patch():
    from django.core.handlers.base import BaseHandler
    load_middleware = BaseHandler.load_middleware
    def replacement_load_middleware(self, *args, **kwargs):
        load_middleware(self, *args, **kwargs)
        wrap_middleware_with_tracers(self)
    BaseHandler.load_middleware = replacement_load_middleware
