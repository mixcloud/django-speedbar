from django.http import HttpResponse
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX

import json

@staff_member_required
def panel(request, trace_id):
    details = cache.get(DETAILS_PREFIX + trace_id)
    if details:
        details_json = json.dumps(details, skipkeys=True, default=repr, indent=2) # Cannot use decorator as need default=repr
        return HttpResponse(content=details_json, mimetype='text/javascript; charset=utf-8')
    return HttpResponse(status=404)

@staff_member_required
def trace(request, trace_id):
    trace = cache.get(TRACE_PREFIX + trace_id)
    if trace:
        return HttpResponse(json.dumps(trace))
    return HttpResponse(status=404)


def noop():
    pass
