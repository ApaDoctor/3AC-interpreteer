import copy
import sys

from errors import VariableDoesntExist, InternalError, SemanthicError, ScopeDoesntExist, MissingValueError

"""
Defines scopes, stack, labels, calls.
All stored data to execute program.
Contains methods to work with scopes and labels.
"""

LF = []
# LocalFrame stack. Empty by default

GF = {}
# GlobalFrame dict

TF = None
# TemperatoryFrame isn't set by default

LABELS = {}
# Labels dict. There will be stored labels

CALL = []
# Calls stack. There we store positions to return after function Call

STACK = []


def add_call(position, label):
    """
    Add position to CALL stack.
    Needed for return instruction
    :param position: Position of CALL instruction
    :param label:  Label to call
    :return: label position if defined else label name
    """
    CALL.append(position)
    # print("CALL:{}, order: {}\nLF:{}".format(CALL, position, LF), file=sys.stderr)
    return get_label(label)


def add_return():
    """
    Return to the last position defined in CALL stack
    Function pops position and returns it
    :return: position to return
    """
    try:
        val = CALL.pop()
        # print("RETURN:{}, order: {}\nLF:{}".format(CALL, val, LF), file=sys.stderr)
        # decrement_scope()
        return val
    except:
        raise MissingValueError("RETURN instruction must be after CALL")


def set_label(name: str, position: int):
    """
    Set label and it position in the LABELS scope.
    Raises error if label defined at different position.
    :param name: name of label
    :param position: position of label (order)
    :return: position of label
    """
    if LABELS.get(name) and LABELS.get(name) != position:
        raise SemanthicError("Label can't be redefined. Name: {}".format(name))
    else:
        LABELS[name] = position


def get_label(name):
    """
    Return label position if defined in LABELS stack else returns their name
    :param name: name of label
    :return: label id or label name
    """
    # print(LABELS, file=sys.stderr)
    if LABELS.get(name) is None:
        return name
    else:
        return LABELS[name]


def set_var(scope: str, name):
    """
    Declare variable to some scope.
    Raises error if scope doesnt exist - for LF and TF.
    Type and value by default are None

    :param scope: scope to set variable - in LF, GF, TF
    :param name: variable name

    """
    # print("sheet", scope, name, value, file=sys.stderr)
    if scope == "LF":
        if not LF:
            raise ScopeDoesntExist("Scope LF ins't initialized yet.")

        if LF[-1].get(name):
            raise SemanthicError("Variable redeclaration in the same indentation level. Variable: {}".format(name))

        LF[-1][name] = {"value": None, "type": None}

    elif scope == "GF":
        GF[name] = {"value": None, "type": None}

    elif scope == "TF":
        if TF is None:
            raise ScopeDoesntExist("You need to CREATEFRAME before using TF")
        else:
            if TF.get(name):
                raise SemanthicError("Variable redeclaration in the same indentation level. Variable: {}".format(name))

            TF[name] = {"value": None, "type": None}
    else:
        raise SyntaxError("Scope must be one of those: [LF, TF, GF]")

def insert_to_var(scope: str, name, value, vtype=None):
    """
    Insert value to previously declared variable
    :param scope: in LF, TF, GF
    :param name: name of variable
    :param value: value to store
    :param vtype: type of variable
    """
    try:
        if scope == "LF":
            if not LF:
                raise ScopeDoesntExist("LF in't initialized yet.")

            LF[-1][name]["value"] = value
            LF[-1][name]["type"] = vtype

        elif scope == "GF":
            GF[name]["value"] = value
            GF[name]["type"] = vtype

        elif scope == "TF":
            if TF is None:
                raise ScopeDoesntExist("You need to CREATEFRAME before using TF")

            TF[name]["value"] = value
            TF[name]["type"] = vtype

        else:
            raise SyntaxError("Scope must be one of those: [LF, TF, GF]")

    except KeyError:
        raise VariableDoesntExist("Variable {} doesnt exist".format(name))


def get_var(scope, name):
    """
    Get variable from scope
    :param scope: in LF, TF, GF
    :param name: name of variable
    :return: dict with keys "key", "type"
    """
    if scope == "GF":
        try:
            value = GF[name]
        except KeyError:
            raise VariableDoesntExist("Variable {} doesn't exist in scope {}.".format(name, scope))
    elif scope == "LF":
        if not LF:
            raise ScopeDoesntExist("LF in't initialized yet.")
        value = LF[-1].get(name)
        if value is None:
            raise VariableDoesntExist("Variable is not defined: {}\n".format(name))
    elif scope == "TF":
        if TF is None:
            raise ScopeDoesntExist("You need to CREATEFRAME before using TF")

        elif TF.get(name) is None:
            raise VariableDoesntExist("Variable is not defined: {} in scope {} \n".format(name, scope))

        value = TF[name]

    else:
        raise SyntaxError("Unknown scope: {}".format(scope))
    return value


def increment_scope():
    """
    Not used anymore.
    Increments LF scope after we get into some block.
    Copies all values to new stack item.
    Sets defined values to False(None)

    """
    try:
        new_scope = copy.deepcopy(LF[-1])
    except IndexError:
        new_scope = {}

    for x in new_scope:
        try:
            del new_scope[x]["defined"]
        except KeyError:
            pass

    LF.append(new_scope)


def decrement_scope():
    """
    If there is not declared values at this scope - saves value to next item in stack.
    Then pops last item.
    :return:
    """
    scope = LF.pop()

    for x in scope:
        if not scope[x].get("defined"):
            LF[-1][x]["value"] = scope[x]["value"]


if __name__ == "__main__":
    increment_scope()
    set_var("LF", "a", 1)

    increment_scope()
    set_var("LF", "b", 12)

    increment_scope()
    set_var("LF", "a", 3)

    increment_scope()
    set_var("LF", "a", 4)
    LF[-1]["a"]["defined"] = True

    increment_scope()
    set_var("LF", "a", 50)

    decrement_scope()
    decrement_scope()
    decrement_scope()
    decrement_scope()

    print(LF)
