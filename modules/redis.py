from __future__ import absolute_import
from .base import BaseModule, RequestTrace
from .monkey_patching import monkeypatch_method

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

    @monkeypatch_method(Redis)
    def execute_command(original, self, *args, **kwargs):
        if len(args) >= 2:
            action = 'Redis: %s (%s)' % args[:2]
            key = args[1]
        else:
            action = 'Redis: %s' % args[:1]
            key = ''

        stack_tracer = RequestTrace.instance().stacktracer
        stack_tracer.push_stack('REDIS', action, extra={'operation': args[0], 'key': key})
        try:
            return original(*args, **kwargs)
        finally:
            stack_tracer.pop_stack()
