from django.conf.urls import *

urlpatterns = patterns('speedbar.views',
    url(r'^panel/(?P<trace_id>[a-zA-Z0-9_-]+)/$', 'panel', name='speedbar_panel'),
    url(r'^trace/(?P<trace_id>[a-zA-Z0-9_-]+)/$', 'trace', name='speedbar_trace'),
    url(r'^details-for-this-request/$', 'noop', name='speedbar_details_for_this_request'),
)
