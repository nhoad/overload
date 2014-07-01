import pytest

from overload import overload


@pytest.yield_fixture(scope='function')
def clear_cache():
    yield
    overload.func_cache.clear()


class TestOverloadWithClass:
    def test_straight_forward(self, clear_cache):
        int_called = False
        float_called = False

        class Foo:
            @overload
            def bar(self, a: int):
                nonlocal int_called
                int_called = True

            @overload
            def bar(self, a: float):
                nonlocal float_called
                float_called = True

        Foo().bar(1.0)
        assert float_called

        Foo().bar(1)
        assert int_called

    def test_class_method(self, clear_cache):
        try:
            class Foo:
                @overload
                @classmethod
                def foo(cls, a: int):
                    pass
        except TypeError:
            pass
        else:
            assert False, "classmethod should be one line above to be valid"

        class Foo:
            @classmethod
            @overload
            def foo(cls, a: int):
                pass

    def test_static_method(self, clear_cache):
        try:
            class Foo:
                @overload
                @staticmethod
                def foo(a: int):
                    pass
        except TypeError:
            pass
        else:
            assert False, "staticmethod should be one line above to be valid"

        class Foo:
            @staticmethod
            @overload
            def foo(cls, a: int):
                pass

    def test_multiple_instances(self, clear_cache):
        class Foo:
            def __init__(self, n):
                self.n = n

            @overload
            def foo(self, a: int):
                print('foo int! {}'.format(self.n))
                return self.n

        a = Foo(1)
        b = Foo(2)
        assert a.foo(5) == 1
        assert b.foo(5) == 2


class TestOverloadFunctions:
    def test_partial_annotations_fail(self, clear_cache):
        try:
            @overload
            def func(a: int, b):
                pass
        except RuntimeError:
            pass
        else:
            assert False, "Missing annotation on parameter b should raise"

    def test_zero_arguments_fail(self, clear_cache):
        try:
            @overload
            def func():
                pass
        except RuntimeError:
            pass
        else:
            assert False, "Function takes no arguments; overload is pointless"

    def test_args_fail(self, clear_cache):
        try:
            @overload
            def func(*args):
                pass
        except RuntimeError:
            pass
        else:
            assert False, "Variable positional args is impossible to handle"

    def test_kwargs_fail(self, clear_cache):
        try:
            @overload
            def func(**kwargs):
                pass
        except RuntimeError:
            pass
        else:
            assert False, "Variable keyword args is impossible to handle"

    def test_duplicates_fail(self, clear_cache):
        @overload
        def func(a: int):
            pass

        try:
            @overload
            def func(a: int):
                pass
        except RuntimeError:
            pass
        else:
            assert False, "Same type annotations should fail"

    def test_lookup_failure_fail(self, clear_cache):
        @overload
        def func(a: int):
            pass

        try:
            func(1.0)
        except RuntimeError:
            pass
        else:
            assert False, "No function exists for float; should complain"
