# interpret.py 2. cast projektu do IPP
# interpretuje XML reprezentaci programu v IPPcode23 a generuje vystup
# @author: Jakub Lukas, xlukas18

import sys
import xml.etree.ElementTree as ET
import argparse

# trida instrukce
class instruction:
    _instList = []      # seznam nactenych instrukci
    _stack = []         # zasobnik na data
    _gfVarDic = {}      # slovnik promenych globalniho ramce {[name] = [type, value]}
    _labelDic = {}      # slovnik labelu {[name] = [position in instList]}
    programCounter = 0
    _frameStack = []    # zasobnik ramcu
    _temporaryFrame = None
    _callStack = []     # zasobnik volani, obsahuje pozice instrukci v instList
    instructionCounter = 0  # pocitadlo vykonanych instrukci

    def __init__(self, opcode, order, args, inst):
        self._name: str = opcode
        self._order: int = order
        self._instList.append(inst) # inst je objekt co zavolal tuto metodu (move, createframe, ...)
        self._args = []

        # parsovani argumentu
        for i in args:
            arg = (i.attrib["type"], i.text)
            self._args.append(arg)

    def __str__(self):
        return self._name + " " + str(self._args)

    def run(self):
        # zavola postupne metodu execute na vsech instrukcich z instList
        while self.programCounter < len(self._instList):
            # pushframe
            if self._instList[self.programCounter].getName() == "PUSHFRAME":
                self.pushFrame()

            # popframe
            if self._instList[self.programCounter].getName() == "POPFRAME":
                self.popFrame()

            # createframe
            if self._instList[self.programCounter].getName() == "CREATEFRAME":
                self.createFrame()

            # instrukce provadejici skok
            if self._instList[self.programCounter].getName() in ["JUMP", "JUMPIFEQ", "JUMPIFNEQ", "CALL", "RETURN"]:
                # pokud metoda execute u provadene skokove instrukce vraci true, tak se provede skok
                if self._instList[self.programCounter].execute():
                    # pro instrukce CALL a RETURN se krome skoku provede zmena callStacku
                    if self._instList[self.programCounter].getName() == "RETURN":
                        self.setPC(int(self.popCallStack()))
                    elif self._instList[self.programCounter].getName() == "CALL":
                        self.pushCallStack(self.programCounter + 1)
                        self.setPC(int(self.getLabelPos(self._instList[self.programCounter].getArgs()[0][1])))
                    else:
                        # bete instrukci na PC a ziska pozici labelu, pak nastavi program counter na tu pozici
                        self.setPC(int(self.getLabelPos(self._instList[self.programCounter].getArgs()[0][1])))
                else:
                    self.programCounter += 1
            else:
                self.executeOnPC()
                self.programCounter += 1

    def executeOnPC(self):
        # provede instrukci na aktualni pozici program counteru
        self._instList[self.programCounter].execute()
        self.instructionCounter += 1

    def sortInstList(self):
        # seradi seznam instrukci podle poradi order
        self._instList.sort(key=lambda x: x.getOrder())
        # kontrola duplicity orderu a zda order neni zaporny
        for i in range(len(self._instList)):
            if self._instList[i].getOrder() <= 0:
                sys.stderr.write("error(32): zero on negative order")
                sys.exit(32)
            
            if i + 1 < len(self._instList) and self._instList[i].getOrder() == self._instList[i + 1].getOrder():
                sys.stderr.write("error(32): duplicite order")
                sys.exit(32)

    def structureLabel(self):
        # projde seznam instrukci a vytvori slovnik labelu
        for i in range(len(self._instList)):
            if self._instList[i].getName() == "LABEL":
                if self._instList[i].getArgs()[0][1] in self._labelDic:
                    sys.stderr.write("error(52): duplicite label")
                    sys.exit(52)
                self._labelDic.update({self._instList[i].getArgs()[0][1]: i})

    def getInstList(self):
        return self._instList
    
    def getName(self):
        return self._name
    
    def getOrder(self):
        try:
            return int(self._order)
        except:
            sys.stderr.write("error(32): order is missing or is not correct")
            sys.exit(32)

    # returns touple (type, value)
    def getArgs(self):
        return self._args

    # variable
    def getGfVarList(self):
        return self._gfVarDic
    
    # podle ramce a jmena promene vraci touple (type, value)
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

    # vytvori promennou v danem ramci
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

    # nastavi hodnotu promenne v danem ramci
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

    # vraci touple (type, value) podle jmena promene z globalniho ramce
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
            sys.stderr.write("error(54): Variable " + var + " not defined")
            sys.exit(54)

    # label
    def getLabelList(self):
        return self._labelDic

    def getLabelPos(self, label):
        try:
            return self._labelDic[label]
        except KeyError:
            sys.stderr.write("error(52): Label " + label + " not defined")
            sys.exit(52)
    
    # program counter
    def getPC(self):
        return self.programCounter
    
    def setPC(self, value):
        self.programCounter = value

    # datovy zasoobnik
    def pushStack(self, symbol):
        self._stack.append(symbol)

    def popStack(self):
        if self.stackEmpty():
            sys.stderr.write("error(56): pops from empty stack but stack is empty")
            sys.exit(56)
        
        return self._stack.pop()
    
    def stackEmpty(self):
        return len(self._stack) == 0

    # ramce
    def createFrame(self):
        self._temporaryFrame = frame()

    def pushFrame(self):
        if self._temporaryFrame == None:
            sys.stderr.write("error(55): no frame to push")
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
    
    def getInstructionCounter(self):
        return self.instructionCounter

# trida pro ramec
class frame:
    # vlastni slovnik pro ulozeni promennych a metody pro praci s nimi

    def __init__(self):
        self.varDic = {}
        instruction._temporaryFrame = self

    def __str__(self):
        return str(self.varDic)

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
    # createframe, vytvori novy prazdny ramec
    def __init__(self, order, args):
        super().__init__("CREATEFRAME", order, args, self)

    def execute(self):
        super().createFrame()

class pushframe(instruction):
    # pushframe, vlozi TF do zasobniku ramcu a udela z nej LF
    def __init__(self, order, args):
        super().__init__("PUSHFRAME", order, args, self)

    def execute(self):
        super().pushFrame()

class popframe(instruction):
    # popframe, vlozi LF z vrcholu zasobniku ramcu do TF
    def __init__(self, order, args):
        super().__init__("POPFRAME", order, args, self)

    def execute(self):
        super().popFrame()

class defvar(instruction):
    # defvar <var>, vytvori promennou var
    def __init__(self, order, args):
        super().__init__("DEFVAR", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        super().addVar(arg[1])
        
class call(instruction):
    # call <label>, skoci na instrukci s danym label
    def __init__(self, order, args):
        super().__init__("CALL", order, args, self)

    def execute(self):
        return True

class return_(instruction):
    # return, skoci na instrukci na vrcholu zasobniku volani
    def __init__(self, order, args):
        super().__init__("RETURN", order, args, self)

    def execute(self):
        if super().callStackEmpty():
            sys.stderr.write("error(56): pops from empty call stack but call stack is empty")
            sys.exit(56)
        
        return True

class pushs(instruction):
    # pushs <symb>, vlozi hodnotu symb na vrchol datoveho zasobniku
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
    # pops <var>, vyjme hodnotu z vrcholu datoveho zasobniku a ulozi ji do var
    def __init__(self, order, args):
        super().__init__("POPS", order, args, self)

    def execute(self):
        arg = super().getArgs()[0]
        var = arg[1]
        symbol = super().popStack()
        super().setVarValue(var, symbol[0], symbol[1])

class add(instruction):
    # add <var> <symb1> <symb2>, secte symb1 a symb2 a ulozi vysledek do var
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
            try:
                super().setVarValue(var[1], "int", int(symb1[1]) + int(symb2[1]))
            except:
                sys.stderr.write("error(32): incorrect int value")
                sys.exit(32)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class sub(instruction):
    # sub <var> <symb1> <symb2>, odecte symb2 od symb1 a ulozi vysledek do var
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
            try:
                super().setVarValue(var[1], "int", int(symb1[1]) - int(symb2[1]))
            except:
                sys.stderr.write("error(32): incorrect int value")
                sys.exit(32)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class mul(instruction):
    # mul <var> <symb1> <symb2>, vynasobi symb1 a symb2 a ulozi vysledek do var
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
            try:
                super().setVarValue(var[1], "int", int(symb1[1]) * int(symb2[1]))
            except:
                sys.stderr.write("error(32): incorrect int value")
                sys.exit(32)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class idiv(instruction):
    # idiv <var> <symb1> <symb2>, vydeli symb1 a symb2 a ulozi vysledek do var
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
            try:
                super().setVarValue(var[1], "int", int(symb1[1]) // int(symb2[1]))
            except:
                sys.stderr.write("error(32): incorrect int value")
                sys.exit(32)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class lt(instruction):
    # lt <var> <symb1> <symb2>, porovna symb1 a symb2 a ulozi do var true, pokud je symb1 mensi nez symb2, jinak false
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
    # gt <var> <symb1> <symb2>, porovna symb1 a symb2 a ulozi do var true, pokud je symb1 vetsi nez symb2, jinak false
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
    # eq <var> <symb1> <symb2>, porovna symb1 a symb2 a ulozi do var true, pokud jsou symb1 a symb2 stejne, jinak false
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
    # and <var> <symb1> <symb2>, provede logickou operaci and nad symb1 a symb2 a ulozi vysledek do var
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
    # or <var> <symb1> <symb2>, provede logickou operaci or nad symb1 a symb2 a ulozi vysledek do var
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
    # not <var> <symb>, zneguje symb a ulozi jeho hodnotu do var
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
    # int2char <var> <symb>, vezme symbol co je int a prevede ho do odpovidajiciho ascii znaku
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
    # str2int <var> <symb1> <symb2>, TODO
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
    # read <var> <type>, nacte ze vstupu symbol daneho typu
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

        if type_[1] == "int":
            try:
                value = int(value)
            except ValueError:
                value = ""
                type_ = "nil"

        elif type_[1] == "bool":
            if value.lower() == "true":
                value = True
            else:
                value = False
        elif type_[1] == "string":
            value = str(value)
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

        #print("value from read: ", value, "type: ", type_)
        super().setVarValue(var[1], type_[1], value)

class write(instruction):
    # write <symb>, vypise na standartni vystup symbol v symb
    def __init__(self, order, args):
        super().__init__("WRITE", order, args, self)

    def execute(self):
        symb = super().getArgs()[0]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])

        if symb is None:
            print("", end="")
            return

        elif symb[0] == "int":
            print(symb[1], end="")
        elif symb[0] == "string":
            s = symb[1]
            i = 0
            while i < len(s):
                if s[i] == "\\" and i < len(s)-3 and s[i+1].isdigit() and s[i+2].isdigit() and s[i+3].isdigit():
                    num = int(s[i+1:i+4])
                    if (num >= 0 and num <= 32) or num == 35 or num == 92:
                        s = s[:i] + chr(num) + s[i+4:]
                        i += 1
                i += 1

            print(s, end="")

        elif symb[0] == "bool":
            print(str(symb[1]).lower(), end="")
        elif symb[0] == "nil":
            print("", end="")
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class concat(instruction):
    # concat <var> <symb1> <symb2>, zkonkatenuje retezce v symb1 a symb2 a ulozi vysledek do var
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
            super().setVarValue(var[1], "string", symb1[1] + symb2[1])
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class strlen(instruction):
    # strlen <var> <symb>, do var ulozi delku retezce v symb
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
    # getchar <var> <symb1> <symb2>, do var ulozi znak na indexu symb2 v retezci symb1
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
    # setchar <var> <symb1> <symb2>, v retezci v var na indexu symb1 ulozi znak symb2
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
    # type <var> <symb>, do var ulozi typ symb
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
    # label <label>, definuje navesti
    def __init__(self, order, args):
        super().__init__("LABEL", order, args, self)

    def execute(self):
        pass

class jump(instruction):
    # jump <label>, provede skok na navesti
    def __init__(self, order, args):
        super().__init__("JUMP", order, args, self)

    def execute(self):
        return True

class jumpifeq(instruction):
    # jumpifeq <label> <symb1> <symb2>, provede skok na navesti, pokud jsou symb1 a symb2 stejne
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

        goingtoJump = False

        if symb1[0] == symb2[0]:
            if symb1[0] == "nil":
                goingtoJump = True
            elif symb1[0] == "bool":
                if symb1[1] == symb2[1]:
                    goingtoJump = True
            elif symb1[0] == "int":
                if int(symb1[1]) == int(symb2[1]):
                    goingtoJump = True
            elif symb1[0] == "string":
                if symb1[1] == symb2[1]:
                    goingtoJump = True
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

        return goingtoJump

class jumpifneq(instruction):
    # jumpifneq <label> <symb1> <symb2>, provede skok na navesti, pokud nejsou symb1 a symb2 stejne
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

        goingtoJump = False

        if symb1[0] == symb2[0]:
            if symb1[0] == "nil":
                goingtoJump = True
            elif symb1[0] == "bool":
                if symb1[1] != symb2[1]:
                    goingtoJump = True
            elif symb1[0] == "int":
                if int(symb1[1]) != int(symb2[1]):
                    goingtoJump = True
            elif symb1[0] == "string":
                if symb1[1] != symb2[1]:
                    goingtoJump = True

        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

        return goingtoJump

class exit_(instruction):
    # exit <symb>, ukonci program s navratovou hodnotou symb
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
    # dprint <symb>, vypise na stderr hodnotu symb
    def __init__(self, order, args):
        super().__init__("DPRINT", order, args, self)

    def execute(self):
        symb = super().getArgs()[0]

        if symb[0] == "var":
            symb = super().getVarValue(symb[1])
        if symb[0] == "int" or symb[0] == "string":
            sys.stderr.write(symb[1])
        elif symb[0] == "bool":
            sys.stderr.write(str(symb[1]).lower())
        elif symb[0] == "nil":
            sys.stderr.write("")
        else:
            sys.stderr.write("error(53): wrong type of operands")
            sys.exit(53)

class break_(instruction):
    # break, vypise stav interpretu
    def __init__(self, order, args):
        super().__init__("BREAK", order, args, self)

    def execute(self):
        # vypise stav interpretu (promene, ramce, ...)
        breakOrder = str(super().getOrder())
        tempFrame = str(super().getTempFrame())
        localFrame = str(super().getLocalFrame())
        instructionCounter = str(super().getInstructionCounter())
        globalFrame = str(super().getGfVarList())
        breakMessage = '''Breakpoint at order: {breakOrder}
        temporary frame: {tempFrame}
        global frame: {globalFrame}
        current local frame: {localFrame}
        number of executed instructions: {instructionCounter}
        '''
        sys.stderr.write(breakMessage)

# tovarna na instrukce
class instrucionFactory:
    @classmethod
    def createInstruction(cls, opcode, order, args):

        # kontrola spravneho opcode
        try:
            opcode = opcode.upper()
        except:
            sys.stderr.write("error(32): missing or incorrect opcode")
            sys.exit(32)

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
            sys.stderr.write("error(32): unknown instruction opcode")
            sys.exit(32)

if __name__ == "__main__":

    # zpracovani argumentu
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--source", help = "source XML file in IPPcode23")
    argParser.add_argument("--input", help = "input file")
    args = argParser.parse_args()

    sourceFile = args.source
    inputFile = args.input

    # input file check
    if (sourceFile == None and inputFile == None):
        sys.stderr.write("Error: No input and source file")
        sys.exit(10)

    if (sourceFile == None):
        sourceFile = input()

    if (inputFile == None):
        inputFile = sys.stdin
    else:
        try:
            inputFile = open(inputFile, "r")
            sys.stdin = inputFile
        except IOError as e:
            sys.stderr.write("Error: Input file error: ", e)
            sys.exit(11)


    # xml parser
    try:
        tree = ET.parse(sourceFile)
        root = tree.getroot()
    except:
        sys.stderr.write("error: XML parse error")
        sys.exit(31)
    
    # kontrola hlavicky
    if root.attrib['language'].upper() != "IPPCODE23":
        sys.stderr.write("error(32): incorrect language")
        exit(32)

    # parsovani instrukci
    for i in root:
        # kontrola tagu instrukce
        if i.tag != "instruction":
            sys.stderr.write("error(32): incorrect instruction tag")
            sys.exit(32)

        args = []
        for j in i:
            # kontrola tagu argumentu
            if j.tag == "arg1" or j.tag == "arg2" or j.tag == "arg3":
                args.append(j)
            else:
                sys.stderr.write("error(32): incorrect argument tag")
                sys.exit(32)
            
        # trideni argumentu
        args.sort(key = lambda x: int(x.tag[-1]))
        # vytvoreni instance instrukce
        i1 = instrucionFactory.createInstruction(i.get("opcode"), i.get("order"), args)

    super(type(i1), i1).sortInstList()
    super(type(i1), i1).structureLabel()
    super(type(i1), i1).run()
