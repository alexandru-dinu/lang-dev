import enum
import itertools
import struct
from typing import NewType

memloc = NewType("memloc", int)


class ParseError(Exception):
    pass


class MemoryError(Exception):
    pass


def to_ieee754(num: float) -> bytes:
    return bytes(struct.pack("!f", num))


def from_ieee754(bs: bytes) -> float:
    (res,) = struct.unpack("!f", bs)
    return res


class Memory:
    SIZE: int = 2**20  # 1MB
    REGION: list[memloc | None] = [None] * SIZE
    # map variable names to (start, end) locations in `MEM`
    TABLE: dict[str, tuple[memloc, memloc]] = {}

    @staticmethod
    def find_first(size: int) -> memloc:
        for i in range(Memory.SIZE - size):
            if all(x == None for x in Memory.REGION[i : i + size]):
                return i
        raise MemoryError(f"Could not find empty region of {size=}")

    @staticmethod
    def fill_value(loc_start: memloc, loc_end: memloc, bs: bytes) -> None:
        assert len(bs) == loc_end - loc_start
        for i in range(len(bs)):
            Memory.REGION[loc_start + i] = bs[i]

    @staticmethod
    def get_value(name: str) -> float:
        assert name in Memory.TABLE

        val = Memory.REGION[slice(*Memory.TABLE[name])]

        return from_ieee754(bytes(val))


@enum.unique
class Types(enum.Enum):
    t_f32 = "f32"


def get_size_of_type(typ: Types) -> int:
    match typ:
        case Types.t_f32:
            return 4
        case _:
            NotImplementedError


@enum.unique
class Keywords(enum.Enum):
    k_var = "var"


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


def parse_var(code: str) -> tuple[memloc, str | None]:
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

    typ_size = get_size_of_type(typ)
    loc = Memory.find_first(typ_size)
    Memory.TABLE[name] = (loc, loc + typ_size)
    Memory.fill_value(loc, loc + typ_size, to_ieee754(float(value)))


if __name__ == "__main__":
    import io

    code = """
    var foo: f32 = 34;
    var bar: f32 = 35;
    """.strip()

    for line in io.StringIO(code).readlines():
        parse_var(line)

    foo = Memory.get_value("foo")
    bar = Memory.get_value("bar")
    assert foo + bar == 69
