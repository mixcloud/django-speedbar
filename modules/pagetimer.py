from __future__ import absolute_import
from .base import Module

import time

class PageTimer(Module):
    key = 'overall'

    def __init__(self):
        self._start_time = time.time()

    def get_metrics(self):
        render_time = int((time.time() - self._start_time) * 1000)
        return { 'time' : render_time }
