# Writing modules

Speedbar uses modules to measure usage of different subsystems (databases, search backends,
templates, etc).

## Minimal module implementation

A minimal module consists of a python module with an `init` function taking no arguments, which
returns a type (not an instance) derived from BaseModule. An instance of the returned type will be
created for each request.

```python
from .base import BaseModule

class MyModule(BaseModule):
    pass

def init():
    return MyModule
```

To make this module availble you must also add it to the list in the `SPEEDBAR_MODULES` setting.
The list of included default modules is in `utils.py`.

## Showing data to the user

Modules can expose their data in two ways. Firstly by overriding `get_metrics` and `get_details`.
Secondly by adding nodes to the stacktracer module, which builds the call tree rendered by the
speedtracer plugin. Most modules should do both.

`get_metrics` returns a dictionary of high level statistics about the subsystem being monitored,
for example the total number of queries made against a database and the total time spend in all
queries. `get_details` should return a list of all operations performed against the subsystem,
by convention in the form:

```python
[
   {'operation': 'ate_something', 'key': 'apple', time: 13},
   {'operation': 'drank_something', 'key': 'coffee', time: 5},
   ...
]
```

The stacktracer stores a tree of operations, corresponding to a summary of the execution stack the
server went through while executing the request. The start of an operation is recorded by calling
`RequestTrace.instance().stacktracer.push_stack()` and the end by a corresponding `pop_stack()`
call. For most modules you will not call these yourself, but instead use one of the monkey patching
helper methods to call them for you.

For modules which record all their operations to the stacktracer there are helpers for implementing
`get_metrics` and `get_details`. See one of the existing implementations (e.g. `memcache.py`) for
details.

## Collecting data

In most cases speedtracer modules collect data by monkey patching subsystem methods to add a
wrapper which calls `push_stack` and `pop_stack`. There is a helper decorator called `trace_method`
to help with this. It takes the type and method name to wrap as arguments, and expects to decorate
a function which returns information about what work is being wrapped. If no name is provided it
assumes the method is named the same as the decorated function.

For example if we wished to write a tracer for a simple http library it might look like this:

```python
from .stacktracer import trace_method

def init():
    @trace_method(HttpRequest)
    def get(self, url):
        return (
            'HTTP',          # Module identifier
            'GET %', % url,  # Human readable summary of operation
            {}               # Any extra custom data
        )
```
