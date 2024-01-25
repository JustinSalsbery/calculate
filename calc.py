#! python3
# author: Justin Salsbery

from sys import argv
from enum import Enum


def main():
    text = setup()
    tokens = lex(text)
    parse(tokens)
    pemdas = order(tokens)
    run(tokens, pemdas)


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
    if "-h" in text or "--help" in text:
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
    (id, precedence) ; must evaluate in order of precedence
    """

    NUM = (0, None)
    EQ = (1, 0)  # ==
    N_EQ = (2, 0)  # !=
    LS = (3, 0)  # <
    GR = (4, 0)  # >
    LS_EQ = (5, 0)  # <=
    GR_EQ = (6, 0)  # >=
    L_AND = (7, 0)  # &&
    L_OR = (8, 0)  # ||
    ADD = (9, 1)  # +
    SUB = (10, 1)  # -
    B_AND = (11, 1)  # &
    B_OR = (12, 1)  # |
    B_NOT = (13, 1)  # ~
    B_XOR = (14, 1)  # ^
    MUL = (15, 2)  # *
    DIV = (16, 2)  # /
    MOD = (17, 2)  # %
    R_SHF = (18, 2)  # >>
    L_SHF = (19, 2)  # <<
    EXP = (20, 3)  # **
    PAREN = (21, 4)  # ()


class Token():
    def __init__(self, token: TokenType, paren_level: int):
        self.token = token
        self.paren_level = paren_level

    def __repr__(self):
        return f"({self.token.name}, {self.paren_level})"


class TokenNum(Token):
    def __init__(self, value: int):
        super().__init__(TokenType.NUM, 0)
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

                token = TokenNum(num)
                tokens.append(token)

                i = index + 1
                continue  # skip to next iteration

            elif base == "x":  # base 16
                num, index = lex_num(text, i + 2, text_len)
                num = int(num, 16)

                token = TokenNum(num)
                tokens.append(token)

                i = index + 1
                continue  # skip to next iteration

        if char.isdigit():  # base 10
            num, index = lex_num(text, i, text_len)
            num = int(num)

            token = TokenNum(num)
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


def lex_num(text: str, index: int, text_len: int) -> tuple[str, int]:
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


def eat_num(tokens: list[Token], index: int) -> int:
    """
    removes binary not operators from tokens ; must reevaluate tokens length
    """

    token = tokens[index]
    b_not = False

    while token.token.name == TokenType.B_NOT.name:
        b_not = not b_not

        tokens.pop(index)
        token = tokens[index]

    if not isinstance(token, TokenNum):
        print(f"Error: expected number at token {index}")
        exit(1)

    token.b_not = b_not
    return index + 1


def eat_op(tokens: list[Token], index: int) -> int:
    token = tokens[index]
    if token.token.name == TokenType.NUM.name \
            or token.token.name == TokenType.B_NOT.name:
        print(f"Error: expected operator at token {index}")
        exit(1)

    return index + 1


# *****************************************************************************
# RUNTIME *********************************************************************
# *****************************************************************************


# this is a naive runtime. run() in particular is O(n^2).
# a faster runtime is possible, but irrelevant due to size of n.
# for a simple optimization, tokens might be a doubly linked list
# and pemdas a sorted array. currently the indexes in pemdas
# desync, but pointers solve that issue.


def order(tokens: list[Token]) -> list[list[int]]:
    """
    (precedence, index) ; sorted by precedence then index
    """

    paren_prec = TokenType.PAREN.value[1]

    pemdas = []
    tokens_len = len(tokens)

    for index in range(tokens_len):
        token = tokens[index]

        value = token.token.value[1]
        if value is None:  # numbers don't have precedence
            continue

        prec = token.paren_level * paren_prec + value
        pemdas.append([prec, index])

    def key(op: list[int]):
        return op[0]

    pemdas.sort(key=key, reverse=True)  # stable sort
    return pemdas


def run(tokens: list[Token], pemdas: list[list[int]]):
    pemdas_len = len(pemdas)
    res = 0

    while pemdas_len:
        index = pemdas[0][1]

        lhs = tokens[index - 1]  # index is op
        assert (isinstance(lhs, TokenNum))

        if lhs.b_not:
            lhs = ~ lhs.value
        else:
            lhs = lhs.value

        op = tokens[index].token.name
        rhs = tokens[index + 1]
        assert (isinstance(rhs, TokenNum))

        if rhs.b_not:
            rhs = ~ rhs.value
        else:
            rhs = rhs.value

        res = calc(lhs, op, rhs)

        token = tokens[index - 1]
        assert (isinstance(token, TokenNum))
        token.value = res

        tokens.pop(index)  # op
        tokens.pop(index)  # rhs
        pemdas.pop(0)

        pemdas_len = len(pemdas)
        for scan in range(pemdas_len):  # inefficient; O(n^2)
            original = pemdas[scan][1]
            if original > index:
                pemdas[scan][1] -= 2

    print("Result:")
    print(f"\t{res}")


def calc(lhs: int, op: str, rhs: int) -> int:
    if op == TokenType.ADD.name:
        return lhs + rhs

    elif op == TokenType.SUB.name:
        return lhs - rhs

    elif op == TokenType.MUL.name:
        return lhs * rhs

    elif op == TokenType.DIV.name:
        return lhs // rhs

    elif op == TokenType.MOD.name:
        return lhs % rhs

    elif op == TokenType.EXP.name:
        return lhs ** rhs

    elif op == TokenType.B_AND.name:
        return lhs & rhs

    elif op == TokenType.B_OR.name:
        return lhs | rhs

    elif op == TokenType.B_XOR.name:
        return lhs ^ rhs

    elif op == TokenType.R_SHF.name:
        return lhs >> rhs

    elif op == TokenType.L_SHF.name:
        return lhs << rhs

    elif op == TokenType.EQ.name:
        return lhs == rhs

    elif op == TokenType.N_EQ.name:
        return lhs != rhs

    elif op == TokenType.LS.name:
        return lhs < rhs

    elif op == TokenType.GR.name:
        return lhs > rhs

    elif op == TokenType.LS_EQ.name:
        return lhs <= rhs

    elif op == TokenType.GR_EQ.name:
        return lhs >= rhs

    elif op == TokenType.L_AND.name:
        return lhs and rhs

    elif op == TokenType.L_OR.name:
        return lhs or rhs

    else:
        print(f"RuntimeError: {op} is not defined")
        exit(1)


if __name__ == "__main__":
    main()
