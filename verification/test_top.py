import os
import random
import sys
from pathlib import Path

import cocotb
from cocotb.triggers import FallingEdge, Timer, RisingEdge, ClockCycles
from cocotb.clock import Clock

from bitstring import Bits, BitArray, pack

MAX_32B_signed = 2**31 - 1
MIN_32B_signed = -(2**31)

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

def lshift(val, n): return (val % 0x100000000) << n #logical left shift


async def reset_dut(dut):
    print("Resetting DUT \n")
    dut.n_rst.value = 0
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    dut.n_rst.value = 1
    await Timer(10, units="ns")
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
    Bits(bin="0000011", length=7) : "I-Type",
    Bits(bin="0100011", length=7) : "S-Type",
    Bits(bin="1100011", length=7) : "B-Type",
    Bits(bin="1101111", length=7) : "J-Type",
    Bits(bin="1100111", length=7) : "I-Type",
    Bits(bin="0110111", length=7) : "U-Type",
    Bits(bin="0010111", length=7) : "U-Type",
    Bits(bin="1110011", length=7) : "I-Type"
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
    # def __init__(self):
    #     self.rd1 = None
    #     self.rd2 = None
    #     self.out = None
    #     self.imm = None
    def reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.signed_integer
    def unsigned_reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.integer
    def imm(DUT):
        return DUT.imm_out.value.signed_integer
    def unsigned_imm(DUT):
        return DUT.imm_out.value.integer
    def control(DUT):
        signals = DUT.debug_control #concate of control sigs
        print(f"Control: {signals}")
        print(f"ALUOp: {DUT.ALUOp}")
        print(f"ALU_Operation: {ALU_Operation[DUT.ALU_Operation.value.integer]}")
        print(f"ALU_Control instr: {DUT.DUT5.instr.value}")
        # print(f"RegWr: {signals[1]}")
    
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
        if((Rfunct3[self.funct3][0] != "add") & (Rfunct3[self.funct3][0] != "srl")): #Switches funct7 for invalid instructions
            self.funct7 = Bits(uint="0", length=7)
        if ((Rfunct3[self.funct3][0] == "sll") | (Rfunct3[self.funct3][0] == "srl")): #avoid illegal instruction: negative shift
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
        return Bits().join([self.imm[0:12], self.rs1, self.funct3, self.rd, Bits(bin="0010011", length=7)])
    
    def bin(self): #generates the binary instruction
        match op[self.opcode]:
            case "R-Type":
                return (self.gen_R_instr()).bin
            case "I-Type":
                return (self.gen_I_instr()).bin
    
    def decode(self, index): #prints instr-type, name, register nums, imm value, and instruction binary
        #find opcode/instruction type. Only R and I currently
        print(f"Test {index}")
        print(f"Instruction type: {op[self.opcode]}")
        match op[self.opcode]:
            case "R-Type":
                match self.funct7.uint:
                    case 0:
                        print(f"Name: {Rfunct3[self.funct3][0]}") 
                    case 32:
                        print(f"Name: {Rfunct3[self.funct3][1]}") #only place that uses self.funct3[1]
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint} rs2={self.rs2.uint}")
            case "I-Type": 
                if((Rfunct3[self.funct3][0] == "srl") & (self.imm.int > 1024)): #srai special case
                    print(f"Name: srai")
                elif(Rfunct3[self.funct3][0] == "sltu"): #sltiu is unsigned
                    print(f"Name: sltiu")
                    print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={(self.imm[0:12]).uint}")
                    return
                else:
                    print(f"Name: {Rfunct3[self.funct3][0] + "i"}")
                actual_imm = self.imm[0:12] #sanity check
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={actual_imm.int}")

        print(f"Instruction: {(self.bin())}")
                
    def model_rd(self, prior): #returns the expected rd value
        #prior always has prior[0] = rd, prior[1] = rs1, and prior[2] can be rs2, imm, or none
        rd1 = (prior[1])
        # print(rd1)
        match op[self.opcode]: #setting rd2 operand
            case "R-Type":
                if(((Rfunct3[self.funct3][0] == "srl") | (Rfunct3[self.funct3][0] == "sll")) ): # only shift lower 5 bits.
                    field = (prior[2]) & 0x1F
                else:
                    field = prior[2]
            case "I-Type": 
                if (Rfunct3[self.funct3][0] == "sltu"):
                    field = (self.imm[0:12]).uint
                elif(((Rfunct3[self.funct3][0] == "srl") | (Rfunct3[self.funct3][0] == "sll")) ): # only shift lower 5 bits for srl, sll, srai.
                    field = self.imm.int & 0x1F
                else:
                    field = (self.imm[0:12]).int
        try:
            match Rfunct3[self.funct3][0]:
                case "add":
                    if((self.funct7.uint == 32) & (op[self.opcode] == "R-Type")): return rd1 - field #sub
                    else: return rd1 + field 
                case "sll": return lshift(rd1, field) #rd1 << field 
                case "slt": return 1 if (binary_to_signed(rd1) < binary_to_signed(field)) else 0
                case "sltu": return 1 if (rd1 < field) else 0
                case "xor": return rd1 ^ field
                case "srl": #NOTE: python's >> is arithmetic
                    if(self.funct7.uint == 32):  return rd1 >> (field) #arithmetic
                    else: return rshift(rd1, field) #logical
                case "or": return (rd1 | field)
                case "and": return (rd1 & field)
                case default: print(f"Model Error")
        except Exception as e:
            print(f"Error occured on {Rfunct3[self.funct3][0]}. Probably negative shift error \n {e}")
            return 0
            
    def monitor(self, DUT, operation): #returns 3 arguments read from DUT
        #will match the order of fields in instructions: add rd, rs1, rs2
        #operation: 
        # "pre"  : won't print imm 
        # "post" : will print imm
        rs1 = dut_fetch.reg(DUT, self.rs1)
        rs2 = dut_fetch.reg(DUT, self.rs2)
        unsigned_rs2 = dut_fetch.unsigned_reg(DUT, self.rs2)
        unsigned_rs1 = dut_fetch.unsigned_reg(DUT, self.rs1)
        rd = dut_fetch.reg(DUT, self.rd)
        imm = dut_fetch.imm(DUT)
        unsigned_imm = dut_fetch.unsigned_imm(DUT) & 0xFFF
        
        if(Rfunct3[self.funct3][0] == "sltu" ): #unsigned conversion case
            rs1 = unsigned_rs1
            rs2 = unsigned_rs2
            imm = unsigned_imm
        elif(((Rfunct3[self.funct3][0] == "srl") | (Rfunct3[self.funct3][0] == "sll")) ): #shift instructions
              imm &= 0x1F #only [0:4] bits count towards shift in RV spec
        
        if (op[self.opcode] == "R-Type"):
            if(operation == "post"): print("Actual: ", end="")
            elif(operation == "pre"): print("Pre-instruction: ", end="")
            print(f"rd={rd}, rs1={rs1}, rs2={rs2}")
            return [rd, rs1, rs2]
        elif (op[self.opcode] == "I-Type"):
            if(operation == "post"): #irrelevant prior imm field ignored
                print(f"Actual: rd={rd}, rs1={rs1}, imm={imm}")
                return [rd, rs1, imm]
            elif(operation == "pre"):
                print(f"Pre-instruction: rd={rd}, rs1={rs1}")
                return [rd, rs1]
        
    def checker(self, expected, actual, dut): #NOTE: doesn't feature overflow handling due to "await"/async property
        print(f"Expected rd: {expected}")
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
            print(f"unsigned: final={uint_final}, rd1={uint_rs1}, imm={uint_imm}\n")
        else:
            print(f"Success! \n")
        return
    
    def feed(self, dut): #feeds instruction directly to DUT (beware of race conditions if fetch_reg)
        dut.instr_cocotb.value = int(self.bin(), 2)        

@cocotb.test()
async def R_I_OOP_test(dut):
    """Test for R-type and I-type Instructions"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut) 
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
        
        expected = instr.model_rd(prior) #expected rd value
        actual = instr.monitor(dut, "post") #post-instruction rs1, rs2, rd, and/or imm values of DUT  
        
        if (expected.bit_length() > 64): #how to make this it's own function while also printing?
            print(f"Severe overflow detected: {expected.bit_length()} bits") #async def + print is weird
            await reset_dut(dut)
        elif((expected >= MAX_32B_signed) | (expected <= MIN_32B_signed)): #Overflow check
            print(f"Overflow detected: {expected}")
            await reset_dut(dut)
        else:
            instr.checker(expected, actual, dut)
        