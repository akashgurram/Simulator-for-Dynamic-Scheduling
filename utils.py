# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


def readFiles(path):
    f = open(path, "r")
    r = f.read()
    r = r.split("\n")
    #This line removes the empty files while parsing
    r = list(filter(None, r))

    if "reg.txt" in path:

        for i in range(len(r)):
            r[i] = int(r[i], 2)
        # for i in range(len(r)):
        #     r[i] = hex(r[i])
        return r
    elif "data.txt" in path:

        j = 0
        d = {}
        for i in range(len(r)):


            d[256+j] = int(r[i], 2)
            #r[i] = (256+j, int(r[i], 2))
            j += 4

        return d
    elif "config.txt" in path:
        functional_units = functionalUnits(r)
        return functional_units

    elif "inst.txt" in path:
        loop, instructions = instParsing(r)
        return loop, instructions


def functionalUnits(units):
    dict1 = {}
    for i in range(len(units)):
        key = units[i].split(":")[0]
        value1 = int(units[i].split(":")[1].split(",")[0][1:])
        if "," in units[i]:
            value2 = units[i].split(":")[1].split(",")[1][1:]
            dict1[key] = (value1, value2)
        else:
            dict1[key] = value1
    return dict1


def instParsing(insts):
    loop = []
    instructions = []
    for i in range(len(insts)):
        if ":" in insts[i]:
            loop.append([insts[i].split(":")[0], i])
            x = insts[i].split(":")[1].split()
            if len(x) == 3:
                instructions.append([x[0], x[1][0:-1], x[2]])
            elif len(x) == 4:
                instructions.append([x[0], x[1][0:-1], x[2][0:-1], x[3]])
            else:
                instructions.append([x[0]])

        else:
            x = insts[i].split()
            if len(x) == 3:
                instructions.append([x[0], x[1][0:-1], x[2]])
            elif len(x) == 4:
                instructions.append([x[0], x[1][0:-1], x[2][0:-1], x[3]])
            # If the instruction is Jump
            elif len(x) == 2:
                instructions.append([x[0], x[1]])
            else:
                instructions.append([x[0]])

# CAPITALIZING THE INSTRUCTIONS AND LOOPS
    for i in range(len(instructions)):
        instructions[i] = [x.upper() for x in instructions[i]]
    for i in range(len(loop)):
        loop[i][0] = loop[i][0].upper()
    return loop, instructions
