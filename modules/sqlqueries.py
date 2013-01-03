from __future__ import absolute_import
from .base import BaseModule, RequestTrace


class Module(BaseModule):
    key = 'sql'

    def __init__(self):
        super(Module, self).__init__()
        self.queries = []

    def get_metrics(self):
        return RequestTrace.instance().stacktracer.get_node_metrics('SQL')

    def get_details(self):
        sql_nodes = RequestTrace.instance().stacktracer.get_nodes('SQL')
        return [{'sql': node.label, 'time': node.duration} for node in sql_nodes]
