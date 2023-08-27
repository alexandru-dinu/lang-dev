import enum
import struct
from typing import NewType

memloc = NewType("memloc", int)


def to_ieee754(num: float) -> bytes:
    return bytes(struct.pack("!f", num))


def from_ieee754(bs: bytes) -> float:
    (res,) = struct.unpack("!f", bs)
    return res


class ParseError(Exception):
    pass


class MemoryError(Exception):
    pass


@enum.unique
class Types(enum.Enum):
    t_f32 = "f32"

    @staticmethod
    def get_size_of_type(typ: "Types") -> int:
        match typ:
            case Types.t_f32:
                return 4
            case _:
                raise NotImplementedError


@enum.unique
class Keywords(enum.Enum):
    k_var = "var"


class Memory:
    SIZE: int = 2**20  # 1MB

    def __init__(self):
        self.REGION: list[memloc | None] = [None] * self.SIZE
        # map variable names to (start, end) locations in `MEM`
        self.TABLE: dict[str, tuple[memloc, memloc]] = {}

    @property
    def is_empty(self):
        return len(self.TABLE) == 0 and all(x is None for x in self.REGION)

    def find_first(self, size: int) -> memloc:
        for i in range(self.SIZE - size):
            if all(x == None for x in self.REGION[i : i + size]):
                return memloc(i)
        raise MemoryError(f"Could not find empty region of {size=}")

    def fill_value(self, loc_start: memloc, loc_end: memloc, bs: bytes) -> None:
        assert len(bs) == loc_end - loc_start

        for i in range(len(bs)):
            self.REGION[loc_start + i] = memloc(bs[i])

    def get_value(self, name: str) -> float:
        if name not in self.TABLE:
            raise MemoryError(f"{name} not in memory table")

        val = self.REGION[slice(*self.TABLE[name])]

        return from_ieee754(bytes(val))


def consume(code: str, what: str) -> str:
    """
    Consume `what` from `code`.
    On error, returns None.
    """
    n = len(what)
    if code[:n] == what:
        return code[n:].lstrip()

    raise ParseError(f"Expected {what}, but found '{code[:n]}'")


def consume_until(code: str, stop: str) -> tuple[str, str]:
    name = ""
    rest = ""

    for i, c in enumerate(code):
        if c != stop:
            name += c
        else:
            rest = code[i + 1 :].lstrip()
            break

    return name, rest


class Interpreter:
    def __init__(self, mem: Memory):
        self.mem = mem

    def __call__(self, code: str):
        """Entrypoint"""
        # TODO: add more statement types
        self.interpret_var(code)

    def interpret_var(self, code: str):
        """
        var <name>: <type> = <value>;
        """
        code = code.strip()
        code = consume(code, Keywords.k_var.value)
        name, code = consume_until(code, ":")
        typ, code = consume_until(code, "=")

        try:
            typ = Types(typ.strip())
        except ValueError as e:
            raise ParseError from e

        value, code = consume_until(code, ";")

        if code != "":
            raise ParseError(f"Got superfluous input: {code}")

        typ_size = Types.get_size_of_type(typ)

        start = self.mem.find_first(typ_size)
        end = memloc(start + typ_size)

        self.mem.TABLE[name] = (start, end)
        self.mem.fill_value(start, end, to_ieee754(float(value)))


if __name__ == "__main__":
    import pytest

    code = """
    var foo: f32 = 34;
    var bar: f32 = 35;
    """.strip()

    interp = Interpreter(mem=Memory())

    for line in code.split("\n"):
        interp(line)

    assert interp.mem.get_value("foo") == 34
    assert interp.mem.get_value("bar") == 35

    with pytest.raises(MemoryError):
        _ = interp.mem.get_value("baz")
