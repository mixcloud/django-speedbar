from django.utils.importlib import import_module
from django.conf import settings

DETAILS_PREFIX='speedbar:details:'
TRACE_PREFIX='speedbar:trace:'

SPEEDBAR_MODULES = [
    'speedbar.modules.stacktracer', # Most other modules depend on this one
    'speedbar.modules.pagetimer',
    'speedbar.modules.hostinformation',
    'speedbar.modules.sql',
    'speedbar.modules.celeryjobs',
    'speedbar.modules.requeststages',
    'speedbar.modules.templates',
    'speedbar.modules.redis',
    'speedbar.modules.memcache',
    'speedbar.modules.haystack',
    'speedbar.modules.cassandra',
]

# A module comprises of two parts, both of which are optional. It may have an init() function which is called once
# on server startup, and it may have a class called Module which is instantiated once per request.

loaded_modules = []

modules_initialised = False
def init_modules():
    """
    Run the init function for all modules which have one
    """
    global modules_initialised
    if modules_initialised:
        return
    modules_initialised = True

    for module_name in getattr(settings, 'SPEEDBAR_MODULES', SPEEDBAR_MODULES):
        python_module = import_module(module_name)
        speedbar_module = python_module.init()
        if speedbar_module:
            loaded_modules.append(speedbar_module)
