from __future__ import absolute_import
from .base import BaseModule

import time

class PageTimerModule(BaseModule):
    key = 'overall'

    def __init__(self):
        super(PageTimerModule, self).__init__()
        self._start_time = time.time()

    def get_metrics(self):
        render_time = int((time.time() - self._start_time) * 1000)
        return { 'time' : render_time }


def init():
    return PageTimerModule
