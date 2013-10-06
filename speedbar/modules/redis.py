from __future__ import absolute_import
from .base import BaseModule, RequestTrace
from .stacktracer import trace_method

try:
    from redis import StrictRedis
except ImportError:
    StrictRedis = None

class RedisModule(BaseModule):
    key = 'redis'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('REDIS')

    def get_details(self):
        redis_nodes = RequestTrace.instance().stacktracer.get_nodes('REDIS')
        return [{'operation': node.extra['operation'], 'key': node.extra['key'], 'time': node.duration} for node in redis_nodes]

def init():
    if StrictRedis is None:
        return False

    # The linter thinks the methods we monkeypatch are not used
    # pylint: disable=W0612
    @trace_method(StrictRedis)
    def execute_command(self, *args, **kwargs):
        if len(args) >= 2:
            action = 'Redis: %s (%s)' % args[:2]
            key = args[1]
        else:
            action = 'Redis: %s' % args[:1]
            key = ''
        return ('REDIS', action, {'operation': args[0], 'key': key})

    return RedisModule
