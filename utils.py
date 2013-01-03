from django.utils.importlib import import_module
from django.conf import settings

DETAILS_PREFIX='speedbar:details:'
TRACE_PREFIX='speedbar:trace:'

SPEEDBAR_MODULES = [
    'mixcloud.speedbar.modules.pagetimer',
    'mixcloud.speedbar.modules.hostinformation',
    'mixcloud.speedbar.modules.sqlqueries',
    'mixcloud.speedbar.modules.celeryjobs',
    'mixcloud.speedbar.modules.stacktracer',
    'mixcloud.speedbar.modules.requeststages',
]

loaded_modules = [import_module(m) for m in getattr(settings, 'SPEEDBAR_MODULES', SPEEDBAR_MODULES)]

def init_modules():
    for module in loaded_modules:
        if hasattr(module, 'init'):
            module.init()
