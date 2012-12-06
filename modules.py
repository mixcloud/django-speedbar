from celery.signals import task_sent
import time
import os

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from thread import get_ident

class ThreadLocalSingleton(object):
    def __init__(self):
        if not hasattr(self.__class__, '_thread_lookup'):
            self.__class__._thread_lookup = dict()
        self.__class__._thread_lookup[get_ident()] = self

    def release(self):
        thread_id = get_ident()
        if self.__class_._thread_lookup[thread_id] == self:
            del self.__class_._thread_lookup[thread_id]

    @classmethod
    def instance(cls):
        thread_id = get_ident()
        if not hasattr(cls, '_thread_lookup') or thread_id not in cls._thread_lookup:
            cls()
        return cls._thread_lookup[thread_id]



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


class SqlQueries(ThreadLocalSingleton):
    key = 'sql'

    def __init__(self):
        super(SqlQueries, self).__init__()
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


class CeleryJobs(ThreadLocalSingleton):
    key = 'celery'

    def __init__(self):
        super(CeleryJobs, self).__init__()
        self.jobs = []

    def celery_task_sent(self, sender, **kwargs):
        self.jobs.append({
            'name': kwargs['task'],
            'args': kwargs['args'],
            'kwargs': kwargs['kwargs'],
            })

    def get_metrics(self):
        return {
            'count' : len(self.jobs),
            }

    def get_details(self):
        return self.jobs


@task_sent.connect(dispatch_uid='celery_task_sent_speedbar')
def celery_task_sent(sender, **kwargs):
    instance = CeleryJobs.instance()
    if instance:
        instance.celery_task_sent(sender, **kwargs)
