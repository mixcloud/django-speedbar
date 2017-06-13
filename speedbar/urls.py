from django.conf.urls import url
from speedbar import views

urlpatterns = [
    url(r'^panel/(?P<trace_id>[a-zA-Z0-9_-]+)/$', views.panel, name='speedbar_panel'),
    url(r'^trace/(?P<trace_id>[a-zA-Z0-9_-]+)/$', views.trace, name='speedbar_trace'),
    url(r'^details-for-this-request/$', views.noop, name='speedbar_details_for_this_request'),
]
