from __future__ import absolute_import
from .base import BaseModule


class Module(BaseModule):
    key = 'sql'

    def __init__(self):
        super(Module, self).__init__()
        self.queries = []

    def get_metrics(self):
        return {
            'count': len(self.queries),
            'time' : int(sum(q['time'] for q in self.queries) * 1000),
            }

    def get_details(self):
        return [{'sql': query['sql'], 'time': query['time'], 'count': query['count']} for query in self.queries ]

    def record_query_details(self, sql, time, backtrace, count=1):
        self.queries.append({'sql': sql, 'time': time, 'backtrace': backtrace, 'count': count})


