from celery.signals import task_sent
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


class CeleryJobs(object):
    key = 'celery'

    jobs = []

    def __init__(self):
        self.__class__.jobs = []

    @classmethod
    def celery_task_sent(cls, sender, **kwargs):
        cls.jobs.append({
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
    CeleryJobs.celery_task_sent(sender, **kwargs)
