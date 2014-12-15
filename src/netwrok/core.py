import asyncio

event_handlers = dict()
function_handlers = dict()


def handler(fn):
    """
    Register a function to receive and handle events.
    """
    module = fn.__module__.split(".")[-1]
    key = module + "." + fn.__name__
    print("Registering Event Handler: '" + key + "' from " + fn.__module__)
    fn = asyncio.coroutine(fn)
    event_handlers[key] = fn
    return fn


def function(fn):
    """
    Register a function to receive a request and return a result
    """
    module = fn.__module__.split(".")[-1]
    key = module + "." + fn.__name__
    print("Registering Function Handler: '" + key + "' from " + fn.__module__)
    fn = asyncio.coroutine(fn)
    function_handlers[key] = fn
    return fn
