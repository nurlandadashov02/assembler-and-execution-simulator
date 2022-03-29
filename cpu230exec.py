#!/usr/bin/python

#Aziza Mankenova and Nurlan Dadashov
import sys
#Output is written into a file
out = open(sys.argv[1].replace(".bin", ".txt"), 'w')

#Reads the lines from a file
with open(sys.argv[1], 'r') as inp:
    lines = [line.strip() for line in inp]

#Stores the value of flags
flags = {
    "ZF": 0,
    "CF": 0,
    "SF": 0,
}

#64KB Memory as a list 
memory = ["00000000"] * 65536 # 64K

#Stores the register values
registers = {
    "PC": 0,
    "A": "0000000000000000",
    "B": "0000000000000000",
    "C": "0000000000000000",
    "D": "0000000000000000",
    "E": "0000000000000000",
    "S": "1111111111111110",
}

#Stores the bit representations of all the registers
bit_to_register = {
    "0000000000000000": "PC",
    "0000000000000001": "A",
    "0000000000000010": "B",
    "0000000000000011": "C",
    "0000000000000100": "D",
    "0000000000000101": "E",
    "0000000000000110": "S",
}

#Returns the data by the given address mode and operand
def operand_by_adr_mode(address_mode, operand):
    if address_mode == 0: # Immediate
        res = operand
    elif address_mode == 1: # Register
        res = registers[bit_to_register[operand]]
    elif address_mode == 2: #Indirect register
        res = memory[int(registers[bit_to_register[operand]], 2)] + memory[int(registers[bit_to_register[operand]], 2) + 1]
    elif address_mode == 3: # Memory
        res = memory[int(operand, 2)] + memory[int(operand, 2) + 1]
    return res



#Sets all of the flags according to the bits of the given parameter
def setFlags(res):
    if len(res) > 16:
        flags["CF"] = 1
        flags["SF"] = int(res[1])
    else :
        flags["CF"] = 0
        flags["SF"] = int(res[0])

    if int(res[-16:]) == 0:
        flags["ZF"] = 1
    else:
        flags["ZF"] = 0

#Sets only the sign and zero flags according to the bits of the given parameter
def set_flags2(res):
    flags["SF"] = int(res[0])
    if int(res[-16:]) == 0:
        flags["ZF"] = 1
    else:
        flags["ZF"] = 0

#Performs bitwise operations according to the bitwise operation and one and/or two operands
def bitwise(op1, operator, op2=0):
    if operator == "XOR":
        res = bin(int(op1, 2) ^ int(op2, 2))[2:].zfill(16)
    elif operator == "AND":
        res = bin(int(op1, 2) & int(op2, 2))[2:].zfill(16)
    elif operator == "OR":
        res = bin(int(op1, 2) | int(op2, 2))[2:].zfill(16)
    elif operator == "NOT":
        res = bin((1 << 16) - 1 - int(op1, 2))[2:].zfill(16)
    return res

#Writes every 8 bits of each instrution into the memory
for index, line in enumerate(lines):
    memory[index * 3] = line[:8]
    memory[index * 3 + 1] = line[8:16]
    memory[index * 3 + 2] = line[16:]

#Stores the the given datadata with respect to the address mode 
def store_data(address_mode, address, data):
    if address_mode == 0: # Immediate
        return;
    elif address_mode == 1: # Register
        registers[bit_to_register[operand]] = data
    elif address_mode == 2: #Indirect register
        memory[int(registers[bit_to_register[operand]], 2)] = data[:8] 
        memory[int(registers[bit_to_register[operand]], 2) + 1] = data[8:] 
    elif address_mode == 3: # Memory
        memory[int(address,2)] = data[:8]
        memory[int(address,2) + 1] = data[8:]

#Performs jump operation by changing the PC register 
def jump(operand):
    registers["PC"] = int(operand, 2) // 3
        
#Starts execution of the program from the first line and continues
#according to the value the PC register holds        
while registers["PC"] < len(lines):
    line = lines[registers["PC"]]
    opcode = format(int(line[:6], 2), 'x')
    address_mode = int(format(int(line[6:8], 2), 'x'))
    operand = line[8:]

    if opcode == "1": # HALT
        break

    elif opcode == "2": # LOAD
        registers["A"] = operand_by_adr_mode(address_mode, operand)

    elif opcode == "3":  # STORE
        store_data(address_mode, operand, registers["A"])

    elif opcode == "4":  # ADD
        res =  bin(int(registers["A"],2) + int(operand_by_adr_mode(address_mode, operand),2))[2:].zfill(16)
        registers["A"] = res
        setFlags(res)
    
    elif opcode == "5":  # SUB
        res = bin(int(registers["A"], 2) + int(bitwise(operand_by_adr_mode(address_mode,operand), "NOT"), 2) + 1)[2:].zfill(16)
        registers["A"] = res[-16:]
        setFlags(res)

    elif opcode == "6":  # INC
        res = bin(1 + int(operand_by_adr_mode(address_mode,operand),2))[2:].zfill(16)
        store_data(address_mode, operand, res)
        setFlags(res)

    elif opcode == "7":  # DEC
        res = bin(-1 + int(operand_by_adr_mode(address_mode,operand),2))[2:].zfill(16)
        store_data(address_mode, operand, res)
        setFlags(res)

    elif opcode == "8": # XOR
        registers["A"] = bitwise(registers["A"], "XOR", operand_by_adr_mode(address_mode,operand))
        set_flags2(registers["A"])

    elif opcode == "9": # AND
        registers["A"] = bitwise(registers["A"], "AND",operand_by_adr_mode(address_mode,operand))
        set_flags2(registers["A"])

    elif opcode == "a": # OR
        registers["A"] = bitwise(registers["A"], "OR", operand_by_adr_mode(address_mode,operand))
        set_flags2(registers["A"])

    elif opcode == "b": # NOT
        registers["A"] = bitwise(operand_by_adr_mode(address_mode,operand), "NOT")
        set_flags2(registers["A"])
        
    elif opcode == "c": # SHL
        if address_mode == 1: # Register
            flags["CF"] = int(registers["A"][0])
            registers["A"] = bin(int(registers["A"], 2) << 1)[2:].zfill(16)
            set_flags2(registers["A"])

    elif opcode == "d": # SHR
        if address_mode == 1: # Register
            registers["A"] = bin(int(registers["A"], 2) >> 1)[2:].zfill(16)
            set_flags2(registers["A"])

    elif opcode == "e": # NOP
        registers["PC"] += 1
        continue

    elif opcode == "f": # PUSH
        if address_mode == 1: # Register
            registers["S"] = bin(int(registers["S"], 2) - 2)[2:].zfill(16)
            memory[int(registers["S"], 2)] = registers[bit_to_register[operand]][:8]
            memory[int(registers["S"], 2) + 1] = registers[bit_to_register[operand]][8:]

    elif opcode == "10": # POP
        if address_mode == 1: # Register
            registers[bit_to_register[operand]] = memory[int(registers["S"], 2)] + memory[int(registers["S"], 2) + 1]
            memory[int(registers["S"], 2)] = "00000000"
            memory[int(registers["S"], 2) + 1] = "00000000"
            registers["S"] = bin(int(registers["S"], 2) + 2)[2:].zfill(16)

    elif opcode == "11": # CMP
        res = bin(int(registers["A"], 2) + int(bitwise(operand_by_adr_mode(address_mode,operand), "NOT"), 2) + 1)[2:].zfill(16)
        setFlags(res)

    elif opcode == "12": # JMP
        if address_mode == 0: # Register
            jump(operand)
            continue

    elif opcode == "13": # JZ, JE
        if address_mode == 0 and flags["ZF"] == 1: # Register
            jump(operand)
            continue

    elif opcode == "14": # JNZ, JNE
        if address_mode == 0 and flags["ZF"] == 0: # Register
            jump(operand)
            continue

    elif opcode == "15": # JC
        if address_mode == 0 and flags["CF"] == 1: # Register
            jump(operand)
            continue

    elif opcode == "16": # JNC 
        if address_mode == 0 and flags["CF"] == 0: # Register
            jump(operand)
            continue

    elif opcode == "17": # JA
        if address_mode == 0 and flags["SF"] == 0: # Register
            jump(operand)
            continue

    elif opcode == "18": # JAE
        if address_mode == 0 and flags["SF"] == 0 or flags["ZF"] == 1: # Register
            jump(operand)
            continue

    elif opcode == "19": # JB
        if address_mode == 0 and flags["SF"] == 1: # Register
            jump(operand)
            continue

    elif opcode == "1a": # JBE
        if address_mode == 0 and flags["SF"] == 1 or flags["ZF"] == 1: # Register
            jump(operand)
            continue
    
    elif opcode == "1b": # READ
        input_char = input()
        store_data(address_mode, operand, bin(ord(input_char))[2:].zfill(16))
        
    elif opcode == "1c": # Print
         out.write(chr(int(operand_by_adr_mode(address_mode,operand), 2)))
         out.write("\n")

    registers["PC"] += 1
