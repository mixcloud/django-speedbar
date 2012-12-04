from mixcloud.speedbar import modules

from django.utils.encoding import smart_unicode, smart_str
from django.conf import settings

import json
import re

ACTIVE_MODULES = [modules.PageTimer, modules.HostInformation, modules.SqlQueries, modules.CeleryJobs]

HTML_TYPES = ('text/html', 'application/xhtml+xml')

METRIC_PLACEHOLDER_RE = re.compile('<span data-module="(?P<module>[^"]+)" data-metric="(?P<metric>[^"]+)"></span>')

class SpeedbarMiddleware(object):
    queries = []

    def process_request(self, request):
        request._speedbar_modules = dict((module.key, module()) for module in ACTIVE_MODULES)

    def process_response(self, request, response):
        def sanitize(string):
            return string.title().replace(' ','-')

        metrics = dict((key, module.get_metrics()) for key, module in request._speedbar_modules.items())
        for module, module_values in metrics.items():
            for key, value in module_values.items():
                response['X-Mixcloud-%s-%s' % (sanitize(module), sanitize(key))] = value

        if hasattr(request, 'user') and request.user.is_staff:
            if 'gzip' not in response.get('Content-Encoding', '') and response.get('Content-Type', '').split(';')[0] in HTML_TYPES:
                all_details = json.dumps(dict(
                    (key, module.get_details()) for key, module in request._speedbar_modules.items() if hasattr(module, 'get_details')
                ))

                content = smart_unicode(response.content)

                def replace_placeholder(match):
                    module = match.group('module')
                    metric = match.group('metric')
                    return unicode(metrics[module][metric])
                content = METRIC_PLACEHOLDER_RE.sub(replace_placeholder, content)

                if settings.DEBUG:
                    content = content.replace(
                        u'<script data-speedbar-details-placeholder></script>',
                        u'<script>var _speedbar_details = %s;</script>' % (all_details,))

                response.content = smart_str(content)

                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        return response

