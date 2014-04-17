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
import re

from django.conf import settings
from django.core.signals import request_started, request_finished
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode, smart_str

from speedbar.signals import setup_request_tracing, store_request_trace
from speedbar.utils import init_modules
from speedbar.modules.base import RequestTrace


if getattr(settings, 'SPEEDBAR_ENABLE', True):
    # We hook everything up in the middleware file as loading the middleware is one of the first things performed
    # by the django WSGI implementation.
    init_modules()

    request_started.connect(setup_request_tracing, dispatch_uid='request_started_speedbar_setup_request_tracing')
    request_finished.connect(store_request_trace, dispatch_uid='request_started_speedbar_store_request_trace')


HTML_TYPES = ('text/html', 'application/xhtml+xml')
METRIC_PLACEHOLDER_RE = re.compile('<span data-module="(?P<module>[^"]+)" data-metric="(?P<metric>[^"]+)"></span>')


class SpeedbarMiddleware(object):
    def process_request(self, request):
        if getattr(settings, 'SPEEDBAR_ENABLE', True):
            request_trace = RequestTrace.instance()
            request_trace.stacktracer.root.label = '%s %s' % (request.method, request.path)
            request_trace.request = request

    def process_response(self, request, response):
        if not getattr(settings, 'SPEEDBAR_ENABLE', True):
            return response

        request_trace = RequestTrace.instance()
        # TODO: Do we also need to stash this on in case of exception?
        request_trace.response = response

        metrics = dict((key, module.get_metrics()) for key, module in request_trace.modules.items())

        if getattr(settings, 'SPEEDBAR_RESPONSE_HEADERS', False):
            self.add_response_headers(response, metrics)

        if hasattr(request, 'user') and request.user.is_staff:
            if getattr(settings, 'SPEEDBAR_TRACE', True):
                response['X-TraceUrl'] = reverse('speedbar_trace', args=[request_trace.id])
                request_trace.persist_log = True

            if 'gzip' not in response.get('Content-Encoding', '') and response.get('Content-Type', '').split(';')[0] in HTML_TYPES:

                # Force render of response (from lazy TemplateResponses) before speedbar is injected
                if hasattr(response, 'render'):
                    response.render()
                content = smart_unicode(response.content)

                content = self.replace_templatetag_placeholders(content, metrics)

                # Note: The URLs returned here do not exist at this point. The relevant data is added to the cache by a signal handler
                # once all page processing is finally done. This means it is possible summary values displayed and the detailed
                # break down won't quite correspond.
                if getattr(settings, 'SPEEDBAR_PANEL', True):
                    panel_url = reverse('speedbar_panel', args=[request_trace.id])
                    panel_placeholder_url = reverse('speedbar_details_for_this_request')
                    content = content.replace(panel_placeholder_url, panel_url)
                    request_trace.persist_details = True

                response.content = smart_str(content)
                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        return response

    def add_response_headers(self, response, metrics):
        """
        Adds all summary metrics to the response headers, so they can be stored in nginx logs if desired.
        """
        def sanitize(string):
            return string.title().replace(' ', '-')

        for module, module_values in metrics.items():
            for key, value in module_values.items():
                response['X-Speedbar-%s-%s' % (sanitize(module), sanitize(key))] = value

    def replace_templatetag_placeholders(self, content, metrics):
        """
        The templatetags defined in this module add placeholder values which we replace with true values here. They
        cannot just insert the values directly as not all processing may have happened by that point.
        """
        def replace_placeholder(match):
            module = match.group('module')
            metric = match.group('metric')
            return unicode(metrics[module][metric])
        return METRIC_PLACEHOLDER_RE.sub(replace_placeholder, content)
