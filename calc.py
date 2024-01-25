#! python3
# author: Justin Salsbery

from sys import argv
from enum import Enum


def main():
    text = setup()
    tokens = lex(text)
    parse(tokens)
    print(tokens)


# *****************************************************************************
# HELP MESSAGE ****************************************************************
# *****************************************************************************


def setup() -> str:
    """
    handle help and return arguments as a string
    """

    argv.pop(0)  # remove file name
    if len(argv) == 0:
        print('calc --help')
        print()
        print('examples:')
        print('\tcalc "3 * 9"')
        print('\tcalc "0x12 ** 2 << 1 == (1 + 9)"')

        exit(1)

    text = "".join(argv)
    if "help" in text:
        print("terminal calculator")
        print()
        print("format:")
        print("\tdecimal    : none, ex. 123456")
        print("\tbinary     : 0b  , ex. 0b0101")
        print("\thexadecimal: 0x  , ex. 0xabcd")
        print()
        print("operations:")
        print("\t+ : add                   - : subtract")
        print("\t* : multiply              / : divide")
        print("\t% : modulus               ** : exponentiation")
        print("\t& : bitwise and           | : bitwise or")
        print("\t~ : bitwise not           ^ : bitwise xor")
        print("\t&& : logical and          || : logical or")
        print("\t< : lesser                > : greater")
        print("\t== : equal                != : not equal")
        print("\t>= : greater or equal     <= : lesser or equal")
        print("\t<< : left shift           >> : right shift")

        exit(1)

    return text


# *****************************************************************************
# TOKEN DEFINITIONS ***********************************************************
# *****************************************************************************


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
        self.b_not = False

    def __repr__(self):
        return f"({self.token.name}, {self.paren_level}, {self.b_not}, {self.value})"


# *****************************************************************************
# LEXICAL ANALYSIS ************************************************************
# *****************************************************************************


def lex(text: str) -> list[Token]:
    """
    convert string to list of tokens
    """

    tokens = []

    i = 0
    paren_level = 0
    text_len = len(text)

    while i < text_len:
        char = text[i]

        # numbers can be: 0b01... ; 0xab... ; 123...
        if char == "0":
            base = text[i + 1]

            if base == "b":  # base 2
                num, index = lex_num(text, i + 2, text_len)
                num = int(num, 2)

                token = TokenNum(num, paren_level)
                tokens.append(token)

                i = index
                continue  # skip to next iteration

            elif base == "x":  # base 16
                num, index = lex_num(text, i + 2, text_len)
                num = int(num, 16)

                token = TokenNum(num, paren_level)
                tokens.append(token)

                i = index
                continue  # skip to next iteration

        if char.isdigit():  # base 10
            num, index = lex_num(text, i, text_len)
            num = int(num)

            token = TokenNum(num, paren_level)
            tokens.append(token)

            i = index

        elif char == " ":
            pass

        elif char == "\n":
            pass

        elif char == "\t":
            pass

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
            if text[i + 1] == "*":
                token = Token(TokenType.EXP, paren_level)
                i += 1
            else:
                token = Token(TokenType.MUL, paren_level)

            tokens.append(token)

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

        i += 1

    assert (not paren_level)
    return tokens


def lex_num(text: str, index: int, text_len: int):
    """
    scan entire number
    """

    word = ""

    while index < text_len and text[index].isalnum():
        word += text[index]
        index += 1

    return (word, index - 1)


# *****************************************************************************
# GRAMMAR PARSING *************************************************************
# *****************************************************************************


def parse(tokens: list[Token]):
    """
    verify the grammar is legal
    """

    index = eat_num(tokens, 0)
    tokens_len = len(tokens)

    while index < tokens_len:
        index = eat_op(tokens, index)
        assert (index < tokens_len)

        index = eat_num(tokens, index)
        tokens_len = len(tokens)


def eat_num(tokens: list[Token], index: int):
    """
    removes binary not operators from tokens ; must reevaluate tokens length
    """

    token = tokens[index]
    b_not = False

    while token.token.name == TokenType.B_NOT.name:
        b_not = not b_not

        tokens.pop(index)
        token = tokens[index]

    if isinstance(token, TokenNum):
        token.b_not = b_not
    else:
        print(f"Error: expected number at token {index}")
        exit(1)

    return index + 1


def eat_op(tokens: list[Token], index: int):
    token = tokens[index]
    if token.token.name == TokenType.NUM.name \
            or token.token.name == TokenType.B_NOT.name:
        print(f"Error: expected operator at token {index}")
        exit(1)

    return index + 1


# *****************************************************************************
# RUNTIME *********************************************************************
# *****************************************************************************


def order(tokens: list[Token]):
    pass


def run(tokens: list[Token]):
    pass


if __name__ == "__main__":
    main()
