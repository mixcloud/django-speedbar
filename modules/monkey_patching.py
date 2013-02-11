# This package has missing __init__.py files, so pylint can't see it
# pylint: disable=F0401
from peak.util.proxies import ObjectProxy

# The linter is dumb
# pylint: disable=E1001,E1002

class ExtendableObjectProxy(ObjectProxy):
    def __getattribute__(self, attr, oga=object.__getattribute__):
        if attr=='__subject__' or attr.startswith('__eop'):
            return oga(self, attr)
        subject = oga(self,'__subject__')
        return getattr(subject,attr)

    def __setattr__(self,attr,val, osa=object.__setattr__):
        if attr=='__subject__' or attr.startswith('__eop'):
            osa(self,attr,val)
        else:
            setattr(self.__subject__,attr,val)


class CallableProxy(ExtendableObjectProxy):
    __slots__ = ('__eop_wrapper__')
    def __init__(self, wrapped, wrapper):
        super(CallableProxy, self).__init__(wrapped)
        self.__eop_wrapper__ = wrapper

    def __call__(self, *args, **kwargs):
        return self.__eop_wrapper__(self.__subject__, *args, **kwargs)


class BoundMethodProxy(ExtendableObjectProxy):
    __slots__ = ('__eop_wrapper__', '__eop_instance__')
    def __init__(self, wrapped, instance, wrapper):
        super(BoundMethodProxy, self).__init__(wrapped)
        self.__eop_instance__ = instance
        self.__eop_wrapper__ = wrapper

    def __call__(self, *args, **kwargs):
        return self.__eop_wrapper__(self.__subject__, self.__eop_instance__, *args, **kwargs)


class UnboundMethodProxy(CallableProxy):
    __slots__ = ('__eop_wrapper__')

    def __get__(self, instance, owner):
        return BoundMethodProxy(self.__subject__.__get__(instance, owner), instance or owner, self.__eop_wrapper__)


def monkeypatch_method(cls, method_name=None):
    def decorator(func):
        method_to_patch = method_name or func.__name__
        original = cls.__dict__[method_to_patch]
        replacement = UnboundMethodProxy(original, func)
        type.__setattr__(cls, method_to_patch, replacement) # Avoid any overrides
        return func
    return decorator


