from __future__ import absolute_import
from .base import BaseModule, RequestTrace
from .stacktracer import trace_method

try:
    import memcache
except ImportError:
    memcache = None

MEMCACHE_OPERATIONS = [ 'add', 'append', 'cas', 'decr', 'delete', 'get', 'gets', 'incr', 'prepend', 'replace', 'set', ]
MEMCACHE_MULTI_OPERATIONS = [ 'get_multi', 'set_multi', 'delete_multi', ]


class MemcacheModule(BaseModule):
    key = 'memcache'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('MEMCACHE')

    def get_details(self):
        memcache_nodes = RequestTrace.instance().stacktracer.get_nodes('MEMCACHE')
        return [{'operation': node.extra['operation'], 'key': node.extra['key'], 'time': node.duration} for node in memcache_nodes]


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def intercept_memcache_operation(operation):
    @trace_method(memcache.Client, operation)
    def info(self, *args, **kwargs):
        return ('MEMCACHE', 'Memcache: %s (%s)' % (operation, args[0]), {'operation': operation, 'key': args[0]})


def intercept_memcache_multi_operation(operation):
    @trace_method(memcache.Client, operation)
    def info(self, *args, **kwargs):
        return ('MEMCACHE', 'Memcache: %s' % (operation,), {'operation': operation, 'key': ''})


def init():
    if memcache is None:
        return False

    for operation in MEMCACHE_OPERATIONS:
        intercept_memcache_operation(operation)

    for operation in MEMCACHE_MULTI_OPERATIONS:
        intercept_memcache_multi_operation(operation)

    return MemcacheModule
