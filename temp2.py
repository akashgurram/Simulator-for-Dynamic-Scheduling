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
        self.raw = 0
        self.war = 0
        self.waw = 0
        self.sruct = 0
        self.status = 0
        self.int = 0
        self.mem = 0
        
        if(len(inst) == 3):
            self.op1 = inst[1]
            self.op2 = inst[2]
            
        elif(len(inst) == 4):
            self.op1 = inst[1]
            self.op2 = inst[2]
            self.op3 = inst[3]
            
    
        
class Pipeline:
     def __init__(self, instructions):
         
         
         
         instObjs = []
         for i in instructions:
             print(i)
             instObjs.append(Instructions(i))
             
             
         #Iterating Over the instruction objects
         processor = Processor()
         print(processor.dBusy)
         x = 2
         cycle = 0
         while(x>0):
             cycle +=1
             for inst in instObjs:
                 if(inst.status != 4):
                     if(inst.status == 0):
                         if(processor.fBusy == "No"):
            
                             processor.fBusy = "Yes"
                             inst.fetch = cycle
                             inst.status = 1
                                 
                                 
                                 
                     elif(inst.status == 1):
                         if(processor.dBusy == "No"):                             
                             processor.dBusy = "Yes"
                             processor.fBusy = "No"
                             inst.decode = cycle
                             inst.status = 2
                             
                     
                     
                     
                 
             x-=1
         for i in instObjs:
             print(i.fetch,i.decode,i.exec, i.write)
         print(functional_units.values())
         

class Processor:
    def __init__(self):
        self.fBusy = "No"
        self.dBusy = "No"
        self.exBusy = "No"
        self.wbBusy = "No"
                
         




if __name__ == "__main__":
    regs = readFiles("D:\\Fall 2019\\ACA\\Project\\reg.txt")
    dataLoc = readFiles("D:\\Fall 2019\\ACA\\Project\\data.txt")    
    functional_units = readFiles("D:\\Fall 2019\\ACA\\Project\\config.txt")
    loop, instructions = readFiles("D:\\Fall 2019\\ACA\\Project\\inst.txt")
    
    print(loop)
    Pipeline(instructions)
    
      