from uuid import uuid4

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from thread import get_ident

class ThreadLocalSingleton(object):
    def __init__(self):
        if not hasattr(self.__class__, '_thread_lookup'):
            self.__class__._thread_lookup = dict()
        self.__class__._thread_lookup[get_ident()] = self

    def release(self):
        thread_id = get_ident()
        if self.__class_._thread_lookup[thread_id] == self:
            del self.__class_._thread_lookup[thread_id]

    @classmethod
    def instance(cls):
        thread_id = get_ident()
        if not hasattr(cls, '_thread_lookup') or thread_id not in cls._thread_lookup:
            cls()
        return cls._thread_lookup[thread_id]


class RequestTrace(ThreadLocalSingleton):
    """
    This is a container which keeps track of all module instances for a single request. For convenience they are made
    available as attributes based on their keyname
    """
    def __init__(self, modules=[]):
        super(RequestTrace, self).__init__()
        self.id = str(uuid4())
        self.modules = dict((m.key, m) for m in modules)
        self.__dict__.update(self.modules)

class BaseModule(object):
    pass
