# Generated by https://quicktype.io

from enum import Enum
from typing import List


class TypeEnum(Enum):
    AND = "and"
    INPUT = "input"
    NOT = "not"
    OR = "or"


class L:
    type: TypeEnum
    id: int
    i: List['L']

    def __init__(self, type: TypeEnum, id: int, i: List['L']) -> None:
        self.type = type
        self.id = id
        self.i = i