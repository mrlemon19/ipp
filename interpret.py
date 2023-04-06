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
    programCounter = 0
    _frameStack = []
    _temporaryFrame = None
    _callStack = []
    def __init__(self, opcode, order, args, inst):
        self._name: str = opcode
        self._order: int = order
        self._instList.append(inst) # inst is instruction object (move, createframe, ...)
        self._args = []

        for i in args:
            arg = (i.attrib["type"], i.text)
            self._args.append(arg)

        if self._name == "LABEL":
            self._labelDic.update({self._args[0][1]: self._order})

    def executeOnPC(self):
        print("Executing: ", self._instList[self.programCounter].getName())
        self._instList[self.programCounter].execute()
        self.programCounter += 1
        print("PC: ", self.programCounter)

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
                return self.getLocalFrame().getVarF(varSplit[1])
            elif varSplit[0] == "TF":
                return self.getTemporaryFrame().getVarF(varSplit[1])
            else:
                # canot happen
                sys.stderr.write("error: unknown frame")
                sys.exit(99)
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)

    # gets touple (type, value) and stores it into GF, LF, TF frame variable dictionary
    def addVar(self, var):
        varSplit = var.split("@")
        if varSplit[0] == "GF":
            self.addGfVar(varSplit[1])
        elif varSplit[0] == "LF":
            self.getLocalFrame().addVarF(varSplit[1])
        elif varSplit[0] == "TF":
            self.getTemporaryFrame().addVarF(varSplit[1])
        else:
            # canot happen
            sys.stderr.write("error: unknown frame")
            sys.exit(99)

    def setVarValue(self, var, type_, value):
        varSplit = var.split("@")
        if varSplit[0] == "GF":
            self.setGfVar(varSplit[1], type_, value)
        elif varSplit[0] == "LF":
            self.getLocalFrame().setVarF(varSplit[1], type_, value)
        elif varSplit[0] == "TF":
            self.getTemporaryFrame().setVarF(varSplit[1], type_, value)
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
    # used in jumps
    def getLabelList(self):
        return self._labelDic

    def addLabel(self, label):
        self._labelDic.update({label: self._order})

    def getLabelPos(self, label):
        try:
            return self._labelDic[label]
        except KeyError:
            sys.stderr.write("Label " + label + " not defined")
            sys.exit(52)
    
    # program counter
    def getPC(self):
        return self.programCounter
    
    def setPC(self, value):
        self.programCounter = value

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

    # frames
    def createFrame(self):
        self._temporaryFrame = frame()

    def pushFrame(self):
        if self._temporaryFrame == None:
            sys.stderr.write("error(55): no temporary frame")
            sys.exit(55)
        
        self._frameStack.append(self._temporaryFrame)
        self._temporaryFrame = None

    def popFrame(self):
        if len(self._frameStack) == 0:
            sys.stderr.write("error(55): no frame to pop")
            sys.exit(55)

        self._temporaryFrame = self._frameStack.pop()

    def getFrameStack(self):
        return self._frameStack
    
    def getTemporaryFrame(self):
        if self._temporaryFrame == None:
            sys.stderr.write("error(55): no temporary frame")
            sys.exit(55)

        return self._temporaryFrame
    
    def getLocalFrame(self):
        if len(self._frameStack) == 0:
            sys.stderr.write("error(55): accessing empty frame stack")
            sys.exit(55)
        
        return self._frameStack[-1]

    # call stack
    def pushCallStack(self, value):
        self._callStack.append(value)

    def popCallStack(self):
        if self.callStackEmpty():
            sys.stderr.write("error(56): pops from empty call stack but call stack is empty")
            sys.exit(56)
        
        return self._callStack.pop()
    
    def callStackEmpty(self):
        return len(self._callStack) == 0
    
    def getCallStack(self):
        return self._callStack

class frame:
    def __init__(self):
        self.varDic = {}
        instruction._temporaryFrame = self
        print("frame created")

    def addVarF(self, var):
        self.varDic.update({var: None})

    def setVarF(self, var, type_, value):
        try:
            correntValue = self.varDic[var] # only to check if it exists
            self.varDic[var] = (type_, value)
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)

    def getVarF(self, var):
        try:
            return self.varDic[var]
        except KeyError:
            sys.stderr.write("Variable " + var + " not defined")
            sys.exit(54)


# classy pro konkretni instrukce
class move(instruction):
    # move <var> <symb>, prenese hodnotu symb do var
    def __init__(self, order, args):
        super().__init__("MOVE", order, args, self)

    def execute(self):
        var = super().getArgs()[0]
        symb = super().getArgs()[1]
        
        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        super().setVarValue(var[1], symb[0], symb[1])


class createframe(instruction):
    def __init__(self, order, args):
        super().__init__("CREATEFRAME", order, args, self)

    def execute(self):
        super().createFrame()

class pushframe(instruction):
    def __init__(self, order, args):
        super().__init__("PUSHFRAME", order, args, self)

    def execute(self):
        super().pushFrame()

class popframe(instruction):
    def __init__(self, order, args):
        super().__init__("POPFRAME", order, args, self)

    def execute(self):
        super().popFrame()

class defvar(instruction):
    def __init__(self, order, args):
        super().__init__("DEFVAR", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        super().addVar(arg[1])
        

class call(instruction):
    def __init__(self, order, args):
        super().__init__("CALL", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg[1]
        super().pushCallStack(super().getPC() + 1)
        super().setPC(int(super().getLabelPos(label)) - 1)

class return_(instruction):
    def __init__(self, order, args):
        super().__init__("RETURN", order, args, self)

    def execute(self):
        super().setPC(super().popCallStack())

class pushs(instruction):   
    def __init__(self, order, args):
        super().__init__("PUSHS", order, args, self)

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
        super().__init__("POPS", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        var = arg[1]
        symbol = super().popStack()
        super().setVarValue(var, symbol[0], symbol[1])


class add(instruction):  
    def __init__(self, order, args):
        super().__init__("ADD", order, args, self)

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
        super().__init__("SUB", order, args, self)

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
        super().__init__("MUL", order, args, self)

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
        super().__init__("IDIV", order, args, self)

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
        super().__init__("LT", order, args, self)

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
        super().__init__("GT", order, args, self)

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
        super().__init__("EQ", order, args, self)

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
        super().__init__("AND", order, args, self)

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
        super().__init__("OR", order, args, self)

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
        super().__init__("NOT", order, args, self)

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
        super().__init__("INT2CHAR", order, args, self)

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
        super().__init__("STRI2INT", order, args, self)

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
        super().__init__("READ", order, args, self)

    def execute(self):
        var = super().getArgs()[0]
        type_ = super().getArgs()[1]

        try:
            value = input()
        except EOFError:
            value = ""
            type_ = "nil"

        if type_ == "int":
            try:
                value = int(value)
            except ValueError:
                value = ""
                type_ = "nil"

        elif type_ == "bool":
            if value.lower() == "true":
                value = True
            else:
                value = False
        elif type_ == "string":
            value = str(value)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

        super().setVarValue(var[1], type_, value)

class write(instruction):
    def __init__(self, order, args):
        super().__init__("WRITE", order, args, self)

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
        super().__init__("CONCAT", order, args, self)

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
        super().__init__("STRLEN", order, args, self)

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
        super().__init__("GETCHAR", order, args, self)
        
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
        super().__init__("SETCHAR", order, args, self)

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
        super().__init__("TYPE", order, args, self)

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
        super().__init__("LABEL", order, args, self)

    def execute(self):
        pass

class jump(instruction):
    def __init__(self, order, args):
        super().__init__("JUMP", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg[1]

        #instruction.programCounter = super().getLabelPos(label)
        super().setPC(int(super().getLabelPos(label)) - 1)
        print("PC from jump: ", instruction.programCounter)
        print("setting PC to:", super().getLabelPos(label))

class jumpifeq(instruction):
    def __init__(self, order, args):
        super().__init__("JUMPIFEQ", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg[1]

        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == symb2[0]:
            if symb1[0] == "nil":
                #instruction.programCounter = super().getLabelPos(label)
                super().setPC(int(super().getLabelPos(label)) - 1)
            elif symb1[0] == "bool":
                if symb1[1] == symb2[1]:
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
            elif symb1[0] == "int":
                if int(symb1[1]) == int(symb2[1]):
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
            elif symb1[0] == "string":
                if symb1[1] == symb2[1]:
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class jumpifneq(instruction):
    def __init__(self, order, args):
        super().__init__("JUMPIFNEQ", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        label = arg[1]

        symb1 = super().getArgs()[1]
        symb2 = super().getArgs()[2]

        if symb1[0] == "var":
            symb1 = super().getVarValue(symb1[1])

        if symb2[0] == "var":
            symb2 = super().getVarValue(symb2[1])

        if symb1[0] == symb2[0]:
            if symb1[0] == "nil":
                #instruction.programCounter = super().getLabelPos(label)
                super().setPC(int(super().getLabelPos(label)) - 1)
            elif symb1[0] == "bool":
                if symb1[1] != symb2[1]:
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
            elif symb1[0] == "int":
                if int(symb1[1]) != int(symb2[1]):
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
                    print("jumpifneq: ", symb1[1], " != ", symb2[1], "going to jump")
            elif symb1[0] == "string":
                if symb1[1] != symb2[1]:
                    #instruction.programCounter = super().getLabelPos(label)
                    super().setPC(int(super().getLabelPos(label)) - 1)
            else:
                print("jumpifneq: ", symb1[1], " == ", symb2[1], "not going to jump")
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class exit_(instruction):
    def __init__(self, order, args):
        super().__init__("EXIT", order, args, self)

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
        super().__init__("DPRINT", order, args, self)

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
        super().__init__("BREAK", order, args, self)

    def execute(self):
        # vypise stav interpretu (promene, ramce, ...)
        print("break not implemented yet :(")

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
    argParser.add_argument("--input", help = "input file")
    args = argParser.parse_args()

    # TODO stdin kdyz nejsou zadany argumenty
    sourceFile = args.source
    inputFile = args.input

    # input file check
    if (sourceFile == None and inputFile == None):
        sys.stderr.write("Error: No input and source file")
        sys.exit(10)

    if (sourceFile == None):
        sourceFile = sys.stdin

    if (inputFile == None):
        inputFile = sys.stdin

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

    # spusteni instrukci
    lenOfInstList = len(super(type(i1), i1).getInstList())
    print("len of label list:", lenOfInstList)
    while super(type(i1), i1).getPC() != lenOfInstList:
        super(type(i1), i1).executeOnPC()

    # debug print
    print("frame stack: ", super(type(i1), i1).getFrameStack())
    #print(i1.getGfVarList())
    #print(i1.getLabelList())
