from django.conf.urls import *

urlpatterns = patterns('mixcloud.speedbar.views',
    url(r'^panel/(?P<trace_id>[a-zA-Z0-9_-]+)/$', 'panel', name='speedbar_panel'),
)
