from __future__ import absolute_import
from .base import BaseModule

import time

class StackEntry(object):
    def __init__(self, id_generator, entry_type, label):
        self.id_generator = id_generator
        self.entry_id = id_generator()
        self.entry_type = entry_type
        self.label = label
        self.start = int(time.time()*1000)
        self.children = []

    def mark_end(self):
        self.end = int(time.time()*1000)

    def add_child(self, entry_type, label):
        child = StackEntry(self.id_generator, entry_type, label)
        self.children.append(child)
        return child

    def to_dict(self):
        return {
            'id': str(self.entry_id),
            'range': {
                'start': self.start,
                'end': self.end,
                'duration': self.end - self.start,
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
        
    def push_stack(self, entry_type, label):
        if len(self.stack):
            entry = self.stack[-1].add_child(entry_type, label)
        else:
            entry = self.root = StackEntry(self._get_next_id, entry_type, label)
        self.stack.append(entry)
        return entry

    def pop_stack(self):
        self.stack[-1].mark_end()
        self.stack.pop()

    def get_metrics(self):
        return {}

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
