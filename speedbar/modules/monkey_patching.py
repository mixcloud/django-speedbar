# This package has missing __init__.py files, so pylint can't see it
# pylint: disable=F0401
from peak.util.proxies import ObjectWrapper


# The linter is dumb
# pylint: disable=E1001,E1002
class CallableProxy(ObjectWrapper):
    __slots__ = ('_eop_wrapper_')

    def __init__(self, wrapped, wrapper):
        super(CallableProxy, self).__init__(wrapped)
        self._eop_wrapper_ = wrapper

    def __call__(self, *args, **kwargs):
        return self._eop_wrapper_(self.__subject__, *args, **kwargs)


class BoundMethodProxy(ObjectWrapper):
    __slots__ = ('_eop_wrapper_', '_eop_instance_')

    def __init__(self, wrapped, instance, wrapper):
        super(BoundMethodProxy, self).__init__(wrapped)
        self._eop_instance_ = instance
        self._eop_wrapper_ = wrapper

    def __call__(self, *args, **kwargs):
        return self._eop_wrapper_(self.__subject__, self._eop_instance_, *args, **kwargs)


class UnboundMethodProxy(CallableProxy):
    __slots__ = ('_eop_wrapper_')

    def __get__(self, instance, owner):
        return BoundMethodProxy(self.__subject__.__get__(instance, owner), instance or owner, self._eop_wrapper_)

    def __getattribute__(self, attr, oga=object.__getattribute__):
        """We need to return our own version of __get__ or we may end up never being called if
        the member we are wrapping is wrapped again by someone else"""
        if attr == '__get__':
            return oga(self, attr)
        return super(UnboundMethodProxy, self).__getattribute__(attr)


def monkeypatch_method(cls, method_name=None):
    def decorator(func):
        method_to_patch = method_name or func.__name__
        original = cls.__dict__[method_to_patch]
        replacement = UnboundMethodProxy(original, func)
        type.__setattr__(cls, method_to_patch, replacement)  # Avoid any overrides
        return func
    return decorator
