import inspect

from collections import defaultdict


class overload:
    func_cache = defaultdict(list)

    def __init__(self, func):
        self.func = func
        argspec = inspect.getfullargspec(func)
        key = '.'.join([func.__module__, func.__qualname__])
        self.key = key

        if not len(argspec.args):
            raise RuntimeError('{} does not have take any arguments'.format(key))
        elif argspec.varargs or argspec.varkw:
            raise RuntimeError('{} uses variable length arguments'.format(key))
        elif len(argspec.annotations) != len(argspec.args):
            raise RuntimeError('{} does not have annotations on all parameters.'.format(key))
        self.func_cache[key].append(func)

    def __call__(self, *args, **kwargs):
        func = self.find_func(args, kwargs)
        return func(*args, **kwargs)

    def find_func(self, args, kwargs):
        funcs = self.func_cache[self.key]

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

        raise RuntimeError('Could not find a mapping for {} that accepts {} {}'.format(self.key, args, formatted_kwargs))
