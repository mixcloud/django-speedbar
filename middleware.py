from mixcloud.speedbar import modules
from mixcloud.speedbar.speedtracer import StackRecorder
from mixcloud.speedbar.utils import DETAILS_PREFIX, TRACE_PREFIX

from django.utils.encoding import smart_unicode, smart_str
from django.utils.html import escape, escapejs
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse

import json
import re
from uuid import uuid4

ACTIVE_MODULES = [modules.PageTimer, modules.HostInformation, modules.SqlQueries, modules.CeleryJobs, StackRecorder]
DETAILS_CACHE_TIME = 60 * 30 # 30 minutes

HTML_TYPES = ('text/html', 'application/xhtml+xml')

METRIC_PLACEHOLDER_RE = re.compile('<span data-module="(?P<module>[^"]+)" data-metric="(?P<metric>[^"]+)"></span>')

class SpeedbarMiddleware(object):
    queries = []

    def process_request(self, request):
        request._speedbar_modules = dict((module.key, module()) for module in ACTIVE_MODULES)
        StackRecorder.instance().push_stack('HTTP', 'GET ' + request.path)

    def process_response(self, request, response):
        def sanitize(string):
            return string.title().replace(' ','-')

        metrics = dict((key, module.get_metrics()) for key, module in request._speedbar_modules.items())
        for module, module_values in metrics.items():
            for key, value in module_values.items():
                response['X-Mixcloud-%s-%s' % (sanitize(module), sanitize(key))] = value

        if hasattr(request, 'user') and request.user.is_staff:
            if 'gzip' not in response.get('Content-Encoding', '') and response.get('Content-Type', '').split(';')[0] in HTML_TYPES:

                # Force render of response (from lazy TemplateResponses) before speedbar is injected
                if hasattr(response, 'render'):
                    response.render()
                content = smart_unicode(response.content)

                def replace_placeholder(match):
                    module = match.group('module')
                    metric = match.group('metric')
                    return unicode(metrics[module][metric])
                content = METRIC_PLACEHOLDER_RE.sub(replace_placeholder, content)

                if settings.DEBUG:
                    all_details = dict(
                        (key, module.get_details()) for key, module in request._speedbar_modules.items() if hasattr(module, 'get_details')
                    )
                    pageload_uuid = str(uuid4())
                    cache.set(DETAILS_PREFIX + pageload_uuid, all_details, DETAILS_CACHE_TIME)


                    StackRecorder.instance().pop_stack()
                    speedtracer_log = StackRecorder.instance().speedtracer_log(pageload_uuid)
                    cache.set(TRACE_PREFIX + pageload_uuid, speedtracer_log, DETAILS_CACHE_TIME)

                    panel_url = reverse('speedbar_panel', args=[pageload_uuid])

                    content = content.replace(
                        u'<script data-speedbar-panel-url-placeholder></script>',
                        u'<script>var _speedbar_panel_url = "%s";</script>' % (escapejs(panel_url),))
                    response['X-TraceUrl'] = reverse('speedbar_trace', args=[pageload_uuid])

                response.content = smart_str(content)

                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        return response

