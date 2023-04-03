# interpret.py 2. cast projektu do IPP
# interpretuje XML reprezentaci programu v IPPcode23 a generuje vystup
# @author: Jakub Lukas, xlukas18

import sys
import xml.etree.ElementTree as ET
import argparse

# instrucrion class
class instruction:
    _instList = []
    _stack = []
    _gfVarDic = {}
    _labelDic = {}
    def __init__(self, opcode, order, args):
        self._name: str = opcode
        self._order: int = order
        self._instList.append(self)
        self._args = []

        for i in args:
            arg = (i.attrib["type"], i.text)
            self._args.append(arg)

    def getInstList(self):
        return self._instList
    
    def getName(self):
        return self._name
    
    def getOrder(self):
        return self._order

    # returns touple (type, value)
    def getArgs(self):
        return self._args

    # variable
    def getGfVarList(self):
        return self._gfVarDic
    
    # gets touple (type, value) and if it exists, returns its value
    def getVarValue(self, var):
        try:
            varSplit = var.split("@")
            if varSplit[0] == "GF":
                return self.getGfVar(varSplit[1])
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
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)

    # gets touple (type, value) and stores it into GF, LF, TF variable dictionary
    def addVar(self, var):
        varSplit = var.split("@")
        if varSplit[0] == "GF":
            self.addGfVar(varSplit[1])
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

    def setVarValue(self, var, type_, value):
        varSplit = var.split("@")
        if varSplit[0] == "GF":
            self.setGfVar(varSplit[1], type_, value)
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

    # label
    def getLabelList(self):
        return self._labelDic

    def addLabel(self, label):
        self._labelDic.update({label: self._order})

    def getLabelPos(self, label):
        return self._labelDic[label]

    # stack
    def pushStack(self, symbol):
        self._stack.append(symbol)

    def popStack(self):
        if self.stackEmpty():
            sys.stderr.write("error(56): pops from empty stack but stack is empty")
            sys.exit(56)
        
        return self._stack.pop()
    
    def stackEmpty(self):
        return len(self._stack) == 0


# classy pro konkretni instrukce
class move(instruction):
    # move <var> <symb>, prenese hodnotu symb do var
    def __init__(self, order, args):
        super().__init__("MOVE", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]
        
        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        super().setVarValue(var[1], symb[0], symb[1])


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
        super().addVar(arg[1])
        

class call(instruction):
    def __init__(self, order, args):
        super().__init__("CALL", order, args)

class return_(instruction):
    def __init__(self, order, args):
        super().__init__("RETURN", order, args)

class pushs(instruction):   
    def __init__(self, order, args):
        super().__init__("PUSHS", order, args)

    def execute(self):
        arg = super().getArgs()[0]
        type_ = arg[0]
        value = arg[1]
        
        if type_ == "var":
            var = super().getVarValue(value)
            super().pushStack(var)
        else:
            super().pushStack((type_, value))


class pops(instruction):  
    def __init__(self, order, args):
        super().__init__("POPS", order, args)

    def execute(self):
        arg = super().getArgs()[0]
        var = arg[1]
        symbol = super().popStack()
        super().setVarValue(var, symbol[0], symbol[1])


class add(instruction):  
    def __init__(self, order, args):
        super().__init__("ADD", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "int" and symb2[0] == "int":
            super().setVarValue(var[1], "int", int(symb1[1]) + int(symb2[1]))
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)


class sub(instruction):  
    def __init__(self, order, args):
        super().__init__("SUB", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "int" and symb2[0] == "int":
            super().setVarValue(var[1], "int", int(symb1[1]) - int(symb2[1]))
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)


class mul(instruction):  
    def __init__(self, order, args):
        super().__init__("MUL", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "int" and symb2[0] == "int":
            super().setVarValue(var[1], "int", int(symb1[1]) * int(symb2[1]))
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)


class idiv(instruction):  
    def __init__(self, order, args):
        super().__init__("IDIV", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "int" and symb2[0] == "int":
            if symb2[1] == "0":
                sys.stderr.write("error(57): division by zero")
                sys.exit(57)
            super().setVarValue(var[1], "int", int(symb1[1]) // int(symb2[1]))
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class lt(instruction):
    def __init__(self, order, args):
        super().__init__("LT", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == symb2[0] and symb1[0] != "nil":
            super().setVarValue(var[1], "bool", symb1[1] < symb2[1])
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class gt(instruction):
    def __init__(self, order, args):
        super().__init__("GT", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == symb2[0] and symb1[0] != "nil":
            super().setVarValue(var[1], "bool", symb1[1] > symb2[1])
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class eq(instruction):
    def __init__(self, order, args):
        super().__init__("EQ", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == symb2[0]:
            if symb1[1] == symb2[1]:
                super().setVarValue(var[1], "bool", True)
            else:
                super().setVarValue(var[1], "bool", False)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class and_(instruction):
    def __init__(self, order, args):
        super().__init__("AND", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "bool" and symb2[0] == "bool":
            boolsym1 = False if symb1[1].lower() == "false" else True
            boolsym2 = False if symb2[1].lower() == "false" else True
            super().setVarValue(var[1], "bool", boolsym1 and boolsym2)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class or_(instruction):
    def __init__(self, order, args):
        super().__init__("OR", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "bool" and symb2[0] == "bool":
            boolsym1 = False if symb1[1].lower() == "false" else True
            boolsym2 = False if symb2[1].lower() == "false" else True
            super().setVarValue(var[1], "bool", boolsym1 or boolsym2)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class not_(instruction):
    def __init__(self, order, args):
        super().__init__("NOT", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        if symb[0] == "bool":
            boolsym = False if symb[1].lower() == "false" else True
            super().setVarValue(var[1], "bool", not boolsym)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class int2char(instruction):
    def __init__(self, order, args):
        super().__init__("INT2CHAR", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        if symb[0] == "int":
            try:
                super().setVarValue(var[1], "string", chr(int(symb[1])))
            except ValueError:
                sys.stderr.write("error(58): wrong value of operand")
                sys.exit(58)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class stri2int(instruction):
    def __init__(self, order, args):
        super().__init__("STRI2INT", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "string" and symb2[0] == "int":
            try:
                super().setVarValue(var[1], "int", ord(symb1[1][int(symb2[1])]))
            except IndexError:
                sys.stderr.write("error(58): wrong value of operand")
                sys.exit(58)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class read(instruction):
    def __init__(self, order, args):
        super().__init__("READ", order, args)

class write(instruction):
    def __init__(self, order, args):
        super().__init__("WRITE", order, args)

    def execute(self):
        symb = super().getArgs()[0]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])
        if symb[0] == "int" or symb[0] == "string":
            print(symb[1], end="")
        elif symb[0] == "bool":
            print(str(symb[1].lower()), end="")
        elif symb[0] == "nil":
            print("", end="")
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class concat(instruction):
    def __init__(self, order, args):
        super().__init__("CONCAT", order, args)

    def execute(self):
        # TODO escape sequences
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "string" and symb2[0] == "string":
            # debug print
            print("sym1:", symb1[1])
            print("sym2:", symb2[1])
            print("concat:", symb1[1] + symb2[1])
            super().setVarValue(var[1], "string", symb1[1] + symb2[1])
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class strlen(instruction):
    def __init__(self, order, args):
        super().__init__("STRLEN", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        if symb[0] == "string":
            super().setVarValue(var[1], "int", len(symb[1]))
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class getchar(instruction):
    def __init__(self, order, args):
        super().__init__("GETCHAR", order, args)
        
    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == "string" and symb2[0] == "int":
            try:
                super().setVarValue(var[1], "string", symb1[1][int(symb2[1])])
            except IndexError:
                sys.stderr.write("error(58): wrong value of operand")
                sys.exit(58)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class setchar(instruction):
    def __init__(self, order, args):
        super().__init__("SETCHAR", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        varVal = super().getVarValue(var[1])

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if varVal[0] == "string" and symb1[0] == "int" and symb2[0] == "string":
            try:
                newString = varVal[1][:int(symb1[1])] + symb2[1][0] + varVal[1][int(symb1[1]) + 1:]
                super().setVarValue(var[1], "string", newString)
            except IndexError:
                sys.stderr.write("error(58): wrong value of operand")
                sys.exit(58)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class type_(instruction):
    def __init__(self, order, args):
        super().__init__("TYPE", order, args)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        if symb is None:
            super().setVarValue(var[1], "string", "")
        else:
            super().setVarValue(var[1], "string", symb[0])

class label(instruction):
    def __init__(self, order, args):
        super().__init__("LABEL", order, args)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg[1]
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

    def execute(self):
        symb = super().getArgs()[0]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])
        if symb[0] == "int":
            if int(symb[1]) >= 0 and int(symb[1]) <= 49:
                sys.exit(int(symb[1]))
            else:
                sys.stderr.write("error(57): wrong value of operand")
                sys.exit(57)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class dprint(instruction):
    def __init__(self, order, args):
        super().__init__("DPRINT", order, args)

    def execute(self):
        symb = super().getArgs()[0]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])
        if symb[0] == "int" or symb[0] == "string":
            sys.stderr.write(symb[1], end="")
        elif symb[0] == "bool":
            sys.stderr.write(str(symb[1]).lower(), end="")
        elif symb[0] == "nil":
            sys.stderr.write("", end="")
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

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

    # debug print
    print(i1.getGfVarList())
    #print(i1.getLabelList())
