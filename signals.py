from mixcloud.speedbar import modules
from django.core.cache import cache
from mixcloud.speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX

ACTIVE_MODULES = [modules.PageTimer, modules.HostInformation, modules.SqlQueries, modules.CeleryJobs, modules.StackTracer]
DETAILS_CACHE_TIME = 60 * 30 # 30 minutes


def setup_request_tracing(sender, **kwargs):
    modules.RequestTrace(module() for module in ACTIVE_MODULES)
    modules.StackTracer.instance().push_stack('HTTP', '')


def store_request_trace(sender, **kwargs):
    modules.StackTracer.instance().pop_stack()
    request_trace = modules.RequestTrace.instance()

    all_details = dict(
        (key, module.get_details()) for key, module in request_trace.modules.items() if hasattr(module, 'get_details')
    )
    cache.set(DETAILS_PREFIX + request_trace.id, all_details, DETAILS_CACHE_TIME)

    speedtracer_log = modules.StackTracer.instance().speedtracer_log()
    cache.set(TRACE_PREFIX + request_trace.id, speedtracer_log, DETAILS_CACHE_TIME)
