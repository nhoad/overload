import inspect
import re

from collections import defaultdict

# Terrible heuristic that func actually refers to a method on a class.
# ( ͡° ͜ʖ ͡°)
METHOD_HEURISTIC = re.compile(
    r'^((.+)\.)?[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$').match


class overload:
    func_cache = defaultdict(list)

    def __init__(self, func, is_method=False):
        argspec = inspect.getfullargspec(func)

        key = '.'.join([func.__module__, func.__qualname__])

        self.is_method = is_method
        self.key = key
        self.func = func

        if is_method:
            # we're a bound method now!
            obj = func.__self__
            func_cache = obj.__dict__.setdefault('__overloaded__', defaultdict(list))
            func_cache[self.key].append(func)
            self.func_cache = func_cache
            # don't bother doing any other checks - we did those already when
            # it was decorated.
            return

        if not len(argspec.args):
            raise RuntimeError('{} does not have take any arguments'.format(key))
        elif argspec.varargs or argspec.varkw:
            raise RuntimeError('{} uses variable length arguments'.format(key))
        else:
            if not is_method:
                is_method = bool(METHOD_HEURISTIC(func.__qualname__))

            expected_annotation_count = len(argspec.annotations)
            actual_annotation_count = len(argspec.args) - int(is_method)

            if expected_annotation_count != actual_annotation_count:
                raise RuntimeError('{} does not have annotations on all parameters.'.format(key))

        for predefine_func in self.func_cache[key]:
            if func.__annotations__ == predefine_func.__annotations__:
                raise RuntimeError('Duplicate annotations found for {}'.format(key))
        self.func_cache[key].append(func)

    def __call__(self, *args, **kwargs):
        func = self.find_func(args, kwargs)
        return func(*args, **kwargs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        method = self.func.__get__(obj, type)
        bound_overload = self.__class__(method, is_method=True)

        key = self.key
        for func in self.func_cache[self.key]:
            obj.__overloaded__[key].append(func.__get__(obj, type))
        return bound_overload

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
