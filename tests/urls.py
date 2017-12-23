from django.conf.urls import url, include


def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

urlpatterns = [
    url('^$', foo, name='speedbar_test_url'),
    url(r'^speedbar/', include('speedbar.urls')),
]