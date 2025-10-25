import jinja2

from stack_pl import StackPL


def test_arithmetic():
    s = StackPL()
    out = s.execute(
        """\
        2 3 +
        peek
        7 10 -
        peek
        dump
        +
        peek
        pop
        pop
        1 2 3
        dump
        """
    )
    assert list(out) == [5, -3, [5, -3], 2, [1, 2, 3]]


def test_vars():
    s = StackPL()
    out = s.execute(
        """\
        10 mov x
        23 mov y
        load x
        load y
        *
        peek
        mov z
        peek
        vars
        load y 17 /
        peek
        """
    )
    assert list(out) == [230, None, {"x": 10, "y": 23, "z": 230}, round(23 / 17, 4)]


def test_if_else():
    s = StackPL()
    out = s.execute(
        """\
        -7 mov z
        42 20 > if
            10 mov x
            42 mov y
            load x load y * 42 == if
                3.14 mov ok
            else
                -3 2 * -6 == if
                    1010 mov ok
                else
                    -42 mov ok
                end
                35 mov needle
                10 peek
            end
            20 peek
            / peek
            17 mov foobar
        end
        load z
        vars
        """
    )
    assert list(out) == [
        10,
        20,
        0.5,
        {"z": -7, "x": 10, "y": 42, "ok": 1010, "needle": 35, "foobar": 17},
    ]


def test_while():
    s = StackPL()
    out = s.execute(
        """\
        0 mov i
        10 mov n
        while
            load i load n <=
        do
            load i 2 % 1 == if
                load i peek pop
            end
            load i 1 + mov i
        end
        """
    )
    assert list(out) == list(range(1, 10, 2))


def test_nested_while():
    s = StackPL()
    out = s.execute(
        """\
        1 mov i
        5 mov n
        while
            load i load n <=
        do
            1 mov j
            while
                load j load i <=
            do
                load j peek pop
                load j 1 + mov j
            end
            load i 1 + mov i
        end
        """
    )
    assert list(out) == sum([list(range(1, n + 1)) for n in range(1, 5 + 1)], [])


def test_fizzbuzz():
    # uglier impl. but shows nesting
    s = StackPL()
    out = s.execute(
        """\
        1 mov i
        20 mov n
        while
            load i load n <=
        do
            load i 3 % 0 == load i 5 % 0 == && if
                -15 peek pop
            else
                load i 3 % 0 == if
                    -3 peek pop
                else
                    load i 5 % 0 == if
                        -5 peek pop
                    else
                        load i peek pop
                    end
                end
            end
            load i 1 + mov i
        end
        """
    )
    v1 = list(out)

    # cleaner impl.
    s = StackPL()
    out = s.execute(
        """\
        1 mov i
        20 mov n
        while
            load i load n <=
        do
            -1 mov x
            load i 3 % 0 == if
                load x 3 * mov x
            end
            load i 5 % 0 == if
                load x 5 * mov x
            end
            load x -1 == if
                load i peek pop
            else
                load x peek pop
            end
            load i 1 + mov i
        end
        """
    )
    v2 = list(out)

    assert v1 == v2 == [1, 2, -3, 4, -5, -3, 7, 8, -3, -5, 11, -3, 13, 14, -15, 16, 17, -3, 19, -5]


def test_func():
    s = StackPL()
    prog = jinja2.Environment().from_string(
        """\
        func halve 1
            2 /
        end

        func collatz_once 1
            dup mov x
            2 % 0 == if
                load x call halve
            else
                load x 3 * 1 +
            end
        end

        func collatz_seq 1
            dup mov x peek
            while
                load x 1 >
            do
                call collatz_once
                dup mov x
                peek
            end
            pop
        end

        {{ arg }} call collatz_seq
        """
    )

    def _co(n):
        return 3 * n + 1 if n % 2 else n // 2

    def _cs(n):
        yield n
        if n == 1:
            return
        yield from _cs(_co(n))

    for arg in [5, 27, 91, 871, 6171]:
        assert list(s.execute(prog.render(arg=arg))) == list(_cs(arg))
