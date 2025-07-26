import os
import random
import sys
from pathlib import Path
import logging

import cocotb
from cocotb.triggers import FallingEdge, Timer, RisingEdge, ClockCycles
from cocotb.clock import Clock

from bitstring import Bits, BitArray, pack

MAX_32B_signed = 2**31 - 1
MIN_32B_signed = -(2**31)
SHIFT_MASK = 0x1F
BYTE_MASK = 0x000000FF
HALF_MASK = 0x0000FFFF
WORD_MASK = 0xFFFFFFFF #Used for sll/i
NUM_WORDS = 32

class node(): #to be used for linked list
    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next_node = next_node
    def set_next(self, next_node):
        self.next_node = next_node

async def generate_clock(dut):
    """Generate clock pulses."""

    for cycle in range(1000000):
        dut.clk.value = 0
        await Timer(10, units="ns")
        dut.clk.value = 1
        await Timer(10, units="ns")

def binary_to_signed(val):
    if(val >= 2**31):
        val -= 2**32 #converts to signed
    return val

def signed_to_binary(val):
    return val & ((1 << 32) - 1) #2's complement

def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n #logical right shift

def lshift(val, n): return (val % 0x100000000) << n #logical left shift. This is not preserving sign. 

async def reset_dut(dut):
    print("Resetting DUT \n")
    dut.n_rst.value = 0
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    dut.n_rst.value = 1
    await Timer(10, units="ns")
    # dut = dut_fetch.randomize_RF(dut)
    # dut = dut_fetch.randomize_data(dut)
    return #dut

async def randomize_rf(dut, N_bits):
    print("Randomizing DUT \n")
    dut = dut_fetch.randomize_RF(dut, N_bits)
    await RisingEdge(dut.clk) 
    await Timer(10, units="ns")
    return 

async def randomize_data(dut, N_bits):
    print("Randomizing DUT \n")
    dut = dut_fetch.randomize_data(dut, N_bits)
    await RisingEdge(dut.clk) 
    await Timer(10, units="ns")
    return 
async def random_reset_dut(dut, N_bits):
    await reset_dut(dut)
    await randomize_data(dut, N_bits)
    await randomize_rf(dut, N_bits)
    return
# class testcase:
#     def __init__(self, instr_type, count, specific_instrs):
#         self.instr_type = instr_type
#         self.count = count # Number of instructions for stimulus
#         self.specific_instrs = specific_instrs # explicitly state what instructions to include
        
#     def __str__(self):
#         print(f"type = {self.instr_type}, instructions = {self.specific_instrs}")
    
    # def feed_case(self): #feeds the testcase directly to instr. Must be done on every clock cycle
        
    # def store_case(self): #stores the testcase to instruction memory. 
op = {
    Bits(bin="0110011", length=7) : "R-Type",
    Bits(bin="0010011", length=7) : "I-Type",
    Bits(bin="0000011", length=7) : "I-Type Load", #load, change name?
    Bits(bin="0100011", length=7) : "S-Type", 
    Bits(bin="1100011", length=7) : "B-Type",
    Bits(bin="1101111", length=7) : "J-Type",
    Bits(bin="1100111", length=7) : "I-Type",
    Bits(bin="0110111", length=7) : "U-Type",
    Bits(bin="0010111", length=7) : "U-Type",
    # Bits(bin="1110011", length=7) : "I-Type" #irrelevant for this implementation.
}

Rfunct3 = { #first entry is funct7=0, second is funct7=0x20
    #how to change this to something where I don't need to specify [0] normally?
    #gut reaction: linked list
    Bits(uint="0", length=3) : ["add", "sub"],
    Bits(uint="1", length=3) : ["sll"],
    Bits(uint="2", length=3) : ["slt"], 
    Bits(uint="3", length=3) : ["sltu"],
    Bits(uint="4", length=3) : ["xor"], 
    Bits(uint="5", length=3) : ["srl", "sra"],
    Bits(uint="6", length=3) : ["or"], 
    Bits(uint="7", length=3) : ["and"],
}

Mfunct3 = { #load and store funct3 conversion. NOTE: store only has 0,1,2, for funct3
    Bits(uint="0", length=3) : ["lb", "sb", "Byte"],
    Bits(uint="1", length=3) : ["lh", "sh", "Half"],
    Bits(uint="2", length=3) : ["lw", "sw", "Word"],
    Bits(uint="4", length=3) : ["lbu", "Unsigned-Byte"],
    Bits(uint="5", length=3) : ["lhu", "Unsigned-Half"]
}

ALU_Operation = {
    int("0010", 2) : "ADD",
    int("0110", 2) : "SUB",
    int("0000", 2) : "AND",
    int("0001", 2) : "OR",
    int("0011", 2) : "XOR",
    int("0100", 2) : "SLL",
    int("0101", 2) : "SRL",
    int("0111", 2) : "SRA",
    int("1000", 2) : "SLT",
    int("1001", 2) : "SLTU",
    int("1100", 2) : "SLTI",
    int("1101", 2) : "SLTUI"
}

class dut_fetch():
    def __init__(DUT): #maybe have access to all submodules?
        DUT.rf = DUT.DUT_RF
        
    def reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.signed_integer
    def set_reg(DUT, bits_index, value): #sets a single register value, returns the DUT
        DUT.DUT_RF.RF[bits_index.uint].value = value
        return DUT
    
    def unsigned_reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.integer
    def imm(DUT):
        return DUT.imm_out.value.signed_integer
    def unsigned_imm(DUT):
        return DUT.imm_out.value.integer
    def control(DUT):
        signals = DUT.debug_control #concate of control sigs
        # print(f"Control: {signals}")
        print(f"ALUOp: {DUT.ALUOp}")
        print(f"ALU_Operation: {ALU_Operation[DUT.ALU_Operation.value.integer]}")
        print(f"ALU_Control instr: {DUT.DUT5.instr.value}")
        print(f"MemtoReg: {DUT.MemtoReg}")
        print(f"MemRead: {DUT.MemRead}")
        print(f"RegWr: {DUT.RegWr}")
        print(f"MemWr: {DUT.MemWr}")
        # print(f"RegWr: {signals[1]}")
    def memory(DUT, rs1, imm):
        return DUT.DUT_Data.data_memory[(rs1.uint + imm.int)>>2].value.signed_integer 
    def unsigned_memory(DUT, rs1, imm):
        return DUT.DUT_Data.data_memory[(rs1.uint + imm.int)>>2].value.integer #for lbu and lhu?
    def randomize_RF(DUT, N_bits):
        for i in range(32):
            DUT.DUT_RF.RF[i].value = random.getrandbits(N_bits)
            # print(DUT.DUT_RF.RF[i].value.integer)
        return DUT
    
    def randomize_data(DUT, N_bits):
        for i in range(NUM_WORDS):
            DUT.DUT_Data.data_memory[i].value = random.getrandbits(N_bits)
            # print(DUT.DUT_Data.data_memory[i].value.integer)
        return DUT
        
class instruction():
    def __init__(self):
        # self.instr_type = instr_type
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.funct3 = None
        self.funct7 = None
        self.opcode = None
        self.imm = None
        
    def gen_random(self): #generates all possible fields
        self.rs1 = Bits(uint=random.randint(1, 31), length=5) #x1-31 randomly chosen
        self.rs2 = Bits(uint=random.randint(1, 31), length=5) #x1-31 randomly chosen
        self.rd  = Bits(uint=random.randint(1, 31), length=5)
        self.funct3 = Bits(uint=random.getrandbits(3), length=3)
        self.funct7 = Bits(uint=random.choice(["0", "32"]), length=7) #32 would only apply to SUB and SRA
        self.opcode = Bits(uint=random.choice([int("0110011",2), int("0010011",2), int("0000011",2), int("0100011",2), int("1100011",2), 
                                            int("1101111",2), int("1100111",2), int("0110111",2), int("0010111",2), int("1110011",2)]),
                                            length=7)
        self.imm = Bits(int=random.randint(-(2**31), 2**31 - 1), length = 32)
        return self
    
    def gen_R(self, dut): #generates a random R-type test
        self = self.gen_random()
        if((Rfunct3[self.funct3][0] != "add") and (Rfunct3[self.funct3][0] != "srl")): #Switches funct7 for invalid instructions
            self.funct7 = Bits(uint="0", length=7)
        if ((Rfunct3[self.funct3][0] == "sll") or (Rfunct3[self.funct3][0] == "srl")): #avoid illegal instruction: negative shift
            if(dut_fetch.reg(dut, self.rs2) <= 0): 
                print("Illegal negative shift detected: swapping instruction")
                self.funct7 = Bits(uint="0", length=7) #ignore sub because error for some reason
                self.funct3 = Bits(uint=random.choice([0,2,3,4,6,7]), length=3) #switch to everything other than shift 
        self.opcode = Bits(bin="0110011", length=7)
        return self
    
    def gen_R_instr(self): #generates the R-type instr
        return Bits().join([self.funct7, self.rs2, self.rs1, self.funct3, self.rd, Bits(bin='0110011', length=7)])
    
    def gen_I(self): #generates a random I-type test
        self = self.gen_random()
        self.opcode = Bits(bin="0010011", length=7)
        if(Rfunct3[self.funct3][0] == "sll"): #valid imm for SLLI
            self.imm = Bits(int=random.choice(range(0,31)), length=12)
        elif(Rfunct3[self.funct3][0] == "srl"): #valid imm for SRLI, SRAI
            self.imm = Bits(int=(random.choice([0,1024]) + random.choice(range(0, 127))), length=12)
            if(self.imm.int > 1024):
                self.funct7 = Bits(uint="32", length=7)
            else:
                self.funct7 = Bits(uint="0", length=7)
        return self
    
    def gen_I_instr(self): #generates the I-type instr
        return Bits().join([self.imm[0:12], self.rs1, self.funct3, self.rd, self.opcode])
    
    def gen_I_load(self, DUT): #generates a random I-type load test
        self = self.gen_random()
        self.opcode = Bits(bin="0000011", length=7)
        self.funct3 = Bits(uint=random.choice([0,1,2,4,5]), length=3)
        match Mfunct3[self.funct3][0]: #natural alignment constraint
            case "lb": 
                self.imm = Bits(uint=random.choice(range(32)), length=12)
            case "lh": 
                self.imm = Bits(uint=random.choice(range(0,32,2)), length=12) 
                DUT = dut_fetch.set_reg(DUT, self.rs1, random.choice(range(0,32,2)))
            case "lw": 
                self.imm = Bits(uint=random.choice(range(0,32,4)), length=12) 
                DUT = dut_fetch.set_reg(DUT, self.rs1, random.choice(range(0,32,4)))
            case "lbu": self.imm = Bits(uint=random.choice(range(32)), length=12) 
            case "lhu": 
                self.imm = Bits(uint=random.choice(range(0,32,2)), length=12) 
                DUT = dut_fetch.set_reg(DUT, self.rs1, random.choice(range(0,32,2)))
        return self
    
    def gen_S(self, DUT):
        self = self.gen_random()
        self.opcode = Bits(bin="0100011", length=7)
        self.funct3 = Bits(uint=random.choice([0,1,2]), length=3)
        match Mfunct3[self.funct3][1]: #natural alignment constraint
            case "sb": self.imm = Bits(uint=random.choice(range(32)), length=12)
            case "sh": 
                self.imm = Bits(uint=random.choice(range(0,32,2)), length=12) 
                DUT = dut_fetch.set_reg(DUT, self.rs1, random.choice(range(0,32,2)))
            case "sw": 
                self.imm = Bits(uint=random.choice(range(0,32,4)), length=12) 
                DUT = dut_fetch.set_reg(DUT, self.rs1, random.choice(range(0,32,4)))
        return self
    
    def gen_S_instr(self): #NOTE: Bits is MSB first and doesn't include end, thus imm[0:7] => imm[11:5] in RTL
        return Bits().join([self.imm[0:7], self.rs2, self.rs1, self.funct3, self.imm[7:12], Bits(bin="0100011", length=7)])
    
    def bin(self): #generates the binary instruction
        match op[self.opcode]:
            case "R-Type":
                return (self.gen_R_instr()).bin
            case "I-Type":
                return (self.gen_I_instr()).bin
            case "I-Type Load":
                return (self.gen_I_instr()).bin
            case "S-Type":
                return (self.gen_S_instr()).bin
    
    def decode(self, test_num): #prints instr-type, name, register nums, imm value, and instruction binary
        #find opcode/instruction type. Only R and I currently
        print(f"Test {test_num}")
        print(f"Instruction type: {op[self.opcode]}")
        word_imm = self.imm[0:12] #sanity check
        match op[self.opcode]:
            case "R-Type":
                match self.funct7.uint:
                    case 0:
                        print(f"Name: {Rfunct3[self.funct3][0]}") 
                    case 32:
                        print(f"Name: {Rfunct3[self.funct3][1]}") #only place that uses self.funct3[1]
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint} rs2={self.rs2.uint}")
            case "I-Type": 
                if((Rfunct3[self.funct3][0] == "srl") and (self.imm.int > 1024)): #srai special case
                    print(f"Name: srai")
                elif(Rfunct3[self.funct3][0] == "sltu"): #sltiu is unsigned
                    print(f"Name: sltiu")
                    print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={word_imm.uint}")
                    return
                else:
                    print(f"Name: {Rfunct3[self.funct3][0] + "i"}")
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={word_imm.int}")
            case "I-Type Load":
                print(f"Name: {Mfunct3[self.funct3][0]}")
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={word_imm.int}")
            case "S-Type":
                print(f"Name: {Mfunct3[self.funct3][1]}")
                print(f"Registers: rs1={self.rs1.uint}, rs2={self.rs2.uint}, Imm={word_imm.int}")
        if(len(self.bin()) != 32):
            print(f"Invalid instruction length: {len(self.bin())} != 32")
        print(f"Instruction: {(self.bin())}")
                
    def model(self, prior): #returns the expected rd value
        #prior always has prior[0] = rd, prior[1] = rs1, and prior[2] can be rs2, imm, or none
        #load: prior = [rd, M, rs1, imm]
        #store: prior =  [M, rs1, imm, rs2] ("pre" has [rs1, rs2])
        rd1 = (prior[1]) #only used for R-type
        # DUT values shouldn't be extracted here, only expected test values.
        match op[self.opcode]: #setting rd2 operand
            case "R-Type":
                if(((Rfunct3[self.funct3][0] == "srl") or (Rfunct3[self.funct3][0] == "sll")) ): # only shift lower 5 bits.
                    field = (prior[2]) & SHIFT_MASK
                else:
                    field = prior[2]
            case "I-Type": 
                if (Rfunct3[self.funct3][0] == "sltu"):
                    field = (self.imm[0:12]).uint
                elif(((Rfunct3[self.funct3][0] == "srl") or (Rfunct3[self.funct3][0] == "sll")) ): # only shift lower 5 bits for srl, sll, srai.
                    field = self.imm.int & SHIFT_MASK
                else:
                    field = (self.imm[0:12]).int
            case "I-Type Load": #value to be loaded into rd
                match Mfunct3[self.funct3][0]: #how to differentiate between sign-extend and zero fill?
                    case "lb" : field = prior[1] & BYTE_MASK
                    case "lh" : field = prior[1] & HALF_MASK
                    case "lw" : field = prior[1]
                    case "lbu": field = prior[1] & BYTE_MASK
                    case "lhu": field = prior[1] & HALF_MASK
            case "S-Type":
                match Mfunct3[self.funct3][1]: #value to be stored in memory
                    case "sb" : field = prior[1] & BYTE_MASK
                    case "sh" : field = prior[1] & HALF_MASK
                    case "sw" : field = prior[1]
        try:
            if(op[self.opcode] == "R-Type" or op[self.opcode] == "I-Type"):
                match Rfunct3[self.funct3][0]: #All R-type and their I-type counterparts
                    case "add":
                        if((self.funct7.uint == 32) and (op[self.opcode] == "R-Type")): return rd1 - field #sub
                        else: return rd1 + field 
                    case "sll": return binary_to_signed(lshift(rd1, field) & WORD_MASK) #rd1 << field. Prevents all overflow with mask.
                    case "slt": return 1 if (binary_to_signed(rd1) < binary_to_signed(field)) else 0
                    case "sltu": return 1 if rd1 < field else 0
                    case "xor": return rd1 ^ field
                    case "srl": #NOTE: python's >> is arithmetic
                        if(self.funct7.uint == 32):  return rd1 >> (field) #arithmetic
                        else: return binary_to_signed(rshift(rd1, field)) #logical
                    case "or": return (rd1 | field)
                    case "and": return (rd1 & field)
                    case default: print(f"Model Error")
            elif(op[self.opcode] == "I-Type Load" or op[self.opcode] == "S-Type"):
                return field
        except Exception as e:
            print(f"Error occured on {Rfunct3[self.funct3][0]}. Probably negative shift error \n {e}")
            return 0
            
    def monitor(self, DUT, operation): #returns 3 arguments read from DUT
        #will match the order of fields in instructions: add rd, rs1, rs2
        #operation: 
        # "pre"  : won't print imm 
        # "post" : will print imm
        #NOTE: async to clk on S-Type
            #Problem: This makes monitor and its objects a coroutine, which then disallows instr.model to iterate through "prior"
        rd1 = dut_fetch.reg(DUT, self.rs1)
        rd2 = dut_fetch.reg(DUT, self.rs2)
        unsigned_rd2 = dut_fetch.unsigned_reg(DUT, self.rs2)
        unsigned_rd1 = dut_fetch.unsigned_reg(DUT, self.rs1)
        rd = dut_fetch.reg(DUT, self.rd)
        imm = dut_fetch.imm(DUT)
        unsigned_imm = dut_fetch.unsigned_imm(DUT) & 0xFFF
        match Rfunct3[self.funct3][0]: #This should only apply to R + I type.
            case "sltu":
                rd1 = unsigned_rd1
                rd2 = unsigned_rd2
                imm = unsigned_imm
            case "srl": 
                imm &= SHIFT_MASK #only [0:4] bits count towards shift in RV spec
                rd2 &= SHIFT_MASK
            case "sll": 
                imm &= SHIFT_MASK 
                rd2 &= SHIFT_MASK
        match op[self.opcode]:
            case "R-Type":
                if(operation == "post"): print("Actual: ", end="")
                elif(operation == "pre"): print("Pre-instruction: ", end="")
                print(f"rd={rd}, rd1={rd1}, rd2={rd2}")
                return [rd, rd1, rd2]
            case "I-Type":
                if(operation == "post"): #irrelevant prior imm field ignored
                    print(f"Actual: rd={rd}, rd1={rd1}, imm={imm}")
                    return [rd, rd1, imm]
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, rd1={rd1}")
                    return [rd, rd1]
            case "I-Type Load": 
                memory = dut_fetch.memory(DUT, self.rs1, self.imm) #called inside here to avoid calling during other instructions (index error)
                if(operation == "post"):
                    print(f"Actual: rd={rd}, M[{rd1}(rd1)+{imm}(imm)]={memory}")
                    return [rd, memory, rd1, imm]
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, M[{rd1}(rd1)+{self.imm}(imm)]={memory}") #no immediate displayed here, less information available
                    print(f"Word-Address:{(rd1 + self.imm.int)>>2}, Byte-Address:{(rd1 + self.imm.int)}")
                    return [rd, memory, rd1]
            case "S-Type": #manually clk for memory to be written?
                memory = dut_fetch.memory(DUT, self.rs1, self.imm)
                if(operation == "post"):
                    print(f"Actual: M={memory}, rd1={rd1}, imm={imm}, rd2={rd2}")
                    return [memory, rd1, imm, rd2]
                elif(operation == "pre"):
                    print(f"Pre-instruction: M={memory}, rd1={rd1}, rd2={rd2} ")
                    print(f"Word-Address:{(rd1 + self.imm.int)>>2}, Byte-Address:{(rd1 + self.imm.int)}")
                    return [rd1, rd2] #no imm value to obtain before clk 
    def checker(self, expected, actual, dut): #NOTE: doesn't feature overflow handling due to "await"/async property
        match op[self.opcode]:
            case "R-Type": print(f"Expected rd: {expected}")
            case "I-Type": print(f"Expected rd: {expected}")
            case "I-Type Load": print(f"Expected rd: {expected}")
            case "S-Type": print(f"Expected Memory: {expected}")
            
        if(expected) != (actual[0]):
            print(f"Instruction Failed")
            dut_fetch.control(dut)
            rs1 = dut_fetch.reg(dut, self.rs1)
            imm = dut_fetch.imm(dut)
            final = dut_fetch.reg(dut, self.rd)
            uint_rs1 = dut_fetch.unsigned_reg(dut, self.rs1)
            uint_imm = dut_fetch.unsigned_imm(dut)
            uint_final = dut_fetch.unsigned_reg(dut, self.rd)
            
            print(f"final={final}, rd1={rs1}, imm={imm}")
            print(f"unsigned: final={uint_final}, rd1={uint_rs1}, imm={uint_imm}")
            
            if(op[self.opcode] == "I-Type Load" or op[self.opcode] == "S-Type"):
                memory = dut_fetch.memory(dut, self.rs1, self.imm)
                print(f"memory={bin(memory)}, word_data={dut.DUT_Data.word_data}")
                print(f"data_read: {dut.data_read}, write_data:{dut.write_data}")
                print(f"Binary: expected={bin(expected)}, actual={bin(actual[0])}")
            print("\n")
        else:
            print(f"Success! \n")
        return
    
    def feed(self, dut): #feeds instruction directly to DUT (beware of race conditions if fetch_reg)
        dut.instr_cocotb.value = int(self.bin(), 2)        

# @cocotb.test()
async def R_I_OOP_test(dut):
    """Test for R-type and I-type Instructions"""
    cocotb.start_soon(generate_clock(dut))
    await random_reset_dut(dut, 32)
    
    for i in range(10000):
        test = instruction()
        instr_type = random.choice([0,1])  #randomize instruction type
        if(instr_type == 0):
            instr = test.gen_R(dut)
        else:
            instr = test.gen_I()
            
        instruction.decode(instr, i)
        
        instr.feed(dut)
        
        prior = instr.monitor(dut, "pre") #prior rs1, rs2, rd register values of DUT

        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")
        
        expected = instr.model(prior) #expected rd value
        actual = instr.monitor(dut, "post") #post-instruction rs1, rs2, rd, and/or imm values of DUT  
        
        if (expected.bit_length() > 64): #how to make this it's own function while also printing?
            print(f"Severe overflow detected: {expected.bit_length()} bits") #async def + print is weird
            await random_reset_dut(dut)
        elif((expected > MAX_32B_signed) or (expected < MIN_32B_signed)): #Overflow check. How to make expected signed for sll/i?
            print(f"Overflow detected: {expected} \n") 
        else:
            instr.checker(expected, actual, dut)

@cocotb.test()
async def Memory_instr_test(dut): #naive same testbench format as R & I type
    """Test for load and store instructions"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut)
    await randomize_data(dut, 32) 
    
    for i in range(10000):
        await randomize_rf(dut, 5) 
        
        test = instruction()
        instr_type = random.choice([0,1])
        if(instr_type == 0):
            instr = test.gen_I_load(dut)
        else:
            instr = test.gen_S(dut)

        instruction.decode(instr, i)
        
        instr.feed(dut)
        
        prior = instr.monitor(dut, "pre") #prior rs1, rs2, rd register values of DUT

        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")        
        
        expected = instr.model(prior) #expected rd value
        actual = instr.monitor(dut, "post") #post-instruction rs1, rs2, rd, and/or imm values of DUT  
        instr.checker(expected, actual, dut)   