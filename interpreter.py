#!/usr/bin/env python3

from collections import deque
import re
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class Token:
    type: str = ""
    val: str = ""


@dataclass
class Node:
    ...


@dataclass
class IntegerNode(Node):
    val: int


@dataclass
class VarRefNode(Node):
    val: str


@dataclass
class DefNode(Node):
    name: str
    body: Node
    args: list[str] = field(default_factory=list)


@dataclass
class CallNode(Node):
    name: str
    args: list[str] = field(default_factory=list)


def run_compiler() -> None:
    print("Smpl(s) programming language compiler\n")
    tokens = deque()
    with open("test.smp", "r") as f:
        tokenizer = Tokenizer(f.read())
        tokens = tokenizer.get_tokens()
    tree = Parser(tokens).parse()
    pprint.pprint(tree)


class Tokenizer:
    def __init__(self, inp: str) -> None:
        self.TOKEN_TYPES = [
            ("_def", r"\bdef\b"),
            ("_end", r"\bend"),
            ("_identifier", r"\b[a-zA-Z]+\b"),
            ("_integer", r"\b\d+\b"),
            ("_oparen", r"\("),
            ("_cparen", r"\)"),
            ("_comma", r","),
        ]
        self.inp = inp

    def get_tokens(self) -> Deque[Token]:
        tokens = deque()
        while self.inp:
            tokens.append(self.get_one_token())
            self.inp = self.inp.strip()
        return tokens

    def get_one_token(self) -> Token | None:
        for token_type, rgx in self.TOKEN_TYPES:
            match = re.match(rgx, self.inp)
            if match:
                st, end = match.span()
                val = self.inp[st:end]
                self.inp = self.inp[end:]
                token = Token(token_type, val)
                return token
        raise RuntimeError(f"Unexpected token at: {self.inp}")


class Parser:
    def __init__(self, tokens: Deque[Token]) -> None:
        self.tokens = tokens

    def parse(self):
        return self.parse_def()

    def parse_def(self):
        _ = self.consume("_def")
        name = self.consume("_identifier").val
        args = self.parse_args()
        body = self.parse_expr()
        _ = self.consume("_end")
        node = DefNode(name=name, args=args, body=body)
        return node

    def parse_call(self):
        name = self.consume("_identifier").val
        args = self.parse_call_args()
        node = CallNode(name=name, args=args)
        return node

    def parse_call_args(self):
        _ = self.consume("_oparen")
        args = []
        if not self.peek("_cparen"):
            args.append(self.parse_expr())
            while self.peek("_comma"):
                self.consume("_comma")
                args.append(self.parse_expr())
        _ = self.consume("_cparen")
        return args

    def parse_args(self) -> list[str]:
        _ = self.consume("_oparen")
        args = []
        if self.peek("_identifier"):
            args.append(self.consume("_identifier").val)
            while self.peek("_comma"):
                self.consume("_comma")
                args.append(self.consume("_identifier").val)
        _ = self.consume("_cparen")
        return args

    def parse_variable_ref(self):
        return VarRefNode(self.consume("_identifier").val)

    def parse_expr(self):
        if self.peek("_integer"):
            return IntegerNode(int(self.consume("_integer").val))
        elif self.peek("_identifier") and self.peek("_oparen", 1):
            return self.parse_call()
        else:
            return self.parse_variable_ref()

    def consume(self, expected_type: str) -> Token:
        token = self.tokens.popleft()
        if token.type == expected_type:
            return token
        else:
            raise RuntimeError(
                f"Expected token_type: {expected_type}, got: {token.type}"
            )

    def peek(self, expected_type: str, offset: int = 0):
        return self.tokens[offset].type == expected_type


if __name__ == "__main__":
    run_compiler()
