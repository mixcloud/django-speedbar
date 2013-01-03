from mixcloud.speedbar.modules.stacktracer import StackTracer
from mixcloud.speedbar.modules.base import RequestTrace

from django.utils.encoding import smart_unicode, smart_str
from django.utils.html import escapejs
from django.conf import settings
from django.core.urlresolvers import reverse

import re

HTML_TYPES = ('text/html', 'application/xhtml+xml')

METRIC_PLACEHOLDER_RE = re.compile('<span data-module="(?P<module>[^"]+)" data-metric="(?P<metric>[^"]+)"></span>')

class SpeedbarMiddleware(object):
    def process_request(self, request):
        StackTracer.instance().root.label = '%s %s' % (request.method, request.path)

    def process_response(self, request, response):
        request_trace = RequestTrace.instance()

        def sanitize(string):
            return string.title().replace(' ','-')

        metrics = dict((key, module.get_metrics()) for key, module in request_trace.modules.items())
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
                    panel_url = reverse('speedbar_panel', args=[request_trace.id])
                    content = content.replace(
                        u'<script data-speedbar-panel-url-placeholder></script>',
                        u'<script>var _speedbar_panel_url = "%s";</script>' % (escapejs(panel_url),))
                    response['X-TraceUrl'] = reverse('speedbar_trace', args=[request_trace.id])

                response.content = smart_str(content)

                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        return response

