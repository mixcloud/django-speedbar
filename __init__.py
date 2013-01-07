"""
Speedbar module

This provides performance metrics, details of operations performed, and Chrome SpeedTracer integration
for page loads.

Information is provided by a set of modules, which are responsible for recording and reporting data.
The collected data is then collected and made available via template tags, headers, and a HAR file.

On startup each module is given a chance to initialize itself, typically this consists of monkey
patching a set of built in django functionality. A per request module object is created in response
to the start of each request. Over the course of the request modules record data, using thread local
storage to associate correctly with the right request. A middleware then writes out summary data,
and the headers required to fetch more detailed information from the server. Finally the request_finished
signal handler stores detailed information to memcache which can then be retrieved.

"""
from django.core.signals import request_started, request_finished
from django.conf import settings
from mixcloud.speedbar.signals import setup_request_tracing, store_request_trace
from mixcloud.speedbar.utils import init_modules

if getattr(settings, 'SPEEDBAR_ENABLE', True):
    init_modules()

    # Initial dummy request to catch early events
    setup_request_tracing(None)

    request_started.connect(setup_request_tracing, dispatch_uid='request_started_speedbar_setup_request_tracing')
    request_finished.connect(store_request_trace, dispatch_uid='request_started_speedbar_store_request_trace')
