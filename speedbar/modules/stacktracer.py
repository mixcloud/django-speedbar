from __future__ import absolute_import

from collections import defaultdict

from .base import BaseModule, RequestTrace
from .monkey_patching import monkeypatch_method, CallableProxy

import time

class StackEntry(object):
    def __init__(self, id_generator, entry_map, entry_type, label, extra=None):
        self.id_generator = id_generator
        self.entry_map = entry_map
        self.entry_id = id_generator()
        self.entry_type = entry_type
        self.label = label
        self.extra = extra
        self.start = time.time()
        self.children = []
        self.entry_map[entry_type].append(self)

    def mark_end(self):
        self.end = time.time()

    def add_child(self, entry_type, label, extra=None):
        child = StackEntry(self.id_generator, self.entry_map, entry_type, label, extra)
        self.children.append(child)
        return child

    @property
    def duration(self):
        if self.end:
            return self.end - self.start
        return 0

    def to_dict(self):
        return {
            'id': str(self.entry_id),
            'range': {
                'start': round(self.start * 1000, 1),
                'end': round(self.end * 1000, 1),
                'duration': round(self.duration * 1000, 1),
            },
            'operation' : {
                'type': self.entry_type,
                'label': self.label,
            },
            'children': [child.to_dict() for child in self.children],
        }


class StackTracer(BaseModule):
    """
    This class maintains a call tree, with a pointer to the current stack
    entry so that new frames can be added at any time without further context
    by the various monkey patching functions.

    It can provide all entries corresponding to operations of particular types, and
    also build a valid HAR file out of the entire call tree for use with SpeedTracer
    """
    key = 'stacktracer'

    def __init__(self):
        super(StackTracer, self).__init__()
        self.root = None
        self.stack = []
        self.stack_id = 0
        self.entry_map = defaultdict(list)

    def push_stack(self, entry_type, label, extra=None):
        if len(self.stack):
            entry = self.stack[-1].add_child(entry_type, label, extra)
        else:
            entry = self.root = StackEntry(self._get_next_id, self.entry_map, entry_type, label, extra)
        self.stack.append(entry)
        return entry

    def pop_stack(self):
        self.stack[-1].mark_end()
        self.stack.pop()

    def get_metrics(self):
        return {}

    def get_node_metrics(self, node_type):
        nodes = self.get_nodes(node_type)
        return {
            'time': int(sum(x.duration for x in nodes)*1000),
            'count': len(nodes),
        }

    def get_nodes(self, node_type):
        return self.entry_map[node_type]

    def speedtracer_log(self):
        entries_as_dict = self.root.to_dict()
        return {
            'trace': {
                'id': str(self.stack_id),
                'application': 'Speedbar',
                'date': time.time(),
                'range': entries_as_dict['range'],
                'frameStack': entries_as_dict,
            }
        }

    def _get_next_id(self):
        self.stack_id += 1
        return self.stack_id


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def trace_method(cls, method_name=None):
    def decorator(info_func):
        method_to_patch = method_name or info_func.__name__
        @monkeypatch_method(cls, method_to_patch)
        def tracing_method(original, self, *args, **kwargs):
            request_trace = RequestTrace.instance()
            if request_trace:
                entry_type, label, extra = info_func(self, *args, **kwargs)
                request_trace.stacktracer.push_stack(entry_type, label, extra=extra)
            try:
                return original(*args, **kwargs)
            finally:
                if request_trace:
                    request_trace.stacktracer.pop_stack()
        return tracing_method
    return decorator


def trace_function(func, info):
    try:
        def tracing_function(original, *args, **kwargs):
            request_trace = RequestTrace.instance()
            if request_trace:
                if callable(info):
                    entry_type, label, extra = info(*args, **kwargs)
                else:
                    entry_type, label, extra = info
                request_trace.stacktracer.push_stack(entry_type, label, extra)
            try:
                return original(*args, **kwargs)
            finally:
                if request_trace:
                    request_trace.stacktracer.pop_stack()
        return CallableProxy(func, tracing_function)
    except Exception:
        # If we can't wrap for any reason, just return the original
        return func


def init():
    return StackTracer
