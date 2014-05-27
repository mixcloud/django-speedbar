import socket

from .base import BaseModule


class HostInformationModule(BaseModule):
    key = 'host'

    def get_metrics(self):
        return {'name': socket.gethostname()}


def init():
    return HostInformationModule
