import wrapt


class BoundCallableWrapper(wrapt.ObjectProxy):
    def __init__(self, wrapped, instance, wrapper):
        super(BoundCallableWrapper, self).__init__(wrapped)
        self._self_wrapper = wrapper
        self._self_instance = instance

    def __call__(self, *args, **kwargs):
        return self._self_wrapper(self.__wrapped__, self._self_instance, *args, **kwargs)


class CallableWrapper(wrapt.ObjectProxy):
    def __init__(self, wrapped, wrapper):
        super(CallableWrapper, self).__init__(wrapped)
        self._self_wrapper = wrapper

    def __call__(self, *args, **kwargs):
        return self._self_wrapper(self.__wrapped__, *args, **kwargs)

    def __get__(self, instance, owner):
        function = self.__wrapped__.__get__(instance, owner)
        return BoundCallableWrapper(function, instance or owner, self._self_wrapper)


def monkeypatch_method(cls, method_name=None):
    def decorator(func):
        method_to_patch = method_name or func.__name__
        original = cls.__dict__[method_to_patch]
        replacement = CallableWrapper(original, func)
        type.__setattr__(cls, method_to_patch, replacement)  # Avoid any overrides
        return func
    return decorator

