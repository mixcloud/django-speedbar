from __future__ import absolute_import
from .base import BaseModule

import os

class Module(BaseModule):
    key = 'host'

    def get_metrics(self):
        return {'name': os.uname()[1]}
