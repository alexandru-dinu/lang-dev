"""
Simple stack-based PL.
"""

from typing import Generator

type Value = float | int

KEYWORDS = [
    "mov",
    "load",
    "if",
    "else",
    "for",
    "while",
    "do",
    "end",
    "def",
    "dup",
    "pop",
    "peek",
    "dump",
    "vars",
]


class StackPLSyntaxError(Exception):
    pass


class StackPL:
    def __init__(self):
        self.stack: list[Value] = []
        self.vars: dict[str, Value] = {}

    @staticmethod
    def _try_numeric(x) -> Value | None:
        try:
            f = float(x)
            i = int(f)
            return i if i == f else f
        except ValueError as e:
            return None

    @staticmethod
    def _requires_block(tok: str) -> bool:
        return tok in ["if", "while"]

    @staticmethod
    def _collect_until(keyword: str, tokens: list[str], index: int) -> tuple[list[str], int]:
        """Collect the block until the outermost `keyword`."""
        i = index
        block = []
        level = 1  # 1 b/c we're in the process of parsing a block

        while i < len(tokens):
            if tokens[i] == keyword:
                level -= 1
                if level == 0:
                    return block, i
                elif level < 0:
                    raise StackPLSyntaxError("Incorrect pairing of `end` instructions.")
            elif StackPL._requires_block(tokens[i]):
                level += 1

            block.append(tokens[i])
            i += 1

        raise StackPLSyntaxError("Missing `end` keyword.")

    @staticmethod
    def _split_else(tokens: list[str]) -> tuple[list[str], list[str] | None]:
        """Return block_true, block_else"""

        i = 0
        level = 1

        while i < len(tokens):
            if tokens[i] == "else":
                level -= 1
                if level == 0:
                    return tokens[:i], tokens[i + 1 :]
            elif StackPL._requires_block(tokens[i]):
                level += 1

            i += 1

        # no "else"
        return tokens, None

    def parse(self, prog: str) -> list[str]:
        return prog.split()

    def execute(self, prog: str) -> Generator:
        yield from self._run(self.parse(prog))

    def _run(self, tokens: list[str], pc: int = 0) -> Generator:
        while pc < len(tokens):
            tok = tokens[pc]

            match tok:
                case _ if (num := self._try_numeric(tok)) is not None:
                    self.stack.append(num)

                case "+" | "-" | "*" | "/" | "==" | "<" | "<=" | ">" | ">=" | "%":
                    b, a = self.stack.pop(), self.stack.pop()
                    if tok == "+":
                        self.stack.append(a + b)
                    if tok == "-":
                        self.stack.append(a - b)
                    if tok == "*":
                        self.stack.append(a * b)
                    if tok == "/":
                        self.stack.append(round(a / b, 4))
                    if tok == "==":
                        self.stack.append(a == b)
                    if tok == "<":
                        self.stack.append(a < b)
                    if tok == "<=":
                        self.stack.append(a <= b)
                    if tok == ">":
                        self.stack.append(a > b)
                    if tok == ">=":
                        self.stack.append(a >= b)
                    if tok == "%":
                        self.stack.append(a % b)

                case "mov":
                    assert self.stack
                    v = tokens[pc + 1]
                    assert v.isalpha()
                    if v in KEYWORDS:
                        raise StackPLSyntaxError(f"{v} is a reserved keyword.")
                    self.vars[v] = self.stack.pop()
                    pc += 1

                case "load":
                    v = tokens[pc + 1]
                    assert v.isalpha() and v in self.vars
                    self.stack.append(self.vars[v])
                    pc += 1

                case "if":
                    assert self.stack

                    block, pc_end = StackPL._collect_until(
                        keyword="end", tokens=tokens, index=pc + 1
                    )
                    block_true, block_else = StackPL._split_else(block)

                    if cond := self.stack.pop():
                        yield from self._run(block_true, pc=0)
                    elif block_else:
                        yield from self._run(block_else, pc=0)

                    pc = pc_end

                case "while":
                    # while <cond> do <body> end
                    block_cond, pc_do = StackPL._collect_until(
                        keyword="do", tokens=tokens, index=pc + 1
                    )
                    block_body, pc_end = StackPL._collect_until(
                        keyword="end", tokens=tokens, index=pc_do + 1
                    )

                    while True:
                        yield from self._run(block_cond, pc=0)
                        if not self.stack.pop():
                            break
                        yield from self._run(block_body)

                    pc = pc_end

                case "dup":  # no-op if stack is empty
                    if self.stack:
                        self.stack.append(self.stack[-1])

                case "pop":
                    if self.stack:
                        self.stack.pop()

                # printing
                case "peek":
                    yield self.stack[-1] if self.stack else None

                case "dump":
                    yield self.stack[::]

                case "vars":
                    yield self.vars.copy()

                # errors
                case other:
                    raise StackPLSyntaxError(f"Invalid token {other} @ index {pc}.")

            pc += 1


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


# def test_func():
#     """
#     def inc:
#         load arg 1 + mov arg
#     """
#     raise NotImplementedError


if __name__ == "__main__":
    test_nested_while()
