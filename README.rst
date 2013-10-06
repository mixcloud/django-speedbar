django-speedbar - Page performance profiling for django
=====

.. image:: https://github.com/theospears/django-speedbar/raw/master/docs/images/chrome-speedtracer.png

django-speedbar instruments key events in the page loading process (database
queries, template rendering, url resolution, etc) and provides summary
information for each page load, as well as integration with Google Chrome
SpeedTracer to show a tree of the events taking place in a page load.

It is designed to be run on live sites, with minimal performance impact.
Although all requests are monitored, results are only visible for users
with the staff flag.


Installation
-----

To install django-speedbar add it to your installed apps and add the
speedbar middleware.

::
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

To view the results in SpeedTracer you will also need to install the
`SpeedTracer plugin <https://developers.google.com/web-toolkit/speedtracer/>`_.

To include summary information in the page you can use the ``metric`` template
tag.

.. raw:: html
    {% load speedbar %}
    <div class="speedbar">
        <span>Overall: {% metric "overall" "time" %} ms</span>
        <span>SQL: {% metric "sql" "count" %} ({% metric "sql" "time" %} ms)</span>
        <!-- ... -->
    </div>

Configuration
-----

django-speedbar has a number of configuration settings.

::
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
