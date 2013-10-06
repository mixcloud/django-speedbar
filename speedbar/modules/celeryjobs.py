from __future__ import absolute_import

try:
    from celery.task import Task as TaskTask
except ImportError:
    TaskTask = None

from .base import BaseModule, RequestTrace
from .stacktracer import trace_method

ENTRY_TYPE = 'CELERY'

class CeleryModule(BaseModule):
    key = 'celery'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics(ENTRY_TYPE)

    def get_details(self):
        nodes = RequestTrace.instance().stacktracer.get_nodes(ENTRY_TYPE)
        return [{'type': node.extra['type'], 'args': node.extra['args'], 'kwargs': node.extra['kwargs'], 'time': node.duration} for node in nodes]


def init():
    if TaskTask is None:
        return False

    @trace_method(TaskTask)
    def apply_async(self, args=None, kwargs=None, *_args, **_kwargs):
        return (ENTRY_TYPE, 'Celery: %s' % (self.__name__,), {'type': self.__name__, 'args': args, 'kwargs': kwargs})

    return CeleryModule
