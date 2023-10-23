from src.lexer import Lexer, TokenType


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
