import argparse
import os
import sys
from xml.etree import ElementTree

from dxml import dictify
from errors import *
from instructions import Instruction
import scope # For debug reasons
"""
While loop:
Value position represents instruction order (or position of instruction in our instructions list).
We increment it after each instruction.
For first Instruction objects initiated. Then it executed.
Position can be changed with some commands. 
If execute returns value - it means that some instruction wants to change regular way of program run.
It can be: JUMP or CALL or RETURN.
When we see some JUMP instruction we are waiting for label id. 
But if there is no label id - it means that interpreter didnt saw any label.
So we need to continue to discover file instruction by instruction to find label.
IF label havn't found since all file was discovered - it means that label doesn't exist.
"""

help_message = "IPPcode18 interpreter. Usage python3 interpret.py --file=filename.xml"

if len(sys.argv) > 1:
    if "--help" in sys.argv and len(sys.argv) > 2:
        print("--help is single argument", file=sys.stderr)
        exit(10)

try:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source", nargs=1, dest="file", required=True, type=str, )
    file = parser.parse_args().file[0]
    if not os.path.exists(file):
        print("Path isn't correct", file=sys.stderr)
        exit(10)
except SystemExit:
    exit(10)



try:
    tree = ElementTree.parse(file)
except OSError:
    print("Error with opening file", file=sys.stderr)
    exit(11)
except ElementTree.ParseError:
    print("XML error", file=sys.stderr)
    exit(31)

try:
    root = tree.getroot()
    xmldict = dictify(root)
except:
    print("Unknown error was happened", file=sys.stderr)
    exit(99)

position = 0
label_mode = None

try:
    if xmldict.get("program").get("language") != "IPPcode18":
        exit(31)
except:
    exit(31)



while position < len(xmldict["program"]["instruction"]):
    x = xmldict["program"]["instruction"][position]
    try:
        if isinstance(label_mode, str):
            if x["opcode"].upper() == "LABEL":
                instruction = Instruction(x, position)
                instruction.execute()
                if instruction.check_label(label_mode):
                    label_mode = None

            position += 1
            continue

        instruction = Instruction(x, position)

        # Errors except statement to exit with correct code

        instruction_return = instruction.execute()
        error = None
    except SemanthicError as e:
        error = e
        error_code = 52
    except IncorrectOperandsError as e:
        error = e
        error_code = 53
    except VariableDoesntExist as e:
        error = e
        error_code = 54
    except ScopeDoesntExist as e:
        error = e
        error_code = 55
        raise e
    except MissingValueError as e:
        error = e
        error_code = 56
    except ZeroDivisionError as e:
        error = e
        error_code = 57
    except StringError as e:
        error = e
        error_code = 58
    except SyntaxError as e:
        error = e
        error_code = 32
    except Exception as e:
        error = e
        error_code = 99

    finally:
        if error:
            try:
                args = "\n     ".join(
                        ["Arg{}: type:{}, value:{}".format(idx + 1, x["type"], x["__val__"]) for idx, x in
                         enumerate(instruction.arguments)]) if x["opcode"] == instruction.name else "Unavailable"
            except (NameError, KeyError):
                args = "Unavailable"
            print(
                "\n\nError occurred: {exception}\nInstruction name: {name}.\nStack:{stack}\nOrder: {order}\nGF:{GF}\nTF: {TF}\nArguments:\n    {args}\n\n{error}".format(
                    name=x["opcode"],
                    order=position+1,
                    args=args,
                    error=error,
                    stack = scope.STACK,
                    GF=scope.GF,
                    TF=scope.TF,
                    exception=error.__class__.__name__
                ), file=sys.stderr)
            exit(error_code)

    if isinstance(instruction_return, int):
        position = instruction_return
        continue
    elif isinstance(instruction_return, str):
        label_mode = instruction_return

    position += 1

if isinstance(label_mode, str):
    print("SemanthicError: Label is not defined: {}".format(label_mode), file=sys.stderr)
    raise exit(52)

