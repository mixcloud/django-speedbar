from django.utils.encoding import smart_unicode
import json

HTML_TYPES = ('text/html', 'application/xhtml+xml')

class SpeedbarMiddleware(object):
    queries = []

    def process_request(self, request):
        SpeedbarMiddleware.queries = []

    def process_response(self, request, response):
        query_count = str(len(SpeedbarMiddleware.queries))
        query_time = int(sum(q['time'] for q in SpeedbarMiddleware.queries) * 1000)
        response['X-Mixcloud-Query-Count'] = query_count
        if request.user.is_staff:
            if 'gzip' not in response.get('Content-Encoding', '') and response.get('Content-Type', '').split(';')[0] in HTML_TYPES:
                query_json = json.dumps([
                    {'sql': query['sql'], 'time': query['time'], 'count': query['count']}
                    for query in SpeedbarMiddleware.queries
                ])


                response.content = (
                  smart_unicode(response.content)
                  .replace(
                    '<span id="query-count"></span>',
                    smart_unicode('<span id="query-count">%s</span>' % (query_count,)))
                  .replace(
                    '<span id="query-time"></span>',
                    smart_unicode('<span id="query-time">%s</span>' % (query_time,)))
                  .replace(
                    '<script id="query_details_script"></script>',
                    u'<script id="query_details_script">var query_details = %s;</script>' % (query_json,))
                  )
                if response.get('Content-Length', None):
                    response['Content-Length'] = len(response.content)
        return response

    @classmethod
    def record_query_details(cls, sql, time, backtrace, count=1):
        cls.queries.append({'sql': sql, 'time': time, 'backtrace': backtrace, 'count': count})
