from django.db.backends.util import CursorWrapper
from django.db.utils import load_backend
from mixcloud.speedbar.modules.base import RequestTrace
from django.conf import settings

wrappedbackend = load_backend(settings.DATABASE_BACKEND_TO_TRACE)

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
        stack_entry = request_trace.stacktracer.push_stack('SQL', sql)
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            request_trace.stacktracer.pop_stack()


class DatabaseWrapper(wrappedbackend.DatabaseWrapper):
    def cursor(self, *args, **kwargs):
        cursor = wrappedbackend.DatabaseWrapper.cursor(self, *args, **kwargs)
        return _DetailedTracingCursorWrapper(cursor, self)

