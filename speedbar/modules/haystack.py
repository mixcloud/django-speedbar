from __future__ import absolute_import

from haystack.exceptions import MissingDependency

from .base import BaseModule, RequestTrace
from .stacktracer import trace_method


ENTRY_TYPE='haystack'

class Module(BaseModule):
    key = 'haystack'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics(ENTRY_TYPE)

    def get_details(self):
        redis_nodes = RequestTrace.instance().stacktracer.get_nodes(ENTRY_TYPE)
        return [{'query_string': node.extra['query_string'], 'kwargs': node.extra['kwargs'], 'time': node.duration} for node in redis_nodes]

def init():
    def search(self, query_string, *args, **kwargs):
        models = kwargs.get('models', None)
        if models:
            description = '[%s] %s' % (", ".join(m.__name__ for m in models), query_string)
        else:
            description = '[no models specified] %s' % (query_string,)

        return (ENTRY_TYPE, 'Haystack: %s' % (description,), {'query_string' : query_string, 'kwargs': kwargs})

    try:
        from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
    except MissingDependency:
        pass
    else:
        trace_method(ElasticsearchSearchBackend)(search)

    try:
        from haystack.backends.simple_backend import SimpleSearchBackend
    except MissingDependency:
        pass
    else:
        trace_method(SimpleSearchBackend)(search)

    try:
        from haystack.backends.solr_backend import SolrSearchBackend
    except MissingDependency:
        pass
    else:
        trace_method(SolrSearchBackend)(search)

    try:
        from haystack.backends.whoosh_backend import WhooshSearchBackend
    except MissingDependency:
        pass
    else:
        trace_method(WhooshSearchBackend)(search)
