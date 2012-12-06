from django.http import HttpResponse
from django.core.cache import cache

import json

def panel(request, trace_id):
    details = cache.get(trace_id)
    if details:
        details_json = json.dumps(details, skipkeys=True, default=repr, indent=2)
        return HttpResponse(content=details_json)
    else:
        return HttpResponse(status=404)
