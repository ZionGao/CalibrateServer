from enum import IntEnum


class ResponseStatus(IntEnum):
    FAIL = 1
    SUCCESS = 0
    ERR_PARAM = 2
    TYPE_ERROR = 9
    OTHER = 10
