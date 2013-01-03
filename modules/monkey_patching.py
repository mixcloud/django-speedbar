from functools import wraps

def monkeypatch_method(cls):
    def decorator(func):
        original = getattr(cls, func.__name__)
        # We can't use partial as it doesn't return a real function
        @wraps(original)
        def replacement(self, *args, **kwargs):
            return func(original, self, *args, **kwargs)
        setattr(cls, func.__name__, replacement)
        return func
    return decorator


