from overload import overload


@overload
def hello(name: str):
    print('Hello, %s!' % name)


@overload
def hello(name: int):
    print('Hello, robot no. %d!' % name)


@overload
def hello(name: float):
    print("I can't exactly work out your name... is %.2f close?" % name)


@overload
def hello(name: float, name2: str):
    print("You have two names? One is a number, the other str?")


hello('bob')
hello(5)
hello(5.123412341234)
hello(5.123412341234, 'bob')


class Greeter:
    @classmethod
    @overload
    def hello(name: str):
        print('Hello, %s!' % name)

    @overload
    def hello(name: int):
        print('Hello, robot no. %d!' % name)

    @overload
    def hello(name: float):
        print("I can't exactly work out your name... is %.2f close?" % name)

    @overload
    def hello(name: float, name2: str):
        print("You have two names? One is a number, the other str?")


Greeter().hello('bob')
Greeter.hello('bob')
Greeter().hello(5)
Greeter().hello(5.123412341234)
Greeter().hello(5.123412341234, 'bob')
