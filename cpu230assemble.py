#!/usr/bin/python

#Aziza Mankenova and Nurlan Dadashov

import re
import sys

#Reads the lines from a file
with open(sys.argv[1], 'r') as inp:
    lines = [line.strip() for line in inp]

#converts binary parameters into hexadecimal number
def convert(opcode1, addrmode1, operand1):
    opcode   = int(opcode1,16) 
    addrmode = int(addrmode1,16) 
    operand  = int(operand1,16) 
    bopcode = format(opcode, '06b') 
    baddrmode = format(addrmode, '02b') 
    boperand = format(operand, '016b') 
    bin = '0b' + bopcode + baddrmode + boperand 
    ibin = int(bin[2:],2) ; 
    return format(ibin, '06x')

#Stores the operation codes
opcodes = {
    "HALT": "1",
    "LOAD": "2",
    "STORE": "3",
    "ADD": "4",
    "SUB": "5",
    "INC": "6",
    "DEC": "7",
    "XOR": "8",
    "AND": "9",
    "OR": "A",
    "NOT": "B",
    "SHL": "C",
    "SHR": "D",
    "NOP": "E",
    "PUSH": "F",
    "POP": "10",
    "CMP": "11",
    "JMP": "12",
    "JZ": "13",
    "JE": "13",
    "JNZ": "14",
    "JNE": "14",
    "JC": "15",
    "JNC": "16",
    "JA": "17",
    "JAE": "18",
    "JB": "19",
    "JBE": "1A",
    "READ": "1B",
    "PRINT": "1C"
}

#Operation codes with no operand
no_operand_opcodes = ["HALT", "NOP"]

#Holds the hexadecimal representation of the registers
registers = {
    "PC": "0",
    "A": "1",
    "B": "2",
    "C": "3",
    "D": "4",
    "E": "5",
    "S": "6"
}

#Stores the labels
labels = {}

#Stores the instructions
instructions = []

#Count for the empty lines and lines containing labels
ignore = 0

#First pass when the empty lines are ignored, 
#and all the labels are stored
for index, line in enumerate(lines):
    tokens = line.split()
    if not tokens: 
        ignore += 1
        continue
    if tokens[0].upper() not in opcodes:
        ignore += 1
        if tokens[0][:-1].lower() not in labels:
            labels[tokens[0][:-1].lower()] = format((index - ignore + 1) * 3, 'x')
        else:
            print("Error: multiple definitions of a label")
            exit()
#Second pass through all the lines with instructions
for index, line in enumerate(lines):
    tokens = line.split()
    if not tokens: continue
    if tokens[0].upper() in opcodes:
        opcode = opcodes[tokens[0].upper()]
    else: 
        continue
    
    if tokens[0].upper() in no_operand_opcodes: 
        instructions.append(convert(opcode, "0", "0"))
    else:
        operandToken = tokens[1]

        if operandToken.lower() in labels:
            operandToken = labels[operandToken.lower()]

        
        isCharacter = re.search(r'\'(.+?)\'', operandToken)

        isMemoryAddress = re.search(r'\[(.+?)\]', operandToken)

        if isCharacter:
            addrmode = "0"
            operand = format(ord(isCharacter.group()[1:-1]), 'x')
        elif operandToken in registers:
            addrmode = "1"
            operand = registers[operandToken]
        elif isMemoryAddress:
            memoryaddress = isMemoryAddress.group()[1:-1]
            if memoryaddress in registers:
                addrmode = "2"
                operand = registers[operandToken[1:-1]]
            else:
                addrmode = "3"
                operand = memoryaddress
        else:
            addrmode = "0"
            operand = operandToken

        instructions.append(convert(opcode, addrmode, operand))


#Output is written into a file
out = open(sys.argv[1].replace(".asm", ".bin"), 'w')

#writes the binary code of each instruction
for instr in instructions: 
    out.write(bin(int(instr, 16))[2:].zfill(24) + "\n")
