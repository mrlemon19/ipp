# interpret.py 2. cast projektu do IPP
# interpretuje XML reprezentaci programu v IPPcode20 a generuje vystup
# @author: Jakub Lukas, xlukas18

import sys
import xml.etree.ElementTree as ET
import argparse


class instruction:
    _instList = []
    def __init__(self, opcode, order):
        self._name: str = opcode
        self._order: int = order
        self._instList.append(self)

    def getInstList(self):
        return self._instList
    
    def getName(self):
        return self._name
    
    def getOrder(self):
        return self._order


class move(instruction):
    def __init__(self, order):
        super().__init__("MOVE", order)

class createframe(instruction):
    def __init__(self, order):
        super().__init__("CREATEFRAME", order)

class pushframe(instruction):
    def __init__(self, order):
        super().__init__("PUSHFRAME", order)

class popframe(instruction):
    def __init__(self, order):
        super().__init__("POPFRAME", order)

class defvar(instruction):  
    def __init__(self, order):
        super().__init__("DEFVAR", order)

class call(instruction):
    def __init__(self, order):
        super().__init__("CALL", order)

class return_(instruction):
    def __init__(self, order):
        super().__init__("RETURN", order)

class pushs(instruction):   
    def __init__(self, order):
        super().__init__("PUSHS", order)

class pops(instruction):  
    def __init__(self, order):
        super().__init__("POPS", order)

class add(instruction):  
    def __init__(self, order):
        super().__init__("ADD", order)

class sub(instruction):  
    def __init__(self, order):
        super().__init__("SUB", order)

class mul(instruction):  
    def __init__(self, order):
        super().__init__("MUL", order)

class idiv(instruction):  
    def __init__(self, order):
        super().__init__("IDIV", order)

class lt(instruction):
    def __init__(self, order):
        super().__init__("LT", order)

class gt(instruction):
    def __init__(self, order):
        super().__init__("GT", order)

class eq(instruction):
    def __init__(self, order):
        super().__init__("EQ", order)

class and_(instruction):
    def __init__(self, order):
        super().__init__("AND", order)

class or_(instruction):
    def __init__(self, order):
        super().__init__("OR", order)

class not_(instruction):
    def __init__(self, order):
        super().__init__("NOT", order)

class int2char(instruction):
    def __init__(self, order):
        super().__init__("INT2CHAR", order)

class stri2int(instruction):
    def __init__(self, order):
        super().__init__("STRI2INT", order)

class read(instruction):
    def __init__(self, order):
        super().__init__("READ", order)

class write(instruction):
    def __init__(self, order):
        super().__init__("WRITE", order)

class concat(instruction):
    def __init__(self, order):
        super().__init__("CONCAT", order)

class strlen(instruction):
    def __init__(self, order):
        super().__init__("STRLEN", order)

class getchar(instruction):
    def __init__(self, order):
        super().__init__("GETCHAR", order)

class setchar(instruction):
    def __init__(self, order):
        super().__init__("SETCHAR", order)

class type_(instruction):
    def __init__(self, order):
        super().__init__("TYPE", order)

class label(instruction):
    def __init__(self, order):
        super().__init__("LABEL", order)

class jump(instruction):
    def __init__(self, order):
        super().__init__("JUMP", order)

class jumpifeq(instruction):
    def __init__(self, order):
        super().__init__("JUMPIFEQ", order)

class jumpifneq(instruction):
    def __init__(self, order):
        super().__init__("JUMPIFNEQ", order)

class exit_(instruction):
    def __init__(self, order):
        super().__init__("EXIT", order)

class dprint(instruction):
    def __init__(self, order):
        super().__init__("DPRINT", order)

class break_(instruction):
    def __init__(self, order):
        super().__init__("BREAK", order)

# tovarna na instrukce
class instrucionFactory:
    @classmethod
    def createInstruction(cls, opcode, order):
        if opcode == "MOVE":
            return move(order)
        elif opcode == "CREATEFRAME":
            return createframe(order)
        elif opcode == "PUSHFRAME":
            return pushframe(order)
        elif opcode == "POPFRAME":
            return popframe(order)
        elif opcode == "DEFVAR":
            return defvar(order)
        elif opcode == "CALL":
            return call(order)
        elif opcode == "RETURN":
            return return_(order)
        elif opcode == "PUSHS":
            return pushs(order)
        elif opcode == "POPS":
            return pops(order)
        elif opcode == "ADD":
            return add(order)
        elif opcode == "SUB":
            return sub(order)
        elif opcode == "MUL":
            return mul(order)
        elif opcode == "IDIV":
            return idiv(order)
        elif opcode == "LT":
            return lt(order)
        elif opcode == "GT":
            return gt(order)
        elif opcode == "EQ":
            return eq(order)
        elif opcode == "AND":
            return and_(order)
        elif opcode == "OR":
            return or_(order)
        elif opcode == "NOT":
            return not_(order)
        elif opcode == "INT2CHAR":
            return int2char(order)
        elif opcode == "STRI2INT":
            return stri2int(order)
        elif opcode == "READ":
            return read(order)
        elif opcode == "WRITE":
            return write(order)
        elif opcode == "CONCAT":
            return concat(order)
        elif opcode == "STRLEN":
            return strlen(order)
        elif opcode == "GETCHAR":
            return getchar(order)
        elif opcode == "SETCHAR":
            return setchar(order)
        elif opcode == "TYPE":
            return type_(order)
        elif opcode == "LABEL":
            return label(order)
        elif opcode == "JUMP":
            return jump(order)
        elif opcode == "JUMPIFEQ":
            return jumpifeq(order)
        elif opcode == "JUMPIFNEQ":
            return jumpifneq(order)
        elif opcode == "EXIT":
            return exit_(order)
        elif opcode == "DPRINT":
            return dprint(order)
        elif opcode == "BREAK":
            return break_(order)
        else:
            raise Exception("Unknown instruction")

if __name__ == "__main__":

    # zpracovani argumentu
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--source', help = 'source XML file in IPPcode23')
    argParser.add_argument("--input", help = "input file")
    args = argParser.parse_args()

    sourceFile = args.source
    inputFile = args.input

    # xml parser
    tree = ET.parse(sourceFile)
    root = tree.getroot()

    #TODO kontrola spravnosti xml
    