#! python3
# author: Justin Salsbery

from sys import argv
from enum import Enum


def main():
    argv.pop(0)  # remove file name
    text = "".join(argv)

    tokens = parse(text)
    print(tokens)


class TokenType(Enum):
    """
    each token is: (id, priority) ; except PAREN_PRIORITY
    priority affects the order of operations
    """

    PAREN_PRIORITY = 4

    NUM = (1, None)
    ADD = (2, 1)  # +
    SUB = (3, 1)  # -
    B_AND = (4, 1)  # &
    B_OR = (5, 1)  # |
    B_NOT = (6, 1)  # ~
    B_XOR = (7, 1)  # ^
    MUL = (8, 2)  # *
    DIV = (9, 2)  # /
    MOD = (10, 2)  # %
    R_SHF = (11, 2)  # >>
    L_SHF = (12, 2)  # <<
    EXP = (13, 3)  # **
    EQ = (14, 0)  # ==
    N_EQ = (15, 0)  # !=
    LS = (16, 0)  # <
    GR = (17, 0)  # >
    LS_EQ = (18, 0)  # <=
    GR_EQ = (19, 0)  # >=
    L_AND = (20, 0)  # &&
    L_OR = (21, 0)  # ||


class Token():
    def __init__(self, token: TokenType, paren_level: int):
        self.token = token
        self.paren_level = paren_level

    def __repr__(self):
        return f"({self.token.name}, {self.paren_level})"


class TokenNum(Token):
    def __init__(self, value: int, paren_level: int):
        super().__init__(TokenType.NUM, paren_level)
        self.value = value

    def __repr__(self):
        return f"({self.token.name}, {self.paren_level}, {self.value})"


def parse(text: str) -> list[Token]:
    tokens = []
    paren_level = 0
    text_len = len(text)

    for i in range(text_len):
        char = text[i]

        # numbers can be: 0b01... ; 0xab... ; 123...
        if char == "0":
            base = text[i + 1]

            if base == "b":  # base 2
                num, index = eat_num(text, i + 2, text_len)
                num = int(num, 2)

                token = TokenNum(num, paren_level)
                tokens.append(token)

                i = index
                continue  # skip to next iteration

            elif base == "x":  # base 16
                num, index = eat_num(text, i + 2, text_len)
                num = int(num, 16)

                token = TokenNum(num, paren_level)
                tokens.append(token)

                i = index
                continue  # skip to next iteration

        if char.isdigit():  # base 10
            num, index = eat_num(text, i, text_len)
            num = int(num)

            token = TokenNum(num, paren_level)
            tokens.append(token)

            i = index

        elif char == "+":  # +
            token = Token(TokenType.ADD, paren_level)
            tokens.append(token)

        elif char == "-":  # -
            token = Token(TokenType.SUB, paren_level)
            tokens.append(token)

        elif char == "&":  # & ; &&
            if text[i + 1] == "&":
                assert (not paren_level)

                token = Token(TokenType.L_AND, paren_level)
                i += 1
            else:
                token = Token(TokenType.B_AND, paren_level)

            tokens.append(token)

        elif char == "|":  # | ; ||
            if text[i + 1] == "|":
                assert (not paren_level)

                token = Token(TokenType.L_OR, paren_level)
                i += 1
            else:
                token = Token(TokenType.B_OR, paren_level)

            tokens.append(token)

        elif char == "~":  # ~
            token = Token(TokenType.B_NOT, paren_level)
            tokens.append(token)

        elif char == "^":  # ^
            token = Token(TokenType.B_XOR, paren_level)
            tokens.append(token)

        elif char == "*":  # * ; **
            pass

        elif char == "/":  # /
            token = Token(TokenType.DIV, paren_level)
            tokens.append(token)

        elif char == "%":  # %
            token = Token(TokenType.MOD, paren_level)
            tokens.append(token)

        elif char == ">":  # > ; >> ; >=
            if (text[i + 1] == ">"):
                assert (not paren_level)

                token = Token(TokenType.R_SHF, paren_level)
                i += 1
            elif (text[i + 1] == "="):
                assert (not paren_level)

                token = Token(TokenType.GR_EQ, paren_level)
                i += 1
            else:
                token = Token(TokenType.GR, paren_level)

            tokens.append(token)

        elif char == "<":  # < ; << ; <=
            if (text[i + 1] == "<"):
                assert (not paren_level)

                token = Token(TokenType.L_SHF, paren_level)
                i += 1
            elif (text[i + 1] == "="):
                assert (not paren_level)

                token = Token(TokenType.LS_EQ, paren_level)
                i += 1
            else:
                token = Token(TokenType.LS, paren_level)

            tokens.append(token)

        elif char == "=":  # ==
            assert (not paren_level and text[i + 1] == "=")
            i += 1

            token = Token(TokenType.EQ, paren_level)
            tokens.append(token)

        elif char == "!":  # !=
            assert (not paren_level and text[i + 1] == "=")
            i += 1

            token = Token(TokenType.N_EQ, paren_level)
            tokens.append(token)

        elif char == "(":  # (
            paren_level += 1

        elif char == ")":  # )
            assert (paren_level)
            paren_level -= 1

        else:
            print(f"TokenError: {char} is not defined")
            exit(1)

    return tokens


def eat_num(text: str, index: int, text_len: int):
    word = ""

    while index < text_len and text[index].isalnum():
        word += text[index]
        index += 1

    return (word, index - 1)


if __name__ == "__main__":
    main()
