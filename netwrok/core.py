import asyncio

handlers = dict()
def handler(fn):
    """
    Register a function to receive and handle events.
    """
    module = fn.__module__.split(".")[-1]
    key = module + "." + fn.__name__
    print("Registering Event Handler: '" + key + "' from " + fn.__module__)
    fn = asyncio.coroutine(fn)
    handlers[key] = fn
    return fn
