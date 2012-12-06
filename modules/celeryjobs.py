from __future__ import absolute_import
from .base import Module

from celery.signals import task_sent

class CeleryJobs(Module):
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

