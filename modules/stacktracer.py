from __future__ import absolute_import
from .base import BaseModule
from collections import defaultdict

import time

class StackEntry(object):
    def __init__(self, id_generator, entry_map, entry_type, label, extra=None):
        self.id_generator = id_generator
        self.entry_map = entry_map
        self.entry_id = id_generator()
        self.entry_type = entry_type
        self.label = label
        self.extra = extra
        self.start = int(time.time()*1000)
        self.children = []
        self.entry_map[entry_type].append(self)

    def mark_end(self):
        self.end = int(time.time()*1000)

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
                'start': self.start,
                'end': self.end,
                'duration': self.duration,
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
            'time': sum(x.duration for x in nodes),
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


Module = StackTracer
