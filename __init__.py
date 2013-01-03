from django.core.signals import request_started, request_finished
from mixcloud.speedbar.signals import setup_request_tracing, store_request_trace
from mixcloud.speedbar.utils import init_modules

init_modules()

# Initial dummy request to catch early events
setup_request_tracing(None)

request_started.connect(setup_request_tracing, dispatch_uid='request_started_speedbar_setup_request_tracing')
request_finished.connect(store_request_trace, dispatch_uid='request_started_speedbar_store_request_trace')


