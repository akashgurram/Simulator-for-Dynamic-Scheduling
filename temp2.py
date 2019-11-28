# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 18:48:44 2019

@author: akash
"""

from utils import readFiles, instParsing, functionalUnits
from tabulate import tabulate


class Instructions:
    def __init__(self, inst):
        self.finalName = " ".join(inst)
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

        if self.iname in ["L.D", "S.D", "LW", "SW"]:
            self.intCount = 1
            self.functionalUnit = "Main memory"
            self.memCount = int(functional_units[self.functionalUnit])

        elif self.iname == "ADD.D" or self.iname == "SUB.D":
            self.functionalUnit = "FP adder"
            self.execCycle = int(functional_units[self.functionalUnit][0])

        elif self.iname == "MUL.D":
            self.functionalUnit = "FP Multiplier"
            self.execCycle = int(functional_units[self.functionalUnit][0])

        elif self.iname == "DIV.D":
            self.functionalUnit = "FP Multiplier"
            self.execCycle = int(functional_units[self.functionalUnit][0])

        elif self.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
            self.intCount = 1
            self.memCount = 1


class Pipeline:
    def __init__(self, instructions):

        fpRegistersList = []
        fpInstructionList = []
        instObjs = []
        for i in instructions:
            instObjs.append(Instructions(i))

        # Iterating Over the instruction objects
        processor = Processor()
        x = 70
        cycle = 0
        newLoop = False
        instructionCache = {0: [], 1: [], 2: [], 3: []}
        cacheMissPen = 2 * (functional_units["I-Cache"] + functional_units["Main memory"])
        cacheHit = 0
        while x > 0:

            cycle += 1
            for inst in instObjs:
                if inst.status != 5:

                    # FETCH IS BEING DONE AND IS SOLID FOR NOW  -> Yet to ADD Instruction Cache


                    if inst.status == 0:

                        if processor.fBusy == "No":
                            blockNo = int(instObjs.index(inst) / 4) % 4
                            print("block no", blockNo)
                            print("inst no", instObjs.index(inst), inst.iname, id(inst))

                            #if id(instObjs[instObjs.index(inst)]) in instructionCache[blockNo]:
                            if any(instObjs.index(inst) % 13 in c for c in instructionCache.values()):
                                print("Present", instructionCache[blockNo])
                                cacheHit += 1
                            else:
                                print("Not present", instructionCache[blockNo])
                                instructionCache[blockNo] = list(range(instObjs.index(inst) % 13, instObjs.index(inst) % 13 + 4))

                            print(instructionCache.values())
                            processor.fBusy = "Yes"
                            inst.fetch = cycle
                            inst.status = 1

                    # DECODE IS BEING DONE AND NOT SOLID
                    elif inst.status == 1:
                        # Checking if the HLT is not the last two halts
                        if inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname != "HLT":
                            processor.fBusy = "No"
                            inst.status = 5
                            continue
                        # Checks if the HLT is the last HLT, Then updates the last HLT and Previous HLT
                        elif inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname == "HLT":
                            instObjs[instObjs.index(inst)-1].decode = cycle-1
                            processor.fBusy = "No"
                            inst.status = 5
                            # x = False

                        # Adds the OP1 to the Global list if the INSTRUCTION NAME is NOT ["BNE", "HLT", "J", "BEQ"]
                        if inst.op1 not in fpRegistersList and inst.iname not in ["BNE", "HLT", "J", "BEQ"]:
                            fpRegistersList.append(inst.op1)
                            fpInstructionList.append(instObjs.index(inst))

                        # Checks THE WAW Hazard
                        if inst.op1 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op1)] != instObjs.index(inst) and inst.iname not in ["BNE", "HLT", "J", "BEQ"]:
                            inst.waw = "Y"
                            continue

                        # Actually diving in to the decode stage for all the other Instructions
                        if processor.dBusy == "No" and inst.iname not in ["BNE", "HLT", "J", "BEQ"]:
                            # Checking if the registers op2 and op3 are not already in the List.
                            if inst.op2 not in fpRegistersList and inst.op3 not in fpRegistersList:
                                if inst.iname == "ADD.D":
                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    if processor.addBusy == "No":
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = "No"
                                        inst.status = 2
                                    else:
                                        inst.struct = "Y"

                                elif inst.iname == "MUL.D":
                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    if processor.mulBusy == "No":
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = "No"
                                        inst.status = 2
                                    else:
                                        inst.struct = "Y"

                                elif inst.iname == "DIV.D":
                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    if processor.divBusy == "No":
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = "No"
                                        inst.status = 2
                                    else:
                                        inst.struct = "Y"

                                else:
                                    inst.decode = cycle
                                    processor.dBusy = "Yes"
                                    processor.fBusy = "No"
                                    inst.status = 2

                            # DO IT FOR OP3 AS WELL - Done
                            elif (inst.op2 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op2)] == instObjs.index(inst))\
                                or (inst.op3 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op3)] == instObjs.index(inst)):
                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2
                            else:
                                inst.raw = "Y"

                        # Branching case if Instruction name is BNE Or BEQ
                        elif inst.iname in ["BNE", "BEQ"]:
                            if inst.op1 in fpRegistersList and not fpInstructionList[fpRegistersList.index(inst.op1)] == instObjs.index(inst):
                                inst.raw = "Y"
                            else:
                                processor.dBusy = "Yes"
                                processor.fBusy = "No"
                                inst.decode = cycle
                                inst.status = 2
                                youcanLoop = False

                                # Branch check for BNE    ---> Yet to write Jump
                                if inst.iname == "BNE":
                                    if regs[int(inst.op1[1:])] != regs[int(inst.op2[1:])]:
                                        youcanLoop = True
                                    else:
                                        youcanLoop = False

                                # Branch check for BEQ
                                elif inst.iname == "BEQ":
                                    if regs[int(inst.op1[1:])] == regs[int(inst.op2[1:])]:
                                        youcanLoop = True
                                    else:
                                        youcanLoop = False

                                if youcanLoop:
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

                    # EXECUTION IS BEING DONE HERE . NOT SOLID
                    elif inst.status == 2:
                        if inst.iname in ["L.D", "S.D", "LW", "SW"]:
                            if processor.intBusy == "No" and inst.intCount == 1:
                                processor.intBusy = "Yes"
                                inst.intCount -= 1
                                processor.dBusy = "No"

                            else:
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
                                    processor.addBusy = "No"
                                    inst.exec = cycle
                                    inst.status = 3
                            else:
                                if processor.addBusy == "No":
                                    #CHANGE THIS FOR MUL AND DIV AS WELL
                                    #inst.decode = cycle-1
                                    processor.dBusy = "No"
                                    print("HHH", cycle, inst.op1)
                                    processor.addBusy = "Yes"
                                    inst.execCycle -= 1
                                    # This code below will be executed if the clock cyles it takes is only 1
                                    if inst.execCycle == 0:
                                        processor.addBusy = "No"
                                        inst.exec = cycle
                                        inst.status = 3

                                elif processor.addBusy == "Yes":
                                    processor.dBusy = "No"
                                    if inst.execCycle != functional_units[inst.functionalUnit][0]:
                                        inst.execCycle -= 1
                                        if inst.execCycle == 0:
                                            print("www", cycle, inst.op1)
                                            processor.addBusy = "No"
                                            inst.exec = cycle
                                            inst.status = 3
                        # MAKE THE PIPELINED WORK FOR THIS AS WELL
                        elif inst.iname == "MUL.D":
                            pipelined = functional_units[inst.functionalUnit][1]
                            if pipelined == "yes":
                                if processor.mulBusy == "No":

                                    processor.dBusy = "No"
                                    processor.mulBusy = "Yes"
                                else:
                                    processor.dBusy = "No"
                                inst.execCycle -= 1
                                if inst.execCycle == 0:
                                    processor.mulBusy = "No"
                                    inst.exec = cycle
                                    inst.status = 3
                            else:
                                if processor.mulBusy == "No":
                                    processor.dBusy = "No"
                                    processor.mulBusy = "Yes"
                                    inst.execCycle -= 1
                                    if inst.execCycle == 0:
                                        processor.mulBusy = "No"
                                        inst.exec = cycle
                                        inst.status = 3
                                elif processor.mulBusy == "Yes":
                                    processor.dBusy = "No"
                                    if inst.execCycle != functional_units[inst.functionalUnit][0]:
                                        inst.execCycle -= 1
                                        if inst.execCycle == 0:
                                            processor.mulBusy = "No"
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
                                    processor.memBusy[0] = "Yes"
                                    processor.memBusy[1] = instObjs.index(inst)

                                inst.exec = cycle
                                inst.status = 3




                    elif inst.status == 3:

                        if processor.wbBusy[0] == "No":
                            if inst.iname in ["L.D", "S.D", "LW", "SW"]:
                                processor.memBusy[0] = "No"
                                processor.memBusy[1] = None


                            elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                                #processor.addBusy = "No"
                                pass

                            elif inst.iname == "MUL.D":
                                #processor.mulBusy = "No"
                                pass

                            elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                #processor.intMemBusy = "No"
                                processor.memBusy[0] = "No"
                                processor.memBusy[1] = None
                                self.calculate(inst.iname, inst.op1, inst.op2, inst.op3)
                            inst.status = 4
                            inst.write = cycle
                            index1 = fpRegistersList.index(inst.op1)
                            fpRegistersList.remove(fpRegistersList[index1])
                            fpInstructionList.remove(fpInstructionList[index1])
                            processor.wbBusy = ["Yes", cycle]

                        else:

                            if cycle == processor.wbBusy[1]:
                                inst.struct = "Y"
                                print("COMIN", cycle)
                                if inst.iname in ["DADDI", "DSUB"]:
                                    inst.exec = cycle
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
            inst.finalOutput.append(inst.finalName)
            #inst.finalOutput.append(inst.iname+","+str(inst.op1)+","+str(inst.op2)+","+str(inst.op3))
            inst.finalOutput.append(inst.fetch)
            inst.finalOutput.append(inst.decode)
            inst.finalOutput.append(inst.exec)
            inst.finalOutput.append(inst.write)
            inst.finalOutput.append(inst.raw)
            inst.finalOutput.append(inst.war)
            inst.finalOutput.append(inst.waw)
            inst.finalOutput.append(inst.struct)

        # REPLACING ALL THE ZERO's with " " in the output file
        for inst in instObjs:
            inst.finalOutput = [" " if x == 0 else x for x in inst.finalOutput]
        table = []
        headers = ["Instruction", "FT", "ID", "EX", "WB", "RAW", "WAR", "WAW", "Struct"]
        table.append(headers)
        for inst in instObjs:
            table.append(inst.finalOutput)
        print(tabulate(table))
        print("Cache hit", cacheHit)
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
        self.divBusy = "No"
        self.intMemBusy = "No"


if __name__ == "__main__":
    regs = readFiles("D:\\Fall 2019\\ACA\\Project\\reg.txt")
    dataLoc = readFiles("D:\\Fall 2019\\ACA\\Project\\data.txt")
    functional_units = readFiles("D:\\Fall 2019\\ACA\\Project\\config.txt")
    loop, instructions = readFiles("D:\\Fall 2019\\ACA\\Project\\inst.txt")

    print(loop)
    Pipeline(instructions)
