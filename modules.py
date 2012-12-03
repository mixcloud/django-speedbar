import time
import os

class PageTimer(object):
    key = 'overall'

    def __init__(self):
        self._start_time = time.time()

    def get_metrics(self):
        render_time = int((time.time() - self._start_time) * 1000)
        return { 'time' : render_time }


class HostInformation(object):
    key = 'host'

    def get_metrics(self):
        return {'name': os.uname()[1]}


class SqlQueries(object):
    key = 'sql'

    queries = []

    def __init__(self):
        self.__class__.queries = []

    def get_metrics(self):
        return {
            'count': len(self.queries),
            'time' : int(sum(q['time'] for q in self.queries) * 1000),
            }

    def get_details(self):
        return [{'sql': query['sql'], 'time': query['time'], 'count': query['count']} for query in self.queries ]

    @classmethod
    def record_query_details(cls, sql, time, backtrace, count=1):
        cls.queries.append({'sql': sql, 'time': time, 'backtrace': backtrace, 'count': count})
