=======================================================
django-speedbar - Page performance profiling for django
=======================================================

.. image:: https://github.com/theospears/django-speedbar/raw/master/docs/images/chrome-speedtracer.png

django-speedbar instruments key events in the page loading process (database
queries, template rendering, url resolution, etc) and provides summary
information for each page load, as well as integration with Google Chrome
SpeedTracer to show a tree of the events taking place in a page load.

It is designed to be run on live sites, with minimal performance impact.
Although all requests are monitored, results are only visible for users
with the staff flag.


Installation
============

To install django-speedbar add it to your installed apps, urls, and add the
speedbar middleware.

.. code:: python

   # settings.py

    INSTALLED_APPS = [
        # ...
        'speedbar',
        # ...
    ]

    # For best results put speedbar as near to the top of your middleware
    # list as possible. django-speedbar listens to the django request_finished
    # signal so actions performed by middleware higher up the stack will still
    # be recorded, but will not be included in summary data.
    MIDDLEWARE_CLASSES = [
        'speedbar.middleware.SpeedbarMiddleware',
        # ...
    ]

.. code:: python

    # urls.py

    urlpatterns = patterns('',
        # ...
        (r'^speedbar/', include('speedbar.urls')),
        # ...
    )


To view the results in SpeedTracer you will also need to install the
`SpeedTracer plugin <https://developers.google.com/web-toolkit/speedtracer/>`_.

To include summary information in the page you can use the ``metric`` template
tag.

.. code:: html

    {% load speedbar %}
    <div class="speedbar">
        <span>Overall: {% metric "overall" "time" %} ms</span>
        <span>SQL: {% metric "sql" "count" %} ({% metric "sql" "time" %} ms)</span>
        <!-- ... -->
    </div>

Configuration
=============

django-speedbar has a number of configuration settings.

.. code:: python

    # Enable instrumentation of page load process
    SPEEDBAR_ENABLE = True

    # Enable the summary data template tags
    SPEEDBAR_PANEL = True

    # Include headers needed to show page generation profile tree in the
    # Google Chrome SpeedTracer plugin.
    SPEEDBAR_TRACE = True

    # Include response headers with summary data for each request. These are
    # intended for logging and are included in all requests, not just staff
    # requests. If you turn this on we recommend configuring your load
    # balancer to strip them before sending the response to the client.
    SPEEDBAR_RESPONSE_HEADERS = False

    # Configure which instrumentation modules to load. This should not
    # normally be necessary for built in modules as they will only load
    # if the relevant clients are installed, but is useful for adding
    # additional custom modules.
    SPEEDBAR_MODULES = [
        'speedbar.modules.stacktracer', # Most other modules depend on this one
        'speedbar.modules.pagetimer',
        'speedbar.modules.sql',
        'myproject.modules.sprockets',
        # ...
    ]

Status
======

We run our production systems with django-speedbar installed. However, the API
is not stable and is likely to change. It does not yet have any default
templates to make it easier to use the on-page features.

Similar projects
================

There are a number of similar projects you may want to consider as well as
or instead of django-speedbar.

django-debug-toolbar
--------------------
Website: `<https://github.com/django-debug-toolbar/django-debug-toolbar>`_

The swiss army knife of django page inspection. Mature, widely used, and
with lots of plugins available. It has more of a focus on debugging and
information, and less focus on performance measurement. We found it too
slow to run on our sites in production.

New Relic
---------
Website: `<http://newrelic.com/>`_

An in depth application monitoring platform. Very useful for observing
trends in application performance and page load times. Less useful for
drilling deep into individual page loads, and has support for a smaller
set of external services. Commercial product.

django-live-profiler
--------------------
Website: `<http://invitebox.github.io/django-live-profiler/>`_

Site wide profiler for django applications. I haven't used this, so
cannot comment on it.


Credits
=======
django-speedbar was primarily written by Theo Spears whilst working at `Mixcloud <http://www.mixcloud.com/>`_.

