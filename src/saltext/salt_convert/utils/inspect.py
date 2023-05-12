import inspect


def function_args(module, func, builtin_data):
    """
    Inspect a function's args and compare it to the
    builtin data.
    """
    module = inspect.signature(getattr(module, func))
    return [x for x in module.parameters if x in builtin_data.keys()]
