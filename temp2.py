# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 18:48:44 2019

@author: akash
"""

from utils import readFiles, instParsing, functionalUnits


if __name__ == "__main__":
    regs = readFiles("D:\\Fall 2019\\ACA\\Project\\reg.txt")
    for i in range(len(regs)):
        regs[i] = int(regs[i],2)
    for i in range(len(regs)):
        regs[i] = hex(regs[i])
    print(regs)
    
    dataLoc = readFiles("D:\\Fall 2019\\ACA\\Project\\data.txt")    
    j = 100
    for i in range(len(dataLoc)):
        dataLoc[i] = ('0x'+str(j), int(dataLoc[i],2))
        j+=1
    print(dataLoc)
    
  
    functional_units = readFiles("D:\\Fall 2019\\ACA\\Project\\config.txt")
    functional_units = functionalUnits(functional_units)
    print(functional_units)
    
    instructions = readFiles("D:\\Fall 2019\\ACA\\Project\\inst.txt")
    print(instructions)
    
    loop,instructions = instParsing(instructions)
    print('\n')
    #print(instructions)
    print(loop)
    
    for i in instructions:
       print(i)