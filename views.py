from django.http import HttpResponse
from django.core.cache import cache
from mixcloud.utils.decorators import staff_only
from mixcloud.speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX
from gargoyle.decorators import switch_is_active

import json

@staff_only
@switch_is_active('speedbar:panel')
def panel(request, trace_id):
    details = cache.get(DETAILS_PREFIX + trace_id)
    if details:
        details_json = json.dumps(details, skipkeys=True, default=repr, indent=2)
        return HttpResponse(content=details_json)
    return HttpResponse(status=404)

@staff_only
@switch_is_active('speedbar:trace')
def trace(request, trace_id):
    trace = cache.get(TRACE_PREFIX + trace_id)
    if trace:
        trace_json = json.dumps(trace, indent=2)
        return HttpResponse(content=trace_json, mimetype="application/json")
    return HttpResponse(status=404)
