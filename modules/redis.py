from __future__ import absolute_import
from .base import BaseModule, RequestTrace
from .stacktracer import trace_method

from redis import Redis

class Module(BaseModule):
    key = 'redis'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('REDIS')

    def get_details(self):
        redis_nodes = RequestTrace.instance().stacktracer.get_nodes('REDIS')
        return [{'operation': node.extra['operation'], 'key': node.extra['key'], 'time': node.duration} for node in redis_nodes]

def init():
    # The linter thinks the methods we monkeypatch are not used
    # pylint: disable=W0612

    @trace_method(Redis)
    def execute_command(self, *args, **kwargs):
        if len(args) >= 2:
            action = 'Redis: %s (%s)' % args[:2]
            key = args[1]
        else:
            action = 'Redis: %s' % args[:1]
            key = ''
        return ('REDIS', action, {'operation': args[0], 'key': key})
