from __future__ import absolute_import

from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper
from .base import BaseModule, RequestTrace
from .monkey_patching import monkeypatch_method


class SqlModule(BaseModule):
    key = 'sql'

    def __init__(self):
        super(SqlModule, self).__init__()
        self.queries = []

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('SQL')

    def get_details(self):
        sql_nodes = RequestTrace.instance().stacktracer.get_nodes('SQL')
        return [{'sql': node.label, 'time': int(node.duration*1000)} for node in sql_nodes]


class _DetailedTracingCursorWrapper(CursorWrapper):
    def execute(self, sql, params=()):
        request_trace = RequestTrace.instance()
        if request_trace:
            stack_entry = request_trace.stacktracer.push_stack('SQL', sql)
        try:
            return self.cursor.execute(sql, params)
        finally:
            if request_trace:
                request_trace.stacktracer.pop_stack()
                sql = self.db.ops.last_executed_query(self.cursor, sql, params)
                stack_entry.label = sql

    def executemany(self, sql, param_list):
        request_trace = RequestTrace.instance()
        if request_trace:
            request_trace.stacktracer.push_stack('SQL', sql)
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            if request_trace:
                request_trace.stacktracer.pop_stack()


# The linter thinks the methods we monkeypatch are not used
# pylint: disable=W0612
def init():
    @monkeypatch_method(BaseDatabaseWrapper)
    def cursor(original, self, *args, **kwargs):
        result = original(*args, **kwargs)
        return _DetailedTracingCursorWrapper(result, self)

    return SqlModule
