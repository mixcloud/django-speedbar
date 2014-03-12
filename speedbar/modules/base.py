from uuid import uuid4
import threading


class ThreadLocalSingleton(object):
    def __init__(self):
        if not hasattr(self.__class__, '_thread_lookup'):
            self.__class__._thread_lookup = threading.local()
        self.__class__._thread_lookup.instance = self

    def release(self):
        if getattr(self.__class_._thread_lookup, 'instance', None) is self:
            self.__class_._thread_lookup.instance = None

    @classmethod
    def instance(cls):
        if hasattr(cls, '_thread_lookup'):
            return getattr(cls._thread_lookup, 'instance', None)


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
