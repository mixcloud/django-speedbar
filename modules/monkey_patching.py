from functools import wraps

def monkeypatch_method(cls, method_name=None):
    def decorator(func):
        method_to_patch = method_name or func.__name__
        original = getattr(cls, method_to_patch)
        # We can't use partial as it doesn't return a real function
        @wraps(original)
        def replacement(self, *args, **kwargs):
            return func(original, self, *args, **kwargs)
        setattr(cls, method_to_patch, replacement)
        return func
    return decorator


