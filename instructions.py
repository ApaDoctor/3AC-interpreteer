import re
import sys

import scope
from errors import *

"""
Functions which names are written in upper case are predefined implementation of IPPcode instructions.
You don't need to call them directly. (Private).
All of them are called by Instruction instance
"""


def splitter(arg):
    """
    Splits argument value with @ to parse it
    :param arg: some variable name
    :return:  list with scope at [0] and name on [1] position
    """
    return arg["__val__"].split("@")


def get_symb(arg):
    """
    Get value of symb.
    If it variable - gets their value
    :param arg: symb argument
    :return: {"type": variable_type, "value": variable_value }
    """
    if arg["type"] == "var":
        var = scope.get_var(*splitter(arg))
        value = var["value"]
        v_type = var["type"]
        if v_type is None:
            raise MissingValueError("Value Missing in variable: {}".format(arg["__val__"]))

    else:

        value = arg.get("__val__")

        if value is None and arg["type"] != "string":
            raise SyntaxError("Empty data in variable")
        elif arg["type"] == "string" and value is None:
            value = ""

        v_type = arg["type"]

        if arg["type"] == "string":
            value = proceed_string_chars(value)
        elif arg["type"] == "int":
            value = int(value)

    return {"value": value, "type": v_type}


def proceed_string_chars(string):
    """
    Replace \023 chars to real chars
    :param string:
    :return: string with all replaced \023 chars
    """
    for x in set(re.findall(r"\\\d{3}", string)):
        string = string.replace(x, chr(int(x[1:])))
    return string


def operation(arguments, function, ctype="int", insert_type="int", ctype_list=False):
    """
    Operation function.
    Used to provide some action for operations with 3 arguments, like: add, sub etc.
    :param arguments: arguments list
    :param function:  function to execute with arguments
    :param ctype:  type of arguments
    :param insert_type:  type which be inserted into variable
    :param ctype_list: type can be one of the list. (ctype var is list)
    """
    processed_args = []

    for x in [1, 2]:

        data = get_symb(arguments[x])

        if (not ctype_list and data["type"] != ctype) or (ctype_list and data["type"] not in ctype):
            raise IncorrectOperandsError("Type: {}, actual: {}".format(ctype, data["type"]))

        if insert_type == "int" or data["type"] == "int":
            processed_args.append(int(data["value"]))
        else:
            processed_args.append(data["value"])

    arg1 = arguments[0]["__val__"].split("@")
    scope.insert_to_var(*arg1, function(*processed_args), insert_type)


def operation_arithmetic(arguments, function):
    symb1 = get_symb(arguments[1])
    symb2 = get_symb(arguments[2])

    if symb1["type"] != symb2["type"]:
        raise IncorrectOperandsError("Operands types are not the same: {} and {}".format(symb1["type"], symb2["type"]))

    if symb1["type"] == "int":
        rtype = "int"
        symb1 = int(symb1["value"])
        symb2 = int(symb2["value"])
    elif symb1["type"] == "float":
        rtype = "float"
        symb1 = float.fromhex(symb1["value"])
        symb2 = float.fromhex(symb2["value"])
    else:
        raise IncorrectOperandsError("Operand must be of type int or float. Actual: {} {}".format(symb1, symb2))

    arg1 = arguments[0]["__val__"].split("@")
    scope.insert_to_var(*arg1, function(symb1, symb2), rtype)


def operation_bool(arguments, function):
    """
    Wrap of operation to work with boolean instructions
    :param arguments: arguments list
    :param function:  function which will be executed with arguments
    """
    bools = {"true": True, "false": False}
    operation(arguments, lambda x, y: {True: "true", False: "false"}[function(bools[x], bools[y]) == True], "bool",
              "bool")


def compare_ops(arguments, function):
    """
    Wrap to the compare operands of operation function.
    :param arguments: arguments list
    :param function:  function which will be executed with arguments
    """
    bools = {"true": True, "false": False}

    if get_symb(arguments[1])["type"] != get_symb(arguments[2])["type"]:
        raise IncorrectOperandsError("Types in compare operands must be the same.")

    if get_symb(arguments[1])["type"] == "bool":
        ld = lambda x, y: {True: "true", False: "false"}[function(bools[x], bools[y]) == True]
    else:
        ld = lambda x, y: {True: "true", False: "false"}[function(x, y) == True]

    operation(arguments,
              ld,
              ["bool", "string", "int"],
              "bool",
              ctype_list=True)


def DEFVAR(arguments, order):
    """
    Declare variable
    """
    arg = splitter(arguments[0])
    # print("arg = {}".format(arg), file=sys.stderr)
    scope.set_var(*arg)


def MOVE(arguments, order):
    """
    Move symb to the variable
    """
    arg1 = splitter(arguments[0])

    arg2 = get_symb(arguments[1])

    scope.insert_to_var(*arg1, arg2["value"], arg2["type"])


def PRINT(arguments, order):
    """
    Write statement
    """
    value = get_symb(arguments[0])
    if value["type"] == "bool":
        print({"true": "true", "false": "false"}[value["value"]])

    else:
        print(value["value"])


def CREATEFRAME(arguments, order):
    """
    Initiate TF
    """
    scope.TF = {}


def PUSHFRAME(arguments, order):
    """
    PUSH TF data to LF
    """
    if scope.TF is None:
        raise ScopeDoesntExist("Scope TF needed to be initialized to use.")

    scope.LF.append(scope.TF)
    scope.TF = None


def POPFRAME(arguments, order):
    """
    Move data from LF to TF
    """
    if not scope.LF:
        raise ScopeDoesntExist("Scope LF isn't initialized")

    scope.TF = scope.LF.pop()


def CALL(arguments, order):
    """
    CALL function
    """
    # print("CALL:{}, order: {}\nLF:{}".format(scope.CALL, order, scope.LF))
    return scope.add_call(order, arguments[0]["__val__"])


def RETURN(arguments, order):
    """
    Return to CALL statement
    """
    # print("RETURN: {}, order: {}\nLF:{}".format(scope.CALL, order+1, scope.LF))
    return scope.add_return()


def PUSHS(arguments, order):
    """
    PUSH data to stack
    """
    symb = get_symb(arguments[0])
    scope.STACK.append(symb)


def POPS(arguments, order):
    """
    POP DATA FROM STACK
    """
    var = splitter(arguments[0])
    stack = scope.STACK
    if len(stack) == 0:
        raise MissingValueError()
    data = stack.pop()
    scope.insert_to_var(*var, data["value"], data["type"])


def CLEARS(arguments, order):
    """
    Remove all values from stack
    :param arguments: 
    :param order: 
    :return: 
    """
    scope.STACK = []


def stack_function(arguments, function, insert_type):
    """
    Function that provides stack operations wrap
    :param arguments: arguments list
    :param function: function that will be executed
    :param insert_type: type ov data will be inserted
    :return:
    """
    var = splitter(arguments[0])
    stack = scope.STACK[::]
    len_stack = len(stack)
    if len_stack < 2:
        raise VariableDoesntExist("actual len stack 2, len stack {}".format(len_stack))
    if stack[-1]["type"] != stack[-2]["type"]:
        raise IncorrectOperandsError("Types in compare operands must be the same.")
    scope.insert_to_var(*var, function(stack[-1]["value"], stack[-2]["value"]), insert_type)


def ADDS(arguments, order):
    """
    ADD with STACK values
    """
    stack_function(arguments, lambda x, y: int(x) + int(y), "int")


def SUBS(arguments, order):
    """
    SUBS with STACK values
    """
    stack_function(arguments, lambda x, y: int(x) - int(y), "int")


def MULS(arguments, order):
    """
    MULS with STACK values
    """
    stack_function(arguments, lambda x, y: int(x) * int(y), "int")


def IDIVS(arguments, order):
    """
    IDIVS with STACK values
    """
    stack_function(arguments, lambda x, y: int(x) // int(y), "int")


def stack_function_cops(arguments, function):
    """
    Wrapper to compare stack values
    """
    var = splitter(arguments[0])
    stack = scope.STACK[::]
    len_stack = len(stack)
    if len_stack < 2:
        raise VariableDoesntExist("actual len stack >= 2, len stack {}".format(len_stack))
    if stack[-1]["type"] != stack[-2]["type"]:
        raise IncorrectOperandsError("Types in compare operands must be the same.")

    bools = {True: "true", False: "false"}
    scope.insert_to_var(*var, bools[function(stack[-1]["value"], stack[-2]["value"])], "bool")


def stack_function_bool(arguments, function):
    """
    Boolean operations with stack function.
    """
    var = splitter(arguments[0])
    stack = scope.STACK[::]
    len_stack = len(stack)
    if len_stack < 2:
        raise VariableDoesntExist("actual len stack >=2, len stack {}".format(len_stack))
    if (stack[-1]["type"] != stack[-2]["type"]) != "bool":
        raise IncorrectOperandsError("Types in compare operands must be the same.")
    bools = {True: "true", False: "false"}
    scope.insert_to_var(*var, bools[function(stack[-1]["value"], stack[-2]["value"])]

                        , "bool")


def LTS(arguments, order):
    stack_function_cops(arguments, lambda x, y,: x < y)


def GTS(arguments, order):
    stack_function_cops(arguments, lambda x, y: x > y)


def EQS(arguments, order):
    stack_function_cops(arguments, lambda x, y: x == y)


def ANDS(arguments, order):
    stack_function_bool(arguments, lambda x, y: x and y)


def ORS(arguments, order):
    stack_function_bool(arguments, lambda x, y: x or y)


def NOTS(arguments, order):
    var = splitter(arguments[0])
    len_stack = len(scope.STACK)
    if len_stack < 1:
        raise VariableDoesntExist("actual len stack >= 1, len stack {}".format(len_stack))
    data = scope.STACK[-1]
    if data["type"] != "bool":
        IncorrectOperandsError("Type: bool, actual: {}".format(data["type"]))
    bools = {"true": "false", "false": "true"}
    scope.insert_to_var(*var, bools[data["value"]], "bool")


def INT2CHARS(arguments, order):
    var = splitter(arguments[0])
    len_stack = len(scope.STACK)
    if len_stack < 1:
        raise VariableDoesntExist("actual len stack >= 1, len stack {}".format(len_stack))
    data = scope.STACK[-1]
    if data["type"] != 'int':
        raise IncorrectOperandsError("Type: int, actual: {}".format(data["type"]))
    try:
        data = chr(int(data["value"]))
        scope.insert_to_var(*var, data, "string")
    except (ValueError, OverflowError):
        raise StringError


def STRI2INTS(arguments, order):
    var = splitter(arguments[0])
    len_stack = len(scope.STACK)
    if len_stack < 2:
        raise VariableDoesntExist("actual len stack >= 2, len stack {}".format(len_stack))
    index = scope.STACK[-2]
    data = scope.STACK[-1]
    if data["type"] != "string":
        raise IncorrectOperandsError("Type: string, actual: {}".format(data["type"]))
    if index["type"] != "int":
        raise IncorrectOperandsError("Type: int, actual: {}".format(index["type"]))
    try:
        scope.insert_to_var(*var, ord(data[index]), "int")
    except Exception as e:
        print(e, file=sys.stderr)
        raise StringError


def jump_stack(arguments, function):
    label = arguments[0]["__val__"]
    len_stack = len(scope.STACK)
    if len_stack < 2:
        raise VariableDoesntExist("actual len stack >= 2, len stack {}".format(len_stack))
    arg1 = scope.STACK[-1]
    arg2 = scope.STACK[-2]
    if arg1["type"] != arg2["type"]:
        raise IncorrectOperandsError()
    if function(arg1["value"], arg2["value"]):
        return scope.get_label(label)


def JUMPIFEQS(arguments, order):
    return jump_stack(arguments, lambda x, y: y == x)


def JUMPIFNEQS(arguments, order):
    return jump_stack(arguments, lambda x, y: y == x)


def ADD(arguments, order):
    operation_arithmetic(arguments, lambda x, y: x + y)


def SUB(arguments, order):
    operation_arithmetic(arguments, lambda x, y: x - y)


def MUL(arguments, order):
    operation_arithmetic(arguments, lambda x, y: x * y)


def DIV(arguments, order):
    operation_arithmetic(arguments, lambda x, y: x / y)


def IDIV(arguments, order):
    operation_arithmetic(arguments, lambda x, y: x // y)


def LT(arguments, order):
    """
    <
    :param arguments:
    :return:
    """

    compare_ops(arguments, lambda x, y: x < y)


def GT(arguments, order):
    """
    >
    :param arguments:
    :return:
    """
    compare_ops(arguments, lambda x, y: x > y)


def EQ(arguments, order):
    """
    ==
    :param arguments:
    :return:
    """
    compare_ops(arguments, lambda x, y: x == y)


def AND(arguments, order):
    """
    and
    :param arguments:
    :return:
    """
    operation_bool(arguments, lambda x, y: x and y)


def OR(arguments, order):
    """
    or
    :param arguments:
    :return:
    """
    operation_bool(arguments, lambda x, y: x or y)


def NOT(arguments, order):
    var = splitter(arguments[0])
    data = get_symb(arguments[1])
    value = {"true": "false", "false": "true"}
    if data["type"] != "bool":
        raise IncorrectOperandsError("Type: bool, actual: {}".format(data["type"]))
    scope.insert_to_var(*var, value[data["value"]], "bool")


def INT2CHAR(arguments, order):
    """
    var - variable where data will be stored
    data - data that INT2CHAR will convert

    :param arguments:
    :return:
    """
    var = splitter(arguments[0])
    data = get_symb(arguments[1])
    if data["type"] != 'int':
        raise IncorrectOperandsError("Type: int, actual: {}".format(data["type"]))
    try:
        data = chr(int(data["value"]))
        scope.insert_to_var(*var, data, "string")
    except (ValueError, OverflowError):
        raise StringError


def str_index(arguments, function, type):
    """
    var - variable where data will be stored
    data - string
    index - index 	letter ord
    :param arguments:
    :return:
    """
    var = splitter(arguments[0])
    data = get_symb(arguments[1])
    index = get_symb(arguments[2])
    if data["type"] != "string":
        raise IncorrectOperandsError("Type: string, actual: {}".format(data["type"]))
    if index["type"] != "int":
        raise IncorrectOperandsError("Type: int, actual: {}".format(index["type"]))
    try:
        scope.insert_to_var(*var, function(data["value"][int(index["value"])]), type)
    except Exception as e:
        print(e, file=sys.stderr)
        raise StringError


def STRI2INT(arguments, order):
    """
    var - variable where data will be stored
    data - string
    index - index 	letter ord
    :param arguments:
    :return:
    """
    # TODO: Fix this, i commented it
    # ord(data["value"][int(index["value"])])
    str_index(arguments, lambda x: ord(x), "int")


def READ(arguments, order):
    try:
        user_input = input()
    except EOFError:
        user_input = ""

    v_type = arguments[1]["__val__"]

    try:
        data = {
            "int": int,
            "string": str,
            "bool": lambda x: x.lower() if x.lower() == "true" else "false"
        }[v_type](user_input)
    except ValueError:
        if v_type == "int":
            data = 0
        elif v_type == "string":
            data = ""
        else:
            raise InternalError("Something happend with type")

    var = splitter(arguments[0])
    scope.insert_to_var(*var, data, v_type)
    # TODO: Float


def CONCAT(arguments, order):
    operation(arguments, lambda x, y: x + y, "string", "string")


def STRLEN(arguments, order):
    """
    s = len(str)
    :param arguments:
    :return:
    """
    var = splitter(arguments[0])
    data = get_symb(arguments[1])
    if data["type"] != "string":
        raise IncorrectOperandsError("Type: string, actual: {}".format(data["type"]))
    scope.insert_to_var(*var, len(data["value"]), "int")


def GETCHAR(arguments, order):
    str_index(arguments, lambda x: x, "string")


def SETCHAR(arguments, order):
    var = splitter(arguments[0])

    var_data = get_symb(arguments[0])

    index = get_symb(arguments[1])

    _string = get_symb(arguments[2])
    if index["type"] != "int":
        raise IncorrectOperandsError("Type: int, actual: {}".format(index["type"]))
    if var_data["type"] != "string" or _string["type"] != "string":
        raise IncorrectOperandsError("Type of arg1 and arg3 must be str, actual: {}".format(index["type"]))
    try:
        var_data = list(var_data["value"])
        var_data[int(index["value"])] = _string["value"][0]
        data = "".join(var_data)
        scope.insert_to_var(*var, data, "string")
    except IndexError:
        raise StringError("Index out of range")

    except:
        raise SemanthicError()


def TYPE(arguments, order):
    var = splitter(arguments[0])
    try:
        data = get_symb(arguments[1])
        data = {"value": data["type"], "type": "string"}
    except MissingValueError:
        data = {"type": "string", "value": ""}

    scope.insert_to_var(var[0], var[1], value=data["value"], vtype="string")


def LABEL(arguments, order):
    scope.set_label(arguments[0]["__val__"], order)
    # print(scope.LABELS)


def JUMP(arguments, order):
    return scope.get_label(arguments[0]["__val__"])


def label_jump(arguments, function, order):
    label = arguments[0]["__val__"]

    arg1 = get_symb(arguments[1])
    arg2 = get_symb(arguments[2])
    if arg1["type"] != arg2["type"]:
        raise IncorrectOperandsError("Argument types not equal {} and {}".format(arg1["type"], arg2["type"]))
    if function(arg1["value"], arg2["value"]):
        return scope.get_label(label)


def JUMPIFEQ(arguments, order):
    """
    Jump if true
    """
    return label_jump(arguments, lambda x, y: x == y, order)


def JUMPIFNEQ(arguments, order):
    """
    Jump if  x!=y
    """
    return label_jump(arguments, lambda x, y: x != y, order)


def DPRINT(arguments, order):
    """
    DPRINT statement
    """
    try:
        value = get_symb(arguments[0])
        if value["type"] == "bool":
            try:
                print({"true": "true", "false": "false"}[value["value"]], file=sys.stderr)
            except KeyError:
                print(" KeyError: value:{} type:{} ".format(value["value"], value["type"]))

        else:
            print(value["value"], file=sys.stderr)
    except:
        pass


def float_op(arguments, function, out_type, in_type):
    var = splitter(arguments[0])
    var_data = get_symb(arguments[0])
    if var_data["type"] != in_type:
        raise IncorrectOperandsError("Type: int, actual: {}".format(var_data["type"]))

    scope.insert_to_var(*var, function(var_data["value"]), out_type)


def INT2FLOAT(arguments, order):
    float_op(arguments, lambda x: float(x).hex(), "float", "int")


def FLOAT2INT(arguments, order):
    float_op(arguments, lambda x: int(float.fromhex(x)), "int", "float")


def BREAK(arguments, order):
    message = """Debug information
Instructions executed: {count}
Instruction position: {order}
Scopes:
    LF: {LF}
    GF: {GF}
    TF: {TF}
""".format(count=Instruction.COUNT, LF=scope.LF, GF=scope.GF, TF=scope.TF, order=order)
    print(message, file=sys.stderr)


class Instruction:
    COUNT = 0
    SYMB_TYPES = ["var", "string", "int", "bool", "float"]
    types_rules = {
        "var": r"",
        "symb": r"",
    }

    instructions = {
        "MOVE": ["var", "symb"],
        "CREATEFRAME": [],  # создает новый временый стек

        "PUSHFRAME": [],  # перемищения временого стека в локальній стек ошибка 55
        "POPFRAME": [],  # перемищения lf в tf ошибка 55,

        "CALL": ["label"],  #
        "DEFVAR": ["var"],
        "RETURN": [],

        "PUSHS": ["symb"],
        "POPS": ["var"],

        "ADD": ["var", "symb", "symb"],
        "SUB": ["var", "symb", "symb"],
        "MUL": ["var", "symb", "symb"],
        "IDIV": ["var", "symb", "symb"],
        "DIV": ["var", "symb", "symb"],
        "LT": ["var", "symb", "symb"],
        "GT": ["var", "symb", "symb"],
        "EQ": ["var", "symb", "symb"],
        "AND": ["var", "symb", "symb"],
        "OR": ["var", "symb", "symb"],
        "NOT": ["var", "symb"],
        "INT2CHAR": ["var", "symb"],
        "STRI2INT": ["var", "symb", "symb"],

        "READ": ["var", "type"],
        "WRITE": ["symb"],

        "CONCAT": ["var", "symb", "symb"],
        "STRLEN": ["var", "symb"],
        "GETCHAR": ["var", "symb", "symb"],
        "SETCHAR": ["var", "symb", "symb"],

        "TYPE": ["var", "symb"],

        "LABEL": ["label"],
        "JUMP": ["label"],
        "JUMPIFEQ": ["label", "symb", "symb"],
        "JUMPIFNEQ": ["label", "symb", "symb"],

        "DPRINT": ["symb"],
        "BREAK": [],

        "CLEARS": [],
        "ADDS": ["var"],
        "SUBS": ["var"],
        "MULS": ["var"],
        "IDIVS": ["var"],
        "LTS": ["var"],
        "GTS": ["var"],
        "EQS": ["var"],
        "ANDS": ["var"],
        "ORS": ["var"],
        "NOTS": ["var"],
        "INT2CHARS": ["var"],
        "STRI2INTS": ["var"],
        "JUMPIFEQS": ["label"],
        "JUMPIFNEQS": ["label"],

        "INT2FLOAT": ["var"],
        "FLOAT2INT": ["var"]

    }

    # EACH function assigned to instruction must take two arguments arguments, order
    # TODO: better to take Instruction instance
    functions = {
        "DEFVAR": DEFVAR,  # Tested
        "MOVE": MOVE,  # Tested

        "ADD": ADD,  # Tested
        "MUL": MUL,  # Tested
        "IDIV": IDIV,  # Tested
        "DIV": DIV,  # Tested
        "SUB": SUB,  # Tested
        "WRITE": PRINT,  # Tested
        "TYPE": TYPE,  # Tested
        "DPRINT": DPRINT,  # Tested
        "BREAK": BREAK,  # Tested
        "STRLEN": STRLEN,  # Tested
        "CONCAT": CONCAT,  # TESTED
        "NOT": NOT,  # TESTED
        "AND": AND,  # TESTED
        "OR": OR,  # TESTED

        "GT": GT,  # TESTED
        "LT": LT,  # TESTED
        "EQ": EQ,  # TESTED

        "LABEL": LABEL,  # TESTED
        "JUMP": JUMP,  # TESTEED

        "CALL": CALL,  # TESTEED
        "RETURN": RETURN,  # TESTEED

        "JUMPIFEQ": JUMPIFEQ,

        "JUMPIFNEQ": JUMPIFNEQ,

        "READ": READ,

        "CREATEFRAME": CREATEFRAME,
        "PUSHFRAME": PUSHFRAME,
        "POPFRAME": POPFRAME,

        "STRI2INT": STRI2INT,
        "INT2CHAR": INT2CHAR,
        "GETCHAR": GETCHAR,
        "SETCHAR": SETCHAR,

        "PUSHS": PUSHS,
        "POPS": POPS,
        "CLEARS": CLEARS,
        "ADDS": ADDS,
        "SUBS": SUBS,
        "MULS": MULS,
        "IDIVS": IDIVS,
        "LTS": LTS,
        "GTS": GTS,
        "EQS": EQS,
        "ANDS": ANDS,
        "ORS": ORS,
        "NOTS": NOTS,
        "INT2CHARS": INT2CHARS,
        "STRI2INTS": STRI2INTS,

        "JUMPIFEQS": JUMPIFEQS,
        "JUMPIFNEQS": JUMPIFNEQS,
        "INT2FLOAT": INT2FLOAT,
        "FLOAT2INT": FLOAT2INT

    }

    def __init__(self, instruction_dict, position):
        """
        There we check that instruction used with correct arguments amount and with correct argument types.
        :param instruction_dict:
        """
        self.name = instruction_dict["opcode"].upper()
        self.arguments = []

        try:
            self.order = int(instruction_dict["order"])
        except:
            raise SyntaxError("Incorrect order")

        self.interpret_order = position + 1

        if self.interpret_order != self.order:
            raise SyntaxError("Order: {}. Set: {}".format(self.interpret_order, self.order))

        # Instruction.COUNT += 1
        if self.name not in Instruction.instructions:
            raise SyntaxError("Instruction isn't defined: {}".format(self.name))

        args = Instruction.instructions[self.name]

        # if len(instruction_dict) != len(args)+1:
        #     raise IncorrectOperandsError()

        if len(instruction_dict) != (len(args) + 2):
            raise SyntaxError("Some unknown tags here")

        if len(args) > 0:
            attributes = re.compile(r"^(arg[1-{}]|opcode|order)$".format(len(args)))
        else:
            attributes = re.compile(r"^(opcode|order)$")

        if list(filter(lambda x: attributes.match(x) is None, instruction_dict.keys())):
            raise SyntaxError("There are unknown attributes")

        for x in range(1, len(args) + 1):
            try:
                argument = instruction_dict["arg{}".format(x)][0]
            except KeyError:
                if len(instruction_dict) == x - 1:
                    raise IncorrectOperandsError(
                        "Instruction: {}. Argument count for this opcode: {}. Current:{}".format(self.name, len(args),
                                                                                                 x - 1))
                else:
                    raise SyntaxError("Incorrect operands syntax")

            # print(argument)
            # print(x-1)
            if (args[x - 1] != "symb" and argument["type"] != args[x - 1]) or \
                    (args[x - 1] == "symb" and argument["type"] not in Instruction.SYMB_TYPES):
                raise IncorrectOperandsError(
                    "Instruction: {}. Argument type must be: {}. Actual: {}".format(self.name, args[x - 1],
                                                                                    argument["type"]))

            self.arguments.append(argument)

    def execute(self):
        """
        Execute Instruction.
        Searches instruction name and calls applied function to that name
        :return:
        """
        Instruction.COUNT += 1
        return self.functions[self.name](self.arguments, order=self.order)

    def check_label(self, label):
        """
        Checks that label name is equal to :param label:
        :return: bool
        """
        instruction_label = self.arguments[0]["__val__"]
        if instruction_label == label:
            return True
        else:
            return False
