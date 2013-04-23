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
        if not hasattr(cls, '_thread_lookup'):
            cls._thread_lookup = dict()
        return cls._thread_lookup.get(get_ident(), None)


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
        self.persist_details = False
        self.persist_log = False

class BaseModule(object):
    def get_metrics(self):
        """
        Get a dictionary of summary metrics for the module
        """
        return dict()

    def get_details(self):
        """
        Get a detailed breakdown of all information collected by the module if available
        """
        return None
