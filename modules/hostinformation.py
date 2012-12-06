from __future__ import absolute_import
from .base import Module

import os

class HostInformation(Module):
    key = 'host'

    def get_metrics(self):
        return {'name': os.uname()[1]}

