from __future__ import absolute_import
from .base import Module

import time

class StackEntry(object):
    def __init__(self, entry_id, entry_type, label):
        self.entry_id = entry_id
        self.entry_type = entry_type
        self.label = label
        self.start = int(time.time()*1000)
        self.children = []

    def end(self):
        self.end = int(time.time()*1000)

    def add_child(self, child):
        self.children.append(child)

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


class StackTracer(Module):
    key = 'stackrecorder'

    def __init__(self):
        super(StackTracer, self).__init__()
        self.root = None
        self.stack = []
        self.stack_id = 0

    def push_stack(self, action_type, label):
        entry = StackEntry(self.stack_id, action_type, label)
        self.stack_id += 1
        if len(self.stack):
            self.stack[-1].add_child(entry)
        else:
            self.root = entry
        self.stack.append(entry)
        return entry

    def pop_stack(self):
        self.stack[-1].end()
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
