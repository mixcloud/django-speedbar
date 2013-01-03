from __future__ import absolute_import
from .base import BaseModule

import time

class StackEntry(object):
    def __init__(self, id_generator, entry_type, label, extra=None):
        self.id_generator = id_generator
        self.entry_id = id_generator()
        self.entry_type = entry_type
        self.label = label
        self.extra = extra
        self.start = int(time.time()*1000)
        self.children = []

    def mark_end(self):
        self.end = int(time.time()*1000)

    def add_child(self, entry_type, label, extra=None):
        child = StackEntry(self.id_generator, entry_type, label, extra)
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
    key = 'stacktracer'

    def __init__(self):
        super(StackTracer, self).__init__()
        self.root = None
        self.stack = []
        self.stack_id = 0
        
    def push_stack(self, entry_type, label, extra=None):
        if len(self.stack):
            entry = self.stack[-1].add_child(entry_type, label, extra)
        else:
            entry = self.root = StackEntry(self._get_next_id, entry_type, label, extra)
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
        accumulator = []
        self._get_nodes(node_type, self.root, accumulator)
        return accumulator

    def _get_nodes(self, node_type, node, accumulator):
        for child in node.children:
            if child.entry_type == node_type:
                accumulator.append(child)
            else:
                self._get_nodes(node_type, child, accumulator)

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
