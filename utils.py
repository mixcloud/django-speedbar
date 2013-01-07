from django.utils.importlib import import_module
from django.conf import settings

DETAILS_PREFIX='speedbar:details:'
TRACE_PREFIX='speedbar:trace:'

SPEEDBAR_MODULES = [
    'mixcloud.speedbar.modules.pagetimer',
    'mixcloud.speedbar.modules.hostinformation',
    'mixcloud.speedbar.modules.sql',
    'mixcloud.speedbar.modules.celeryjobs',
    'mixcloud.speedbar.modules.stacktracer',
    'mixcloud.speedbar.modules.requeststages',
    'mixcloud.speedbar.modules.redis',
    'mixcloud.speedbar.modules.memcache',
]

# A module comprises of two parts, both of which are optional. It may have an init() function which is called once
# on server startup, and it may have a class called Module which is instantiated once per request.

loaded_modules = [import_module(m) for m in getattr(settings, 'SPEEDBAR_MODULES', SPEEDBAR_MODULES)]

modules_initialised = False
def init_modules():
    """
    Run the init function for all modules which have one
    """
    global modules_initialised
    if modules_initialised:
        return
    modules_initialised = True

    for module in loaded_modules:
        if hasattr(module, 'init'):
            module.init()
