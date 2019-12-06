# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 18:48:44 2019

@author: akash
"""

from utils import readFiles, instParsing, functionalUnits
import tabulate as tb
from tabulate import tabulate
tb.PRESERVE_WHITESPACE = True
import copy


class Instructions:
    def __init__(self, inst):
        self.structset = 0
        self.finalLoop = "    "
        self.finalName = " ".join(inst)
        self.instCacheMiss = False
        self.dataCacheMiss = False
        self.instSpecialFlag = False
        self.dataSpecialFlag = False
        self.dataCacheHit = False
        self.wordAddress = 0
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

        self.ihit = False
        self.dhit = False
        self.imiss = False
        self.dmiss = False


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
            self.memCount = 0

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
        elif self.iname in ["J"]:
            self.op3 = inst[1]


class Pipeline:
    def __init__(self, instructions):

        RAND1 = False
        RAND2 = False
        fpRegistersList = []
        fpInstructionList = []
        instObjs = []
        for i in instructions:
            instObjs.append(Instructions(i))

        for i in range(len(instObjs)):
            instObjs[i].wordAddress = i

        #Appending the loop to the isntructions that require to the finalName to be displayed in the table
        for i in loop:
            instObjs[i[1]].finalLoop = i[0] + ": "


        newInstObjs = copy.deepcopy(instObjs)
        # Iterating Over the instruction objects
        processor = Processor()
        x = 1000
        cycle = 0
        newLoop = False
        newLoopJump = False
        youcanLoop = False
        cacheBusBusy = [False, None]
        instructionCache = {0: [], 1: [], 2: [], 3: []}
        dataCache1 = {0: [], 1: []}
        LRU1 = 0
        dataCache2 = {0: [], 1: []}
        LRU2 = 0
        dirty1 = [0, 0]
        dirty2 = [0, 0]
        instcacheMissPen = 2 * (functional_units["I-Cache"] + functional_units["Main memory"])
        datacacheMissPen = 2 * (functional_units["D-Cache"] + functional_units["Main memory"])
        icacheHit = 0
        iaccessReq = 0
        dcacheHit = 0
        daccessReq = 0
        onetimeAssignFlag = True
        instToBeSkipped = []
        instToBeFetched = []
        while x > 0:

            cycle += 1
            #HANDLING THE JUMP SUCH THAT Items after jump but before destination are skipped
            for inst in instObjs:
                if instObjs.index(inst) in instToBeSkipped:
                    inst.status = 5
                    continue
                if instObjs.index(inst) == instToBeFetched and inst.fetch == 0:
                    iaccessReq+=1
                    if inst.wordAddress in instructionCache[blockNo]:
                        icacheHit += 1
                    inst.fetch = cycle
                    inst.status = 5
                    continue
                if inst.status != 5:

                    # FETCH IS BEING DONE AND IS SOLID FOR NOW  -> Yet to ADD Instruction Cache


                    if inst.status == 0:
                        if processor.fBusy[0] == "No" or inst.instSpecialFlag == True:
                            blockNo = int(inst.wordAddress / 4) % 4


                            if onetimeAssignFlag == True:
                                if inst.wordAddress in instructionCache[blockNo]:
                                    icacheHit += 1
                                    inst.ihit = True
                                    iaccessReq += 1
                                else:
                                    startingAdress = int(inst.wordAddress/4) * 4
                                    instructionCache[blockNo] = list(range(startingAdress, startingAdress + 4))
                                    inst.instCacheMiss = True
                                    if cacheBusBusy[0] == True:
                                        continue
                                    else:
                                        inst.imiss = True
                                        cacheBusBusy = [True, instObjs.index(inst)]
                                    iaccessReq += 1
                                if inst.instCacheMiss:
                                    instructionCycles = instcacheMissPen
                                    onetimeAssignFlag = False
                                else:
                                    instructionCycles = functional_units["I-Cache"]
                                    onetimeAssignFlag = False

                            if inst.imiss == True and cacheBusBusy[0] == True and cacheBusBusy[1] != instObjs.index(inst):
                                inst.struct = "Y"
                                continue

                            elif inst.imiss == True and not cacheBusBusy[0] == True or cacheBusBusy[1] == instObjs.index(inst):
                                processor.fBusy = ["Yes", instObjs.index(inst)]
                                inst.instSpecialFlag = True

                                instructionCycles -= 1
                                if(instructionCycles== 0):

                                    inst.fetch = cycle
                                    cacheBusBusy = [False, None]
                                    onetimeAssignFlag = True
                                    inst.status = 1
                            elif inst.ihit == True:
                                processor.fBusy = ["Yes", instObjs.index(inst)]
                                inst.instSpecialFlag = True

                                instructionCycles -= 1
                                if(instructionCycles== 0):
                                    inst.fetch = cycle
                                    onetimeAssignFlag = True
                                    inst.status = 1

                            else:
                                inst.struct = "Y"





                    # DECODE IS BEING DONE AND NOT SOLID
                    elif inst.status == 1:

                        if inst.iname in ["S.D", "SW"]:
                            if inst.op1 not in fpRegistersList:
                                processor.dBusy = "Yes"
                                if processor.fBusy[1] != instObjs.index(inst):
                                    pass
                                else:
                                    processor.fBusy = ["No", None]
                                inst.decode = cycle
                                inst.status = 2
                            else:
                                if inst.raw == "N":
                                    processor.fBusy = ["No", None]
                                inst.raw = "Y"
                                processor.dBusy = "Yes"
                                continue
                        # Checking if the HLT is not the last two halts
                        if inst.iname == "HLT" and instObjs[instObjs.index(inst) - 1].iname != "HLT" and youcanLoop == True:
                            processor.fBusy = ["No", None]
                            inst.fetch = cycle-1
                            inst.status = 5
                            continue

                        elif inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname != "HLT" and youcanLoop == False:

                            processor.fBusy = ["No", None]
                            inst.decode = cycle
                            inst.status = 5

                        elif inst.iname == "HLT" and instObjs[instObjs.index(inst)-1].iname == "HLT":
                            processor.fBusy = ["No", None]
                            inst.status = 5
                            # x = False

                        # Adds the OP1 to the Global list if the INSTRUCTION NAME is NOT ["BNE", "HLT", "J", "BEQ"]
                        if inst.op1 not in fpRegistersList and inst.iname not in ["BNE", "HLT", "J", "BEQ", "S.D"]:
                            fpRegistersList.append(inst.op1)
                            fpInstructionList.append(instObjs.index(inst))

                        # Checks THE WAW Hazard
                        if inst.iname not in ["BNE", "HLT", "J", "BEQ", "S.D"] and inst.op1 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op1)] != instObjs.index(inst):
                            inst.waw = "Y"
                            continue

                        # Actually diving in to the decode stage for all the other Instructions
                        if processor.dBusy == "No" and inst.iname not in ["BNE", "HLT", "J", "BEQ"]:
                            # Checking if the registers op2 and op3 are not already in the List.
                            if inst.op2 not in fpRegistersList and inst.op3 not in fpRegistersList and inst.iname not in ["S.D", "SW"]:
                                #processor.fBusy = "No"
                                if inst.iname in ["ADD.D", "SUB.D"]:

                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    pipelined = functional_units[inst.functionalUnit][1]
                                    if pipelined == "no":
                                        if processor.addBusy == "No":
                                            inst.decode = cycle
                                            processor.dBusy = "Yes"
                                            processor.fBusy = ["No", None]
                                            inst.status = 2
                                        else:
                                            inst.struct = "Y"

                                    else:  # NOT PIPELINED
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = ["No", None]
                                        inst.status = 2

                                elif inst.iname == "MUL.D":
                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    pipelined = functional_units[inst.functionalUnit][1]
                                    if pipelined == "no":
                                        if processor.mulBusy == "No":
                                            inst.decode = cycle
                                            processor.dBusy = "Yes"
                                            processor.fBusy = ["No", None]
                                            inst.status = 2
                                        else:
                                            inst.struct = "Y"

                                    else:  # NOT PIPELINED
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = ["No", None]
                                        inst.status = 2



                                elif inst.iname == "DIV.D":
                                    # Stalling the Inst in the decode stage itself if it's exec stage is not available
                                    # DO THIS FOR THE OTHER INSTRUCTIONS AS WELL
                                    pipelined = functional_units[inst.functionalUnit][1]
                                    if pipelined == "No":
                                        if processor.divBusy == "No":
                                            inst.decode = cycle
                                            processor.dBusy = "Yes"
                                            processor.fBusy = ["No", None]
                                            inst.status = 2
                                        else:
                                            inst.struct = "Y"

                                    else:  # NOT PIPELINED
                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = ["No", None]
                                        inst.status = 2

                                elif inst.iname in ["L.D", "LW"]:
                                    if RAND1 == True or processor.intBusy == "No":
                                        if instObjs[instObjs.index(inst)-1].decode - inst.fetch > 0:
                                            inst.fetch = instObjs[instObjs.index(inst)-1].decode

                                        inst.decode = cycle
                                        processor.dBusy = "Yes"
                                        processor.fBusy = ["No", None]
                                        inst.status = 2
                                    else:
                                        continue

                                else:
                                    if instObjs[instObjs.index(inst)-1].decode - inst.fetch > 0:
                                        inst.fetch = instObjs[instObjs.index(inst)-1].decode

                                    inst.decode = cycle
                                    processor.dBusy = "Yes"
                                    processor.fBusy = ["No", None]
                                    inst.status = 2

                            # DO IT FOR OP3 AS WELL - Done
                            elif (inst.op2 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op2)] == instObjs.index(inst))\
                                or (inst.op3 in fpRegistersList and fpInstructionList[fpRegistersList.index(inst.op3)] == instObjs.index(inst)):
                                if RAND1 == True or processor.intBusy == "No":
                                    if instObjs[instObjs.index(inst) - 1].decode - inst.fetch > 0:
                                        inst.fetch = instObjs[instObjs.index(inst) - 1].decode
                                    processor.dBusy = "Yes"
                                    processor.fBusy = ["No", None]
                                    inst.decode = cycle
                                    inst.status = 2
                                else:
                                    continue
                            # else:
                            #     inst.raw = "Y"
                            else:
                                inst.raw = "Y"
                                #processor.dBusy = "Yes"



                        # Branching case if Instruction name is BNE Or BEQ
                        elif inst.iname in ["BNE", "BEQ"]:
                            if inst.op1 in fpRegistersList and not fpInstructionList[fpRegistersList.index(inst.op1)] == instObjs.index(inst):
                                #processor.dBusy = "Yes"
                                inst.raw = "Y"
                            else:
                                #processor.dBusy = "Yes"
                                processor.fBusy = ["No", None]
                                inst.decode = cycle
                                inst.status = 2
                                #youcanLoop = False

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
                                    newInstructions = copy.deepcopy(newInstObjs[z:])
                                    newLoop = True
                                    processor.dBusy = "No"
                                    inst.status = 5
                                    continue

                        # Branching case if Instruction name is J
                        elif inst.iname in ["J"]:
                            print(vars(inst))
                            #processor.dBusy = "Yes"
                            processor.fBusy = ["No", None]
                            inst.decode = cycle
                            inst.status = 2



                            for p in loop:
                                print("loop is ", loop)
                                if p[0] == inst.op3:
                                    z = p[1]


                            instToBeSkipped = list(range(instObjs.index(inst)+2, z))
                            instToBeFetched = instObjs.index(inst)+1
                            #newInstructions = copy.deepcopy(newInstObjs[z:])
                            newLoopJump = True
                            processor.dBusy = "No"
                            inst.status = 5
                            continue





                    # EXECUTION IS BEING DONE HERE. SOLID
                    elif inst.status == 2:

                        if inst.iname in ["L.D", "LW"]:

                            if inst.dataCacheMiss == False:
                                offset = inst.op2.split("(")[0]
                                actualReg = inst.op2.split("(")[1][:-1]
                                actualBlockNo1 = regs[int(actualReg[1:])] + int(offset)
                                if inst.iname == "L.D":
                                    actualBlockNos = [actualBlockNo1, actualBlockNo1+4]
                                else:
                                    actualBlockNos = [actualBlockNo1]

                                for actualBlockNo in actualBlockNos:
                                    initialBlockNo = int(actualBlockNo / 16) * 16
                                    setNumber = int(actualBlockNo/ 16) % 2

                                    listtoBePopulated = [initialBlockNo, initialBlockNo+4, initialBlockNo+8, initialBlockNo+12]
                                    dataCacheSet = []
                                    if setNumber == 0:
                                        if dirty1[LRU1] != 0:
                                            #inst.memCount += datacacheMissPen
                                            dirty1[LRU1] = 0

                                        dataCacheSet, LRU = dataCache1, LRU1
                                    elif setNumber == 1:
                                        if dirty2[LRU2] != 0:
                                            #inst.memCount += datacacheMissPen
                                            dirty2[LRU2] = 0
                                        dataCacheSet, LRU = dataCache2, LRU2
                                    # Search in only 1 set

                                    if actualBlockNo in dataCacheSet[0] or actualBlockNo in dataCacheSet[1]:

                                        dcacheHit+=1
                                        daccessReq += 1
                                        inst.dhit = True
                                        inst.memCount += functional_units["D-Cache"]
                                        inst.dataCacheMiss = True
                                    else:
                                        if cacheBusBusy[0] == True:
                                            continue
                                        else:
                                            inst.dmiss = True
                                            daccessReq += 1
                                            cacheBusBusy = [True, instObjs.index(inst)]
                                        inst.memCount += datacacheMissPen


                                        dataCacheSet[LRU] = listtoBePopulated
                                        LRU = LRU ^ 1


                            if processor.intBusy == "No" and inst.intCount == 1:

                                #HANDLING THE STRUCT HAZARD
                                if processor.memBusy[1] == instObjs.index(inst)-1:
                                    inst.structset +=1
                                if instObjs[instObjs.index(inst)-1].structset > 1:
                                    inst.struct = "Y"

                                if RAND2 == True or processor.memBusy[0] == "No":
                                    processor.intBusy = "Yes"
                                    inst.intCount -= 1
                                    processor.dBusy = "No"
                                    RAND1 = True
                                else:
                                    inst.struct = "Y"
                                    continue
                            else:
                                if inst.dmiss and cacheBusBusy[0] and cacheBusBusy[1]!= instObjs.index(inst):
                                    inst.struct = "Y"
                                    continue

                                elif (inst.dmiss and not cacheBusBusy[0]) or cacheBusBusy[1] == instObjs.index(inst):

                                    if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                        if processor.memBusy[0] == "No":
                                            processor.intBusy = "No"
                                            RAND1 = False
                                        processor.memBusy[0] = "Yes"
                                        processor.memBusy[1] = instObjs.index(inst)
                                        inst.memCount -= 1

                                        if (inst.memCount == 0):
                                            cacheBusBusy = [False, None]
                                            RAND2 = True
                                            inst.exec = cycle
                                            inst.status = 3

                                    else:
                                        inst.struct = "Y"

                                elif inst.dhit:
                                    if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                        if processor.memBusy[0] == "No":
                                            processor.intBusy = "No"
                                            RAND1 = False
                                        processor.memBusy[0] = "Yes"
                                        processor.memBusy[1] = instObjs.index(inst)
                                        inst.memCount -= 1

                                        if(inst.memCount == 0):
                                            RAND2 = True
                                            inst.exec = cycle
                                            inst.status = 3

                                    else:
                                     inst.struct = "Y"

                                else:
                                    inst.struct = "Y"


                        if inst.iname in ["S.D", "SW"]:

                            if inst.dataCacheMiss == False:
                                offset = inst.op2.split("(")[0]
                                actualReg = inst.op2.split("(")[1][:-1]
                                actualBlockNo1 = regs[int(actualReg[1:])] + int(offset)
                                if inst.iname == "S.D":
                                    actualBlockNos = [actualBlockNo1, actualBlockNo1+4]
                                else:
                                    actualBlockNos = [actualBlockNo1]

                                for actualBlockNo in actualBlockNos:
                                    initialBlockNo = int(actualBlockNo / 16) * 16
                                    setNumber = int(actualBlockNo/ 16) % 2

                                    listtoBePopulated = [initialBlockNo, initialBlockNo+4, initialBlockNo+8, initialBlockNo+12]
                                    dataCacheSet = []
                                    if setNumber == 0:
                                        # WRITE ALLOCATE. DIRTY BLOCKS
                                        if dirty1[LRU1] != 0:
                                            pass
                                            #inst.memCount += datacacheMissPen
                                        dirty1[LRU1] = 1
                                        dataCacheSet, LRU = dataCache1, LRU1
                                    elif setNumber == 1:
                                        if dirty2[LRU2] != 0:
                                            pass
                                            #inst.memCount += datacacheMissPen
                                        dirty2[LRU2] = 1
                                        dataCacheSet, LRU = dataCache2, LRU2
                                    # Search in only 1 set

                                    if actualBlockNo in dataCacheSet[0] or actualBlockNo in dataCacheSet[1]:

                                        dcacheHit+=1
                                        daccessReq += 1
                                        inst.dhit = True
                                        inst.memCount += functional_units["D-Cache"]
                                        inst.dataCacheMiss = True
                                    else:
                                        if cacheBusBusy[0] == True:
                                            continue
                                        else:
                                            inst.dmiss = True
                                            daccessReq += 1
                                            cacheBusBusy = [True, instObjs.index(inst)]
                                        # The EXTRA ONE CYCLE because store takes it to write
                                        inst.memCount += datacacheMissPen+1


                                        dataCacheSet[LRU] = listtoBePopulated
                                        LRU = LRU ^ 1


                            if processor.intBusy == "No" and inst.intCount == 1:

                                #HANDLING THE STRUCT HAZARD
                                if processor.memBusy[1] == instObjs.index(inst)-1:
                                    inst.structset +=1
                                if instObjs[instObjs.index(inst)-1].structset > 1:
                                    inst.struct = "Y"

                                if RAND2 == True or processor.memBusy[0] == "No":
                                    processor.intBusy = "Yes"
                                    inst.intCount -= 1
                                    processor.dBusy = "No"
                                    RAND1 = True
                                else:
                                    inst.struct = "Y"
                                    continue
                            else:
                                if inst.dmiss and cacheBusBusy[0] and cacheBusBusy[1]!= instObjs.index(inst):
                                    inst.struct = "Y"
                                    continue

                                elif (inst.dmiss and not cacheBusBusy[0]) or cacheBusBusy[1] == instObjs.index(inst):

                                    if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                        if processor.memBusy[0] == "No":
                                            processor.intBusy = "No"
                                            RAND1 = False
                                        processor.memBusy[0] = "Yes"
                                        processor.memBusy[1] = instObjs.index(inst)
                                        inst.memCount -= 1

                                        if (inst.memCount == 0):
                                            cacheBusBusy = [False, None]
                                            RAND2 = True
                                            inst.exec = cycle
                                            inst.status = 3

                                    else:
                                        inst.struct = "Y"

                                elif inst.dhit:
                                    if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                        if processor.memBusy[0] == "No":
                                            processor.intBusy = "No"
                                            RAND1 = False
                                        processor.memBusy[0] = "Yes"
                                        processor.memBusy[1] = instObjs.index(inst)
                                        inst.memCount -= 1

                                        if(inst.memCount == 0):
                                            RAND2 = True
                                            inst.exec = cycle
                                            inst.status = 3

                                    else:
                                     inst.struct = "Y"

                                else:
                                    inst.struct = "Y"


                        #
                        # if inst.iname in ["S.D"]:
                        #     if inst.dataCacheMiss == False:
                        #         offset = inst.op2.split("(")[0]
                        #         actualReg = inst.op2.split("(")[1][:-1]
                        #         actualBlockNo = regs[int(actualReg[1:])] + int(offset)
                        #         # initialBlockNo = int((regs[int(actualReg[1:])] + int(offset))/16) * 16
                        #         # setNumber = int(regs[int(actualReg[1:])] + int(offset)/16) % 2
                        #         initialBlockNo = int(actualBlockNo / 16) * 16
                        #         setNumber = int(actualBlockNo/ 16) % 2
                        #         daccessReq+=1
                        #         listtoBePopulated = [initialBlockNo, initialBlockNo+4, initialBlockNo+8, initialBlockNo+12]
                        #         dataCacheSet = []
                        #         if setNumber == 0:
                        #             #WRITE ALLOCATE. DIRTY BLOCKS
                        #             if dirty1[LRU1] != 0:
                        #                 inst.memCount += datacacheMissPen
                        #             dirty1[LRU1] = 1
                        #             dataCacheSet, LRU = dataCache1, LRU1
                        #         elif setNumber == 1:
                        #             if dirty2[LRU2] != 0:
                        #                 inst.memCount += datacacheMissPen
                        #             dirty2[LRU1] = 1
                        #             dataCacheSet, LRU = dataCache2, LRU2
                        #         # Search in only 1 set
                        #
                        #         if actualBlockNo in dataCacheSet[0] or actualBlockNo in dataCacheSet[1]:
                        #
                        #             dcacheHit+=1
                        #             inst.memCount += functional_units["D-Cache"]
                        #             inst.dataCacheMiss = True
                        #         else:
                        #
                        #             inst.memCount += datacacheMissPen+1
                        #
                        #
                        #             dataCacheSet[LRU] = listtoBePopulated
                        #             LRU = LRU ^ 1
                        #
                        #         actualBlockNo += 4
                        #         initialBlockNo = int(actualBlockNo / 16) * 16
                        #         setNumber = int(actualBlockNo/ 16) % 2
                        #         daccessReq += 1
                        #         listtoBePopulated = [initialBlockNo, initialBlockNo + 4, initialBlockNo + 8,
                        #                              initialBlockNo + 12]
                        #         dataCacheSet = []
                        #         if setNumber == 0:
                        #             dataCacheSet, LRU = dataCache1, LRU1
                        #         elif setNumber == 1:
                        #             dataCacheSet, LRU = dataCache2, LRU2
                        #         if actualBlockNo in dataCacheSet[0] or actualBlockNo in dataCacheSet[1]:
                        #
                        #             dcacheHit += 1
                        #             inst.memCount += functional_units["D-Cache"]
                        #             inst.dataCacheMiss = True
                        #         else:
                        #
                        #             inst.memCount += datacacheMissPen +1
                        #             dataCacheSet[LRU] = listtoBePopulated
                        #             LRU = LRU ^ 1
                        #
                        #     if processor.intBusy == "No" and inst.intCount == 1:
                        #         if RAND2 == True or processor.memBusy[0] == "No":
                        #
                        #             processor.intBusy = "Yes"
                        #             inst.intCount -= 1
                        #             processor.dBusy = "No"
                        #             RAND1 = True
                        #         else:
                        #             inst.raw = "Y"
                        #             continue
                        #
                        #     else:
                        #
                        #         if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                        #             if processor.memBusy[0] == "No":
                        #                 processor.intBusy = "No"
                        #                 RAND1 = False
                        #             processor.memBusy[0] = "Yes"
                        #             processor.memBusy[1] = instObjs.index(inst)
                        #             inst.memCount -= 1
                        #
                        #             if (inst.memCount == 0):
                        #                 RAND2 = True
                        #                 inst.exec = cycle
                        #                 inst.status = 3
                        #
                        #         else:
                        #             inst.struct = "Y"
                        #
                        #
                        # if inst.iname in ["SW"]:
                        #     if inst.dataCacheMiss == False:
                        #         offset = inst.op2.split("(")[0]
                        #         actualReg = inst.op2.split("(")[1][:-1]
                        #         actualBlockNo = regs[int(actualReg[1:])] + int(offset)
                        #         # initialBlockNo = int((regs[int(actualReg[1:])] + int(offset))/16) * 16
                        #         # setNumber = int(regs[int(actualReg[1:])] + int(offset)/16) % 2
                        #         initialBlockNo = int(actualBlockNo / 16) * 16
                        #         setNumber = int(actualBlockNo/ 16) % 2
                        #         daccessReq+=1
                        #         listtoBePopulated = [initialBlockNo, initialBlockNo+4, initialBlockNo+8, initialBlockNo+12]
                        #         dataCacheSet = []
                        #         if setNumber == 0:
                        #             dataCacheSet, LRU = dataCache1, LRU1
                        #         elif setNumber == 1:
                        #             dataCacheSet, LRU = dataCache2, LRU2
                        #         # Search in only 1 set
                        #
                        #         if actualBlockNo in dataCacheSet[0] or actualBlockNo in dataCacheSet[1]:
                        #
                        #             dcacheHit+=1
                        #             inst.memCount += functional_units["D-Cache"]
                        #             inst.dataCacheMiss = True
                        #         else:
                        #
                        #             inst.memCount += datacacheMissPen +1
                        #
                        #
                        #             dataCacheSet[LRU] = listtoBePopulated
                        #             LRU = LRU ^ 1
                        #
                        #     if processor.intBusy == "No" and inst.intCount == 1:
                        #         if RAND2 == True or processor.memBusy[0] == "No":
                        #
                        #             processor.intBusy = "Yes"
                        #             inst.intCount -= 1
                        #             processor.dBusy = "No"
                        #             RAND1 = True
                        #         else:
                        #             inst.struct = "Y"
                        #             continue
                        #
                        #     else:
                        #
                        #         if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                        #             if processor.memBusy[0] == "No":
                        #                 processor.intBusy = "No"
                        #                 RAND1 = False
                        #             processor.memBusy[0] = "Yes"
                        #             processor.memBusy[1] = instObjs.index(inst)
                        #             inst.memCount -= 1
                        #
                        #             if (inst.memCount == 0):
                        #                 RAND2 = True
                        #                 inst.exec = cycle
                        #                 inst.status = 3
                        #
                        #         else:
                        #             inst.struct = "Y"

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

                        elif inst.iname == "DIV.D":
                            pipelined = functional_units[inst.functionalUnit][1]
                            if pipelined == "yes":
                                if processor.divBusy == "No":

                                    processor.dBusy = "No"
                                    processor.divBusy = "Yes"
                                else:
                                    processor.dBusy = "No"
                                inst.execCycle -= 1
                                if inst.execCycle == 0:
                                    processor.divBusy = "No"
                                    inst.exec = cycle
                                    inst.status = 3
                            else:
                                if processor.divBusy == "No":
                                    processor.dBusy = "No"
                                    processor.divBusy = "Yes"
                                    inst.execCycle -= 1
                                    if inst.execCycle == 0:
                                        processor.divBusy = "No"
                                        inst.exec = cycle
                                        inst.status = 3
                                elif processor.divBusy == "Yes":
                                    processor.dBusy = "No"
                                    if inst.execCycle != functional_units[inst.functionalUnit][0]:
                                        inst.execCycle -= 1
                                        if inst.execCycle == 0:
                                            processor.divBusy = "No"
                                            inst.exec = cycle
                                            inst.status = 3


                        elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                            #processor.dBusy = "No"

                            if processor.intBusy == "No" and inst.intCount == 1:
                                if processor.memBusy[1] == instObjs.index(inst)-1:
                                    inst.structset +=1
                                if instObjs[instObjs.index(inst)-1].structset > 1:
                                    inst.struct = "Y"
                                if RAND2 == True or processor.memBusy[0] == "No":

                                    processor.intBusy = "Yes"
                                    inst.intCount -= 1
                                    processor.dBusy = "No"
                                    RAND1 = True
                                else:
                                    inst.struct = "Y"
                                    continue

                            else:

                                if processor.memBusy[0] == "No":
                                    if inst.memCount == 1:
                                        inst.memCount = 0
                                        RAND2 = True
                                        processor.intBusy = "No"
                                        RAND1 = False
                                        processor.memBusy[0] = "Yes"
                                        processor.memBusy[1] = instObjs.index(inst)

                                    inst.exec = cycle
                                    inst.status = 3

                                else:
                                    inst.struct = "Y"
                                # if processor.memBusy[0] == "No" or processor.memBusy[1] == instObjs.index(inst):
                                #     if processor.memBusy[0] == "No":
                                #         processor.intBusy = "No"
                                #         RAND1 = False
                                #     processor.memBusy[0] = "Yes"
                                #     processor.memBusy[1] = instObjs.index(inst)
                                #     inst.memCount -= 1
                                #
                                #     if (inst.memCount == 0):
                                #         RAND2 = True
                                #         inst.exec = cycle
                                #         inst.status = 3
                                #
                                # else:
                                #     inst.struct = "Y"





                    elif inst.status == 3:

                        if processor.wbBusy[0] == "No":
                            if inst.iname in ["L.D", "S.D", "LW", "SW"]:
                                if RAND2 == True:

                                    processor.memBusy[0] = "No"
                                    processor.memBusy[1] = None


                                    RAND2 = False
                                else:
                                    continue


                            elif inst.iname == "ADD.D" or inst.iname == "SUB.D":
                                #processor.addBusy = "No"
                                pass

                            elif inst.iname == "MUL.D":
                                #processor.mulBusy = "No"
                                pass

                            elif inst.iname in ["DADD", "DADDI", "DSUB", "DSUBI", "AND", "ANDI", "OR", "ORI"]:
                                #processor.intMemBusy = "No"
                                if RAND2 == True:
                                    RAND2 = False
                                    processor.memBusy[0] = "No"
                                    processor.memBusy[1] = None
                                    self.calculate(inst.iname, inst.op1, inst.op2, inst.op3)
                                    inst.status = 4
                                    inst.write = cycle
                                else:
                                    continue
                            if inst.iname not in ["S.D", "SW"]:
                                index1 = fpRegistersList.index(inst.op1)
                                fpRegistersList.remove(fpRegistersList[index1])
                                fpInstructionList.remove(fpInstructionList[index1])
                            processor.wbBusy = ["Yes", cycle]
                            inst.status = 4
                            inst.write = cycle

                        else:

                            if cycle == processor.wbBusy[1]:
                                inst.struct = "Y"
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
                #youcanLoop = False
                processor.fBusy = ["No", None]
                processor.dBusy = "No"
                processor.wbBusy = ["No", 0]
                instObjs.pop()
                instObjs += newInstructions
                newLoop = False
                #cycle -= 1
            # else:
            #     processor.dBusy = "No"
            x -= 1
        for inst in instObjs:
            inst.finalOutput.append(inst.finalLoop)
            inst.finalOutput.append(inst.finalName)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.fetch)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.decode)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.exec)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.write)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.raw)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.war)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.waw)
            inst.finalOutput.append("    ")
            inst.finalOutput.append(inst.struct)

        # REPLACING ALL THE ZERO's with " " in the output file
        for inst in instObjs:
            inst.finalOutput = [" " if x == 0 else x for x in inst.finalOutput]
        # instObjs[-1].finalOutput = [" " if x == "N" else x for x in instObjs[-1].finalOutput]
        for inst in instObjs:
            if inst.iname == "HLT" and inst.decode == 0:
                inst.finalOutput = [" " if x == "N" else x for x in inst.finalOutput]
        table = []
        headers = ["", "Instruction", "    ", "FT", "    ", "ID", "    ", "EX", "    ", "WB", "    ", "RAW", "    ", "WAR", "    ", "WAW", "    ", "Struct"]
        table.append(headers)
        for inst in instObjs:
            table.append(inst.finalOutput)
        print(tabulate(table))
        print("I Cache hit", icacheHit)
        print("I Access req", iaccessReq)
        print("D Cache hit", dcacheHit)
        print("D Access req", daccessReq)
        f = open('result.txt', 'w')
        f.write(tabulate(table, tablefmt="plain"))
        f.write("\n\nTotal number of access requests for instruction cache: " + repr(iaccessReq))
        f.write("\n\nNumber of instruction cache hits: " + repr(icacheHit))
        f.write("\n\nTotal number of access requests for data cache: " + repr(daccessReq))
        f.write("\n\nNumber of data cache hits: " + repr(dcacheHit))
        f.close()


    def calculate(self, inst, op1, op2, op3):
        if inst == "DADD":
            regs[int(op1[1:])] = regs[int(op2[1:])] + regs[int(op3[1:])]

        elif inst == "DADDI":
            regs[int(op1[1:])] = regs[int(op2[1:])] + int(op3)

        elif inst == "DSUB":
            regs[int(op1[1:])] = regs[int(op2[1:])] - regs[int(op3[1:])]

        elif inst == "DSUBI":
            regs[int(op1[1:])] = regs[int(op2[1:])] - int(op3)

        elif inst == "AND":
            regs[int(op1[1:])] = regs[int(op2[1:])] & regs[int(op3[1:])]

        elif inst == "ANDI":
            regs[int(op1[1:])] = regs[int(op2[1:])] & int(op3)

        elif inst == "OR":
            regs[int(op1[1:])] = regs[int(op2[1:])] | regs[int(op3[1:])]

        elif inst == "ORI":
            regs[int(op1[1:])] = regs[int(op2[1:])] | int(op3)

class Processor:
    def __init__(self):
        self.fBusy = ["No", None]
        self.dBusy = "No"
        self.wbBusy = ["No", 0]
        self.intBusy = "No"
        self.memBusy = ["No", None]
        self.addBusy = "No"
        self.mulBusy = "No"
        self.divBusy = "No"
        self.intMemBusy = "No"


if __name__ == "__main__":
    regs = readFiles("reg.txt")
    dataLoc = readFiles("data.txt")
    functional_units = readFiles("config.txt")
    loop, instructions = readFiles("inst.txt")

    Pipeline(instructions)
