from __future__ import absolute_import
from .base import BaseModule, RequestTrace
from .monkey_patching import monkeypatch_method
from functools import wraps

import memcache

class Module(BaseModule):
    key = 'memcache'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('MEMCACHE')

    def get_details(self):
        memcache_nodes = RequestTrace.instance().stacktracer.get_nodes('MEMCACHE')
        return [{'operation': node.extra['operation'], 'key': node.extra['key'], 'time': node.duration} for node in memcache_nodes]


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def wrap_operation(operation):
    @monkeypatch_method(memcache.Client, operation)
    def wrapper(original, self, *args, **kwargs):
        stack_tracer = RequestTrace.instance().stacktracer
        try:
            stack_tracer.push_stack('MEMCACHE', 'Memcache: %s (%s)' % (operation, args[0]), extra={'operation': operation, 'key': args[0]})
            return original(self, *args, **kwargs)
        finally:
            stack_tracer.pop_stack()


def wrap_multi_operation(operation):
    @monkeypatch_method(memcache.Client, operation)
    def wrapper(original, self, *args, **kwargs):
        stack_tracer = RequestTrace.instance().stacktracer
        try:
            stack_tracer.push_stack('MEMCACHE', 'Memcache: %s' % (operation,), extra={'operation': operation, 'key': ''})
            return original(self, *args, **kwargs)
        finally:
            stack_tracer.pop_stack()


def init():
    operations = [
        'add', 'append', 'cas', 'decr', 'delete',
        'get', 'gets', 'incr', 'prepend', 'replace', 'set',
    ]
    for operation in operations:
        wrap_operation(operation)

    multi_operations = [
        'get_multi',
        'set_multi',
        'delete_multi',
    ]
    for operation in multi_operations:
        wrap_multi_operation(operation)
