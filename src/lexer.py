import string
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto, unique


@unique
class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    ASSIGN = auto()
    SEMICOLON = auto()

    IDENTIFIER = auto()
    LITERAL = auto()

    # keywords
    LET = auto()
    FUNCTION = auto()

    # special
    INVALID = auto()


@dataclass
class Token:
    token_type: TokenType
    literal: str


KEYWORD_MAP: dict[str, TokenType] = {
    "let": TokenType.LET,
}


@dataclass
class Lexer:
    code: str
    pos: int
    tokens: list[Token]

    def get_char(self) -> str | None:
        if self.pos >= len(self.code):
            return None

        return self.code[self.pos]

    def advance(self) -> None:
        self.pos += 1

    def emit(self, token: Token) -> None:
        self.tokens.append(token)

    def lex(self) -> "Lexer":
        while (c := self.get_char()) is not None:
            match c:
                case c if c in string.whitespace:
                    pass
                case "(":
                    self.emit(Token(TokenType.LPAREN, c))
                case ")":
                    self.emit(Token(TokenType.RPAREN, c))
                case "=":
                    self.emit(Token(TokenType.ASSIGN, c))
                case ";":
                    self.emit(Token(TokenType.SEMICOLON, c))
                case _:
                    if c.isalpha():
                        ident: str = self._read_while(lambda x: x.isalpha())
                        # if there's a known identifier
                        if (t := KEYWORD_MAP.get(ident)) is not None:
                            self.emit(Token(t, ident))
                        else:
                            self.emit(Token(TokenType.IDENTIFIER, ident))

                    elif c.isdigit():
                        lit = self._read_while(lambda x: x.isdigit())
                        self.emit(Token(TokenType.LITERAL, lit))

                    else:
                        raise NotImplementedError(f"<{c}>")

            self.advance()

        return self

    def _read_while(self, pred: Callable[[str], bool]) -> str:
        start = self.pos

        while (c := self.get_char()) is not None and pred(c):
            self.pos += 1

        end = self.pos

        out = self.code[start:end]
        self.pos -= 1

        return out


def test_simple():
    code = "let x = 5;"

    lexer = Lexer(code=code, pos=0, tokens=[])
    lexer.lex()

    expected = [
        TokenType.LET,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.LITERAL,
        TokenType.SEMICOLON,
    ]
    assert [t.token_type for t in lexer.tokens] == expected


if __name__ == "__main__":
    for t in Lexer("let x = 5;", pos=0, tokens=[]).lex().tokens:
        print(t)
