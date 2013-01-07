from __future__ import absolute_import

from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper
from .base import BaseModule, RequestTrace
from .monkey_patching import monkeypatch_method


class Module(BaseModule):
    key = 'sql'

    def __init__(self):
        super(Module, self).__init__()
        self.queries = []

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('SQL')

    def get_details(self):
        sql_nodes = RequestTrace.instance().stacktracer.get_nodes('SQL')
        return [{'sql': node.label, 'time': node.duration} for node in sql_nodes]


class _DetailedTracingCursorWrapper(CursorWrapper):
    def execute(self, sql, params=()):
        self.set_dirty()
        request_trace = RequestTrace.instance()
        stack_entry = request_trace.stacktracer.push_stack('SQL', sql)
        try:
            return self.cursor.execute(sql, params)
        finally:
            request_trace.stacktracer.pop_stack()
            sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            stack_entry.label = sql

    def executemany(self, sql, param_list):
        self.set_dirty()
        request_trace = RequestTrace.instance()
        request_trace.stacktracer.push_stack('SQL', sql)
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            request_trace.stacktracer.pop_stack()


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def init():
    @monkeypatch_method(BaseDatabaseWrapper)
    def cursor(original, self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        return _DetailedTracingCursorWrapper(result, self)
