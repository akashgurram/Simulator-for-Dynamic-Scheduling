# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 18:48:44 2019

@author: akash
"""

from utils import readFiles, instParsing, functionalUnits


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
        self.war = 0
        self.waw = 0
        self.struct = "N"
        self.status = 0
        self.intCount = 0
        self.memCount = 0
        self.functionalUnit = None
        self.execCycle = 0

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
        x = 40
        cycle = 0
        while x > 0:
            cycle += 1
            for inst in instObjs:
                if inst.status != 4:
                    if inst.status == 0:
                        if processor.fBusy == "No":
                            processor.fBusy = "Yes"
                            #fpRegistersList.append(inst.op1)
                            inst.fetch = cycle
                            inst.status = 1



                    elif inst.status == 1:
                        if inst.op1 not in fpRegistersList:
                            fpRegistersList.append(inst.op1)
                            fpInstructionList.append(instObjs.index(inst))
                        if processor.dBusy == "No":
                            if inst.op2 not in fpRegistersList and inst.op3 not in fpRegistersList:
                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2
                            # DO IT FOR OP3 AS WELL
                            elif inst.op2 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op2)] == instObjs.index(inst):
                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2
                            else:
                                inst.raw = "Y"

                    elif inst.status == 2:
                        if inst.iname == "L.D":

                            if processor.intBusy == "No" and inst.intCount == 1:
                                processor.intBusy = "Yes"
                                inst.intCount -= 1
                                processor.dBusy = "No"

                            elif processor.memBusy == "No":
                                if inst.memCount == 2:
                                    inst.memCount = 1
                                    processor.intBusy = "No"
                                    processor.memBusy = "Yes"
                            elif processor.memBusy == "Yes":
                                if inst.memCount == 2:
                                    inst.struct = "Y"
                                if inst.memCount == 1:
                                    inst.memCount = 0
                                    inst.exec = cycle

                                    inst.status = 3


                        ## YET TO ADD THE HAZARDS BOTH STRUCT  and make the pipelined auto instead of manual
                        elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                            pipelined = functional_units[inst.functionalUnit][1]
                            if pipelined == "yes":
                                if processor.addBusy == "No":
                                    processor.dBusy = "No"
                                    processor.addBusy = "Yes"
                                inst.execCycle -= 1
                                if inst.execCycle == 0:
                                    inst.exec = cycle
                                    inst.status = 3

                            else:
                                if processor.addBusy == "No":
                                    processor.dBusy = "No"
                                    processor.addBusy = "Yes"
                                    inst.execCycle -= 1
                                    if inst.execCycle == 0:
                                        inst.exec = cycle
                                        inst.status = 3

                                elif processor.addBusy == "Yes":
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

                            elif processor.memBusy == "No":
                                if inst.memCount == 1:
                                    inst.memCount = 0
                                    processor.intBusy = "No"
                                    processor.memBusy = "No"

                                inst.exec = cycle
                                inst.status = 3




                    elif inst.status == 3:
                        if inst.iname == "L.D":
                            processor.memBusy = "No"
                            inst.status = 4
                        elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                            processor.addBusy = "No"
                            inst.status = 4
                        elif inst.iname == "MUL.D":
                            processor.mulBusy = "No"
                            inst.status = 4
                        elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                            processor.intMemBusy = "No"
                            inst.status = 4
                        inst.write = cycle
                        index1 = fpRegistersList.index(inst.op1)
                        fpRegistersList.remove(fpRegistersList[index1])
                        fpInstructionList.remove(fpInstructionList[index1])
            x -= 1

        for i in instObjs:
            print(i.fetch, i.decode, i.exec, i.write, i.raw, i.struct)
        print(functional_units)
        print(functional_units.values())


class Processor:
    def __init__(self):
        self.fBusy = "No"
        self.dBusy = "No"
        self.wbBusy = "No"
        self.intBusy = "No"
        self.memBusy = "No"
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
