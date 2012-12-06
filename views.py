from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from mixcloud.utils.decorators import staff_only
from mixcloud.speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX


import json
import time

@staff_only
def panel(request, trace_id):
    details = cache.get(DETAILS_PREFIX + trace_id)
    if details and settings.DEBUG:
        details_json = json.dumps(details, skipkeys=True, default=repr, indent=2)
        return HttpResponse(content=details_json)
    else:
        return HttpResponse(status=404)

@staff_only
def trace(request, trace_id):
    trace = cache.get(TRACE_PREFIX + trace_id)
    if trace and settings.DEBUG:
        trace_json = json.dumps(trace, indent=2)
        return HttpResponse(content=trace_json, mimetype="application/json")
    else:
        return HttpResponse(status=404)
