from __future__ import absolute_import
from .base import BaseModule, RequestTrace

from celery.signals import task_sent

class Module(BaseModule):
    key = 'celery'

    def __init__(self):
        super(Module, self).__init__()
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


def celery_task_sent(sender, **kwargs):
    instance = RequestTrace.instance()
    if intance:
        instance.celery.celery_task_sent(sender, **kwargs)


def init():
    task_sent.connect(celery_task_sent, dispatch_uid='celery_task_sent_speedbar')
