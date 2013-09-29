from __future__ import absolute_import

from cassandra.cluster import Session

from .base import BaseModule, RequestTrace
from .stacktracer import trace_method


class Module(BaseModule):
    key = 'cassandra'

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('CASSANDRA')

    def get_details(self):
        nodes = RequestTrace.instance().stacktracer.get_nodes('CASSANDRA')
        return [{'cql': node.label, 'time': node.duration} for node in nodes]


def init():
    # The linter thinks the methods we monkeypatch are not used
    # pylint: disable=W0612
    @trace_method(Session)
    def execute(self, query, parameters=None, *args, **kwargs):
        return ('CASSANDRA', query, {})
