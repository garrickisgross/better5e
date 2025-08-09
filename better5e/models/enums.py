from enum import Enum


class RechargeType(str, Enum):
    LONG_REST = "long_rest"
    SHORT_REST = "short_rest"
    DAWN = "dawn"
    OTHER = "other"

class Op(str, Enum):
    ADD = "add"
    SET = "set"
    GET = "get"
    MUL = "mul"

class ActionType(str, Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    DAMAGE = "damage"
    OTHER = "other"