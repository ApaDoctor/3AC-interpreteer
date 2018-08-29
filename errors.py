"""
Error wrappers . To except errors in main file.
"""
#
# class SyntaxisError(Exception):
#     # 32
#     pass


class SemanthicError(Exception):
    # 52
    pass


class IncorrectOperandsError(Exception):
    # 53
    pass


class VariableDoesntExist(Exception):
    # 54
    pass


class ScopeDoesntExist(Exception):
    # 55
    pass


class MissingValueError(Exception):
    pass
    # 56


class StringError(Exception):
    # 58
    pass


class InternalError(Exception):
    # 99
    pass
