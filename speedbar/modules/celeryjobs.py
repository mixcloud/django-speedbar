from __future__ import absolute_import

try:
    #from celery.app.task import Task as AppTask
    from celery.task import Task as TaskTask
    #from celery import Task as CeleryTask
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

    def apply_async(self, args=None, kwargs=None, *_args, **_kwargs):
        return (ENTRY_TYPE, 'Celery: %s' % (self.__name__,), {'type': self.__name__, 'args': args, 'kwargs': kwargs})
    # Celery has various legacy ways of getting to the task object, which python
    # interprets as different types, so we have to patch all of them.
    #trace_method(AppTask)(apply_async)
    #trace_method(CeleryTask)(apply_async)
    trace_method(TaskTask)(apply_async)

    return CeleryModule
