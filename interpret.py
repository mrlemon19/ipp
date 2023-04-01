# interpret.py 2. cast projektu do IPP
# interpretuje XML reprezentaci programu v IPPcode20 a generuje vystup
# @author: Jakub Lukas, xlukas18

import sys
import xml.etree.ElementTree as ET
import argparse

# instrucrion class
class instruction:
    _instList = []
    _gfVarDic = {}
    _labelDic = {}
    def __init__(self, opcode, order, args):
        self._name: str = opcode
        self._order: int = order
        self._args: list = args
        self._instList.append(self)

    def getInstList(self):
        return self._instList
    
    def getName(self):
        return self._name
    
    def getOrder(self):
        return self._order

    def getArgs(self):
        return self._args

    def getGfVarList(self):
        return self._gfVarDic
    
    def addGfVar(self, var):
        self._gfVarDic.update({var: None})

    def getGfVar(self, var):
        try:
            return self._gfVarDic[var]
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)

    def setGfVar(self, var, type_, value):
        try:
            self._gfVarDic[var] = (type_, value)
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)

    def getLabelList(self):
        return self._labelDic

    def addLabel(self, label):
        self._labelDic.update({label: self._order})

    def getLabelPos(self, label):
        return self._labelDic[label]


# classy pro konkretni instrukce
class move(instruction):
    def __init__(self, order, args):
        super().__init__("MOVE", order, args)

class createframe(instruction):
    def __init__(self, order, args):
        super().__init__("CREATEFRAME", order, args)

class pushframe(instruction):
    def __init__(self, order, args):
        super().__init__("PUSHFRAME", order, args)

class popframe(instruction):
    def __init__(self, order, args):
        super().__init__("POPFRAME", order, args)

class defvar(instruction):  
    def __init__(self, order, args):
        super().__init__("DEFVAR", order, args)

    def execute(self):
        arg = super().getArgs()[0]
        var = arg.text
        varSplit = var.split("@")
        if varSplit[0] == "GF":
            super().addGfVar(varSplit[1])
        elif varSplit[0] == "LF":
            print("LF frame not implemented yet")
            exit(99)
        elif varSplit[0] == "TF":
            print("TF frame not implemented yet")
            exit(99)
        else:
            # canot happen
            sys.stderr.write("error: unknown frame")
            sys.exit(99)
        

class call(instruction):
    def __init__(self, order, args):
        super().__init__("CALL", order, args)

class return_(instruction):
    def __init__(self, order, args):
        super().__init__("RETURN", order, args)

class pushs(instruction):   
    def __init__(self, order, args):
        super().__init__("PUSHS", order, args)

class pops(instruction):  
    def __init__(self, order, args):
        super().__init__("POPS", order, args)

class add(instruction):  
    def __init__(self, order, args):
        super().__init__("ADD", order, args)

class sub(instruction):  
    def __init__(self, order, args):
        super().__init__("SUB", order, args)

class mul(instruction):  
    def __init__(self, order, args):
        super().__init__("MUL", order, args)

class idiv(instruction):  
    def __init__(self, order, args):
        super().__init__("IDIV", order, args)

class lt(instruction):
    def __init__(self, order, args):
        super().__init__("LT", order, args)

class gt(instruction):
    def __init__(self, order, args):
        super().__init__("GT", order, args)

class eq(instruction):
    def __init__(self, order, args):
        super().__init__("EQ", order, args)

class and_(instruction):
    def __init__(self, order, args):
        super().__init__("AND", order, args)

class or_(instruction):
    def __init__(self, order, args):
        super().__init__("OR", order, args)

class not_(instruction):
    def __init__(self, order, args):
        super().__init__("NOT", order, args)

class int2char(instruction):
    def __init__(self, order, args):
        super().__init__("INT2CHAR", order, args)

class stri2int(instruction):
    def __init__(self, order, args):
        super().__init__("STRI2INT", order, args)

class read(instruction):
    def __init__(self, order, args):
        super().__init__("READ", order, args)

class write(instruction):
    def __init__(self, order, args):
        super().__init__("WRITE", order, args)

class concat(instruction):
    def __init__(self, order, args):
        super().__init__("CONCAT", order, args)

class strlen(instruction):
    def __init__(self, order, args):
        super().__init__("STRLEN", order, args)

class getchar(instruction):
    def __init__(self, order, args):
        super().__init__("GETCHAR", order, args)

class setchar(instruction):
    def __init__(self, order, args):
        super().__init__("SETCHAR", order, args)

class type_(instruction):
    def __init__(self, order, args):
        super().__init__("TYPE", order, args)

class label(instruction):
    def __init__(self, order, args):
        super().__init__("LABEL", order, args)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg.text
        print("label: " + label)
        super().addLabel(label)

class jump(instruction):
    def __init__(self, order, args):
        super().__init__("JUMP", order, args)

class jumpifeq(instruction):
    def __init__(self, order, args):
        super().__init__("JUMPIFEQ", order, args)

class jumpifneq(instruction):
    def __init__(self, order, args):
        super().__init__("JUMPIFNEQ", order, args)

class exit_(instruction):
    def __init__(self, order, args):
        super().__init__("EXIT", order, args)

class dprint(instruction):
    def __init__(self, order, args):
        super().__init__("DPRINT", order, args)

class break_(instruction):
    def __init__(self, order, args):
        super().__init__("BREAK", order, args)

# tovarna na instrukce
class instrucionFactory:
    @classmethod
    def createInstruction(cls, opcode, order, args):
        if opcode == "MOVE":
            return move(order, args)
        elif opcode == "CREATEFRAME":
            return createframe(order, args)
        elif opcode == "PUSHFRAME":
            return pushframe(order, args)
        elif opcode == "POPFRAME":
            return popframe(order, args)
        elif opcode == "DEFVAR":
            return defvar(order, args)
        elif opcode == "CALL":
            return call(order, args)
        elif opcode == "RETURN":
            return return_(order, args)
        elif opcode == "PUSHS":
            return pushs(order, args)
        elif opcode == "POPS":
            return pops(order, args)
        elif opcode == "ADD":
            return add(order, args)
        elif opcode == "SUB":
            return sub(order, args)
        elif opcode == "MUL":
            return mul(order, args)
        elif opcode == "IDIV":
            return idiv(order, args)
        elif opcode == "LT":
            return lt(order, args)
        elif opcode == "GT":
            return gt(order, args)
        elif opcode == "EQ":
            return eq(order, args)
        elif opcode == "AND":
            return and_(order, args)
        elif opcode == "OR":
            return or_(order, args)
        elif opcode == "NOT":
            return not_(order, args)
        elif opcode == "INT2CHAR":
            return int2char(order, args)
        elif opcode == "STRI2INT":
            return stri2int(order, args)
        elif opcode == "READ":
            return read(order, args)
        elif opcode == "WRITE":
            return write(order, args)
        elif opcode == "CONCAT":
            return concat(order, args)
        elif opcode == "STRLEN":
            return strlen(order, args)
        elif opcode == "GETCHAR":
            return getchar(order, args)
        elif opcode == "SETCHAR":
            return setchar(order, args)
        elif opcode == "TYPE":
            return type_(order, args)
        elif opcode == "LABEL":
            return label(order, args)
        elif opcode == "JUMP":
            return jump(order, args)
        elif opcode == "JUMPIFEQ":
            return jumpifeq(order, args)
        elif opcode == "JUMPIFNEQ":
            return jumpifneq(order, args)
        elif opcode == "EXIT":
            return exit_(order, args)
        elif opcode == "DPRINT":
            return dprint(order, args)
        elif opcode == "BREAK":
            return break_(order, args)
        else:
            raise Exception("Unknown instruction")

if __name__ == "__main__":

    # zpracovani argumentu
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--source", help = "source XML file in IPPcode23")
    #argParser.add_argument("--input", help = "input file")
    args = argParser.parse_args()

    # TODO stdin kdyz nejsou zadany argumenty
    sourceFile = args.source
    #inputFile = args.input

    # xml parser
    try:
        tree = ET.parse(sourceFile)
        root = tree.getroot()
    except ET.ParseError as e:
        sys.stderr.write("Error: XML parse error: ", e)
        sys.exit(31)
    
    #TODO kontrola spravnosti xml

    # parsovani instrukci
    for i in root:
        print(i.tag, i.attrib)
        args = []
        for j in i:
            args.append(j)
            
        i1 = instrucionFactory.createInstruction(i.get("opcode"), i.get("order"), args)
        i1.execute()

    print(i1.getGfVarList())
    print(i1.getLabelList())
