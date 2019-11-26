# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 18:48:44 2019

@author: akash
"""

from utils import readFiles, instParsing, functionalUnits
from tabulate import tabulate


class Instructions:
    def __init__(self, inst):
        self.iname = inst[0]
        self.op1 = 0
        self.op2 = 0
        self.op3 = 0
        self.fetch = 0
        self.decode = 0
        self.exec = 0
        self.write = 0
        self.raw = "N"
        self.war = "N"
        self.waw = "N"
        self.struct = "N"
        self.status = 0
        self.intCount = 0
        self.memCount = 0
        self.functionalUnit = None
        self.execCycle = 0
        self.finalOutput = []

        if len(inst) == 3:
            self.op1 = inst[1]
            self.op2 = inst[2]

        if len(inst) == 4:
            self.op1 = inst[1]
            self.op2 = inst[2]
            self.op3 = inst[3]

        if self.iname == "L.D":
            self.intCount = 1
            self.functionalUnit = "Main memory"
            self.memCount = int(functional_units[self.functionalUnit])

        if self.iname == "ADD.D" or self.iname == "SUB.D":
            self.functionalUnit = "FP adder"
            self.execCycle = int(functional_units[self.functionalUnit][0])

        if self.iname == "MUL.D":
            self.functionalUnit = "FP Multiplier"
            self.execCycle = int(functional_units[self.functionalUnit][0])

        if self.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
            self.intCount = 1
            self.memCount = 1
class Pipeline:
    def __init__(self, instructions):

        fpRegistersList = []
        fpInstructionList = []
        instObjs = []
        for i in instructions:
            print(i)
            instObjs.append(Instructions(i))

        # Iterating Over the instruction objects
        processor = Processor()
        x = 70
        cycle = 0
        newLoop = False
        while x > 0:

            cycle += 1
            if cycle == 35:
                print("X", vars(processor))
            for inst in instObjs:
                if inst.status != 5:
                    if inst.status == 0:
                        if processor.fBusy == "No":
                            processor.fBusy = "Yes"
                            #fpRegistersList.append(inst.op1)
                            inst.fetch = cycle
                            inst.status = 1




                    elif inst.status == 1:
                        print("XXX",inst.iname, cycle)
                        if inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname != "HLT":
                            processor.fBusy = "No"
                            inst.status = 5
                            continue
                        elif inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname == "HLT":
                            print("IDHAR AARA HAI")
                            instObjs[instObjs.index(inst)-1].decode = cycle-1
                            processor.fBusy = "No"

                            inst.status = 5

                        if inst.op1 not in fpRegistersList and inst.iname != "BNE" and inst.iname != "HLT":
                            fpRegistersList.append(inst.op1)
                            fpInstructionList.append(instObjs.index(inst))
                        if inst.op1 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op1)] != instObjs.index(inst) and inst.iname != "BNE":
                            inst.waw = "Y"
                            continue
                        if processor.dBusy == "No" and inst.iname != "BNE" and inst.iname != "HLT":
                            if cycle == 35:
                                print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
                            if inst.op2 not in fpRegistersList and inst.op3 not in fpRegistersList:
                                processor.dBusy = "Yes"
                                print("This is making DBUSyXYZ", cycle, inst.iname)
                                processor.fBusy = "No"

                                inst.decode = cycle
                                inst.status = 2
                            # DO IT FOR OP3 AS WELL
                            elif (inst.op2 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op2)] == instObjs.index(inst))\
                                or (inst.op3 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op3)] == instObjs.index(inst)):

                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2
                            else:
                                print(fpRegistersList)
                                print("SSSS", cycle)
                                inst.raw = "Y"
                        elif inst.iname == "BNE":
                            if inst.op1 in fpRegistersList and not fpInstructionList[fpRegistersList.index(inst.op1)] == instObjs.index(inst):
                                inst.raw = "Y"

                            else:
                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2

                                if regs[int(inst.op1[1:])] != regs[int(inst.op2[1:])]:

                                    for p in loop:
                                        if p[0] == inst.op3:
                                            z = p[1]

                                    newInstructions = instructions[z:]
                                    newInstructionsObjs = []
                                    for n in newInstructions:
                                        newInstructionsObjs.append(Instructions(n))
                                    newLoop = True
                                    processor.dBusy = "No"
                                    inst.status = 5
                                    break






                    elif inst.status == 2:
                        if inst.iname == "L.D":
                            if processor.intBusy == "No" and inst.intCount == 1:
                                processor.intBusy = "Yes"
                                inst.intCount -= 1
                                processor.dBusy = "No"

                            # elif processor.memBusy == "No":
                            #     if inst.memCount == 2:
                            #         inst.memCount = 1
                            #         processor.intBusy = "No"
                            #         processor.memBusy = "Yes"
                            # elif processor.memBusy == "Yes":
                            #     if inst.memCount == 2:
                            #         inst.struct = "Y"
                            #     if inst.memCount == 1:
                            #         inst.memCount = 0
                            #         inst.exec = cycle
                            #
                            #         inst.status = 3

                            else:
                                print(cycle, processor.memBusy)
                                if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                    if processor.memBusy[0] == "No":
                                        processor.intBusy = "No"
                                    processor.memBusy[0] = "Yes"
                                    processor.memBusy[1] = instObjs.index(inst)
                                    inst.memCount -= 1

                                    if(inst.memCount == 0):
                                        inst.exec = cycle
                                        inst.status = 3

                                else:
                                 inst.struct = "Y"



                        ## YET TO ADD THE HAZARDS BOTH STRUCT  and make the pipelined auto instead of manual
                        elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                            pipelined = functional_units[inst.functionalUnit][1]
                            if pipelined == "yes":
                                if processor.addBusy == "No":
                                    processor.dBusy = "No"
                                    processor.addBusy = "Yes"
                                else:
                                    processor.dBusy = "No"
                                inst.execCycle -= 1
                                if inst.execCycle == 0:
                                    inst.exec = cycle
                                    inst.status = 3
                            #MAKE THE PIPELINED WORK FOR THIS AS WELL
                            else:
                                if processor.addBusy == "No":
                                    processor.dBusy = "No"
                                    processor.addBusy = "Yes"
                                    inst.execCycle -= 1
                                    if inst.execCycle == 0:
                                        inst.exec = cycle
                                        inst.status = 3

                                elif processor.addBusy == "Yes":
                                    processor.dBusy = "No"
                                    if inst.execCycle != functional_units[inst.functionalUnit][0]:
                                        inst.execCycle -= 1
                                        if inst.execCycle == 0:
                                            inst.exec = cycle
                                            inst.status = 3

                        elif inst.iname == "MUL.D":
                            pipelined = functional_units[inst.functionalUnit][1]
                            if pipelined == "yes":
                                if processor.mulBusy == "No":

                                    processor.dBusy = "No"
                                    processor.mulBusy = "Yes"
                                inst.execCycle -= 1
                                if inst.execCycle == 0:
                                    inst.exec = cycle
                                    inst.status = 3
                            else:
                                if processor.mulBusy == "No":
                                    processor.dBusy = "No"
                                    processor.mulBusy = "Yes"
                                    inst.execCycle -= 1
                                    if inst.execCycle == 0:
                                        inst.exec = cycle
                                        inst.status = 3
                                elif processor.mulBusy == "Yes":
                                    if inst.execCycle != functional_units[inst.functionalUnit][0]:
                                        inst.execCycle -= 1
                                        if inst.execCycle == 0:
                                            inst.exec = cycle
                                            inst.status = 3
                        elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                            if processor.intBusy == "No" and inst.intCount == 1:
                                processor.intBusy = "Yes"
                                inst.intCount -= 1
                                processor.dBusy = "No"

                            elif processor.memBusy[0] == "No":
                                if inst.memCount == 1:
                                    inst.memCount = 0
                                    processor.intBusy = "No"
                                    processor.memBusy[0] = "No"
                                    processor.memBusy[1] = None

                                inst.exec = cycle
                                inst.status = 3




                    elif inst.status == 3:

                        if processor.wbBusy[0] == "No":
                            if inst.iname == "L.D":
                                print("CC", cycle)
                                processor.memBusy[0] = "No"
                                processor.memBusy[1] = None


                            elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                                processor.addBusy = "No"

                            elif inst.iname == "MUL.D":
                                processor.mulBusy = "No"

                            elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                #processor.intMemBusy = "No"
                                self.calculate(inst.iname, inst.op1, inst.op2, inst.op3)
                            inst.status = 4
                            inst.write = cycle
                            print(fpRegistersList)
                            index1 = fpRegistersList.index(inst.op1)
                            fpRegistersList.remove(fpRegistersList[index1])
                            fpInstructionList.remove(fpInstructionList[index1])
                            processor.wbBusy = ["Yes", cycle]

                        else:

                            if cycle == processor.wbBusy[1]:
                                inst.struct = "Y"
                            if cycle > processor.wbBusy[1]:
                                inst.write = cycle
                                if inst.iname in ["ADD.D", "SUB.D"]:
                                    processor.addBusy = "No"
                                    index1 = fpRegistersList.index(inst.op1)
                                    fpRegistersList.remove(fpRegistersList[index1])
                                    fpInstructionList.remove(fpInstructionList[index1])
                                if inst.iname == "MUL.D":
                                    processor.mulBusy = "No"
                                    index1 = fpRegistersList.index(inst.op1)
                                    fpRegistersList.remove(fpRegistersList[index1])
                                    fpInstructionList.remove(fpInstructionList[index1])
                                processor.wbBusy = ["Yes", cycle]
                                inst.status = 4
                    elif inst.status == 4:
                        if cycle > processor.wbBusy[1]:
                            processor.wbBusy = ["No", 0]
                        inst.status = 5

            if newLoop:
                processor.fBusy = "No"
                processor.dBusy = "No"
                processor.wbBusy = ["No", 0]
                instObjs.pop()
                instObjs += newInstructionsObjs
                newLoop = False
                cycle -= 1
            x -= 1

        for i in instObjs:
            print(i.iname, i.fetch, i.decode, i.exec, i.write, i.raw, i.struct)

        print(regs)

        # for i in range(len(instructions)):
        #     instObjs[i].finalOutput.append(" ".join(instructions[i]))
        for inst in instObjs:
            inst.finalOutput.append(inst.iname+","+str(inst.op1)+","+str(inst.op2)+","+str(inst.op3))
            inst.finalOutput.append(inst.fetch)
            inst.finalOutput.append(inst.decode)
            inst.finalOutput.append(inst.exec)
            inst.finalOutput.append(inst.write)
            inst.finalOutput.append(inst.raw)
            inst.finalOutput.append(inst.war)
            inst.finalOutput.append(inst.waw)
            inst.finalOutput.append(inst.struct)
        table = []
        headers = ["Instruction", "FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct"]
        table.append(headers)
        for inst in instObjs:
            table.append(inst.finalOutput)
        print(tabulate(table))

        f = open('result.txt', 'w')
        f.write(tabulate(table))
        f.close()

    def calculate(self, inst, op1, op2, op3):
        if inst == "DADDI":
            regs[int(op1[1:])] = regs[int(op2[1:])] + int(op3)
        elif inst == "DSUB":
            regs[int(op1[1:])] = regs[int(op2[1:])] - regs[int(op3[1:])]

class Processor:
    def __init__(self):
        self.fBusy = "No"
        self.dBusy = "No"
        self.wbBusy = ["No", 0]
        self.intBusy = "No"
        self.memBusy = ["No", None]
        self.addBusy = "No"
        self.mulBusy = "No"
        self.intMemBusy = "No"


if __name__ == "__main__":
    regs = readFiles("D:\\Fall 2019\\ACA\\Project\\reg.txt")
    dataLoc = readFiles("D:\\Fall 2019\\ACA\\Project\\data.txt")
    functional_units = readFiles("D:\\Fall 2019\\ACA\\Project\\config.txt")
    loop, instructions = readFiles("D:\\Fall 2019\\ACA\\Project\\inst.txt")

    print(loop)
    Pipeline(instructions)
