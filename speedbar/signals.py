from django.core.cache import cache
from django.dispatch import Signal
from speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX, loaded_modules
from speedbar.modules.base import RequestTrace

DETAILS_CACHE_TIME = 60 * 30  # 30 minutes


request_trace_complete = Signal(providing_args=['metrics', 'request', 'response'])


def setup_request_tracing(sender, **kwargs):
    RequestTrace(module() for module in loaded_modules)
    RequestTrace.instance().stacktracer.push_stack('HTTP', '')


def store_request_trace(sender, **kwargs):
    request_trace = RequestTrace.instance()
    if not request_trace:
        return

    request_trace.stacktracer.pop_stack()

    # Calculate values before doing any cache writes, so the cache writes don't affect the results
    if request_trace.persist_details:
        details_tuples = tuple(
            (key, module.get_details()) for key, module in request_trace.modules.items()
        )
        all_details = dict(details for details in details_tuples if details[1] is not None)
    if request_trace.persist_log:
        speedtracer_log = request_trace.stacktracer.speedtracer_log()
    metrics = dict((key, module.get_metrics()) for key, module in request_trace.modules.items())

    if request_trace.persist_details:
        cache.set(DETAILS_PREFIX + request_trace.id, all_details, DETAILS_CACHE_TIME)
    if request_trace.persist_log:
        cache.set(TRACE_PREFIX + request_trace.id, speedtracer_log, DETAILS_CACHE_TIME)

    request_trace_complete.send(
        sender,
        metrics=metrics,
        request=getattr(request_trace, 'request', None),
        response=getattr(request_trace, 'response', None)
    )
