from __future__ import absolute_import

from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIHandler

from .base import RequestTrace
from .monkey_patching import monkeypatch_method
from .stacktracer import trace_function

import traceback


def patch_function_list(functions, action_type, format_string):
    for i, func in enumerate(functions):
        if hasattr(func, 'im_class'):
            middleware_name = func.im_class.__name__
        else:
            middleware_name = func.__name__
        info = (action_type, format_string % (middleware_name,), {})
        functions[i] = trace_function(func, info)


def wrap_middleware_with_tracers(request_handler):
    patch_function_list(request_handler._request_middleware, 'MIDDLEWARE_REQUEST', 'Middleware: %s (request)')
    patch_function_list(request_handler._view_middleware, 'MIDDLEWARE_VIEW', 'Middleware: %s (view)')
    patch_function_list(request_handler._template_response_middleware, 'MIDDLEWARE_TEMPLATE_RESPONSE', 'Middleware: %s (template response)')
    patch_function_list(request_handler._response_middleware, 'MIDDLEWARE_RESPONSE', 'Middleware: %s (response)')
    patch_function_list(request_handler._exception_middleware, 'MIDDLEWARE_EXCEPTION', 'Middleware: %s (exeption)')


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
middleware_patched = False
def intercept_middleware():
    @monkeypatch_method(WSGIHandler)
    def __call__(original, self, *args, **kwargs):
        # The middleware cache may have been built before we have a chance to monkey patch
        # it, so do so here
        global middleware_patched
        if not middleware_patched and self._request_middleware is not None:
            self.initLock.acquire()
            try:
                if not middleware_patched:
                    wrap_middleware_with_tracers(self)
                    middleware_patched = True
            finally:
                self.initLock.release()
        return original(*args, **kwargs)

    @monkeypatch_method(BaseHandler)
    def load_middleware(original, self, *args, **kwargs):
        global middleware_patched
        original(*args, **kwargs)
        wrap_middleware_with_tracers(self)
        middleware_patched = True


def intercept_resolver_and_view():
    # The only way we can really wrap the view method is by replacing the implementation
    # of RegexURLResolver.resolve. It would be nice if django had more configurability here, but it does not.
    # However, we only want to replace it when invoked directly from the request handling stack, so we
    # inspect the callstack in __new__ and return either a normal object, or an instance of our proxying
    # class.
    real_resolver_cls = urlresolvers.RegexURLResolver
    class ProxyRegexURLResolverMetaClass(urlresolvers.RegexURLResolver.__class__):
        def __instancecheck__(self, instance):
            # Some places in django do a type check against RegexURLResolver and behave differently based on the result, so we have to
            # make sure the replacement class we plug in accepts instances of both the default and replaced types.
            return isinstance(instance, real_resolver_cls) or super(ProxyRegexURLResolverMetaClass, self).__instancecheck__(instance)
    class ProxyRegexURLResolver(object):
        __metaclass__ = ProxyRegexURLResolverMetaClass
        def __new__(cls, *args, **kwargs):
            real_object = real_resolver_cls(*args, **kwargs)
            stack = traceback.extract_stack()
            if stack[-2][2] == 'get_response':
                obj = super(ProxyRegexURLResolver, cls).__new__(cls)
                obj.other = real_object
                return obj
            else:
                return real_object
        def __getattr__(self, attr):
            return getattr(self.other, attr)
        def resolve(self, path):
            request_trace = RequestTrace.instance()
            if request_trace:
                request_trace.stacktracer.push_stack('RESOLV', 'Resolving: ' + path)
            try:
                callbacks = self.other.resolve(path)
            finally:
                if request_trace:
                    request_trace.stacktracer.pop_stack()
            # Replace the callback function with a traced copy so we can time how long the view takes.
            callbacks.func = trace_function(callbacks.func, ('VIEW', 'View: ' + callbacks.view_name, {}))
            return callbacks
    urlresolvers.RegexURLResolver = ProxyRegexURLResolver


def init():
    intercept_middleware()
    intercept_resolver_and_view()
