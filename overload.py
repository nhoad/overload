import inspect

from collections import defaultdict

func_cache = defaultdict(list)


def overload(func):
    argspec = inspect.getfullargspec(func)
    key = '.'.join([func.__module__, func.__name__])

    if not len(argspec.args):
        raise RuntimeError('{} does not have take any arguments'.format(key))
    elif argspec.varargs or argspec.varkw:
        raise RuntimeError('{} uses variable length arguments'.format(key))
    elif len(argspec.annotations) != len(argspec.args):
        raise RuntimeError('{} does not have annotations on all parameters.'.format(key))
    func_cache[key].append(func)
    return overloaded(key)


def find_func(name, args, kwargs):
    funcs = func_cache[name]

    for func in funcs:
        try:
            call_map = inspect.getcallargs(func, *args, **kwargs)
        except TypeError:
            continue

        for key, expected_type in func.__annotations__.items():
            if expected_type != type(call_map[key]):
                break
        else:
            return func

    formatted_kwargs = ', '.join('{}={}'.format(k, v) for (k, v) in kwargs.items())

    raise RuntimeError('Could not find a mapping for {} that accepts {} {}'.format(name, args, formatted_kwargs))


def overloaded(name):
    def call(*args, **kwargs):
        func = find_func(name, args, kwargs)
        return func(*args, **kwargs)
    return call
