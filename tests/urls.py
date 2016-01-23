try:
    # Django <1.6
    from django.conf.urls.defaults import *
except ImportError:
    # Django >=1.6
    from django.conf.urls import *


def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = patterns('',
    url('^$', foo, name='speedbar_test_url'),
    (r'^speedbar/', include('speedbar.urls')),
)