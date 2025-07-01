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

async def reset_dut(dut):
    print("Resetting DUT")
    dut.n_rst.value = 0
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    dut.n_rst.value = 1
    await Timer(10, units="ns")
    
# class testcase:
#     def __init__(self, instr_type, count, specific_instrs):
#         self.instr_type = instr_type
#         self.count = count # Number of instructions for stimulus
#         self.specific_instrs = specific_instrs # explicitly state what instructions to include
        
#     def __str__(self):
#         print(f"type = {self.instr_type}, instructions = {self.specific_instrs}")
    
    # def gen_random(self): #constrained random generator. 
        
    # def feed_case(self): #feeds the testcase directly to instr. Must be done on every clock cycle
        
    # def store_case(self): #stores the testcase to instruction memory. 
op_to_type = {
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
Rfunct_to_name = { #first entry is funct7=0, second is funct7=0x20
    Bits(uint="0", length=3) : ["add", "sub"],
    Bits(uint="1", length=3) : ["sll", "" ],
    Bits(uint="2", length=3) : ["slt", "" ],
    Bits(uint="3", length=3) : ["sltu", ""],
    Bits(uint="4", length=3) : ["xor", ""],
    Bits(uint="5", length=3) : ["srl", "sra"],
    Bits(uint="6", length=3) : ["or", ""],
    Bits(uint="7", length=3) : ["and", ""]
}
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
        self.funct7 = Bits(uint=random.choice([0, 32]), length=7) #32 would only apply to SUB and SRA
        self.opcode = Bits(uint=random.choice([int("0110011",2), int("0010011",2), int("0000011",2), int("0100011",2), int("1100011",2), 
                                            int("1101111",2), int("1100111",2), int("0110111",2), int("0010111",2), int("1110011",2)]),
                                            length=7)
        self.imm = Bits(int=random.randint(-(2**31), 2**31 - 1), length = 32)
        return self
    
    def gen_R(self): #generates a random R-type test
        if(self.funct3 != Bits(uint=0, length=3) & self.funct3 != Bits(uint=5, length=3)): #Switches funct7 for invalid instructions
            self.funct7 = Bits(uint=0, length=7)
        self.opcode = Bits(bin="0110011", length=7)
        return self
    
    def gen_R_instr(self): #generates the R-type instr
        return Bits().join([self.funct7, self.rs2, self.rs1, self.funct3, self.rd, Bits(bin='0110011', length=7)])
    
    def gen_I(self): #generates a random I-type test
        self.opcode = Bits(bin="0010011", length=7)
        if(self.funct3 == Bits(uint=1, length=3)): #valid imm for SLLI
            self.imm = Bits(uint=0, length=12)
        elif(self.funct3 == Bits(uint=5, length=3)): #valid imm for SRLI, SRAI
            self.imm = Bits(uint=(random.choice([0,1024]) + random.choice(range(0, 127))), length=12)
        return self
    
    def gen_I_instr(self): #generates the I-type instr
        return Bits().join([self.imm[0:12], self.rs1, self.funct3, self.rd, Bits(bin="0010011", length=7)])
    
    def bin(self): #generates the binary instruction
        match op_to_type[self.opcode]:
            case "R-Type":
                return (self.gen_R_instr()).bin
            case "I-Type":
                return (self.gen_I_instr()).bin
    
    def decode(self):
        #find opcode/instruction type. Only R and I currently
        print(f"Instruction type: {op_to_type[self.opcode]}")
        match op_to_type[self.opcode]:
            case "R-Type":
                match self.funct7.uint:
                    case 0:
                        print(f"Name: {Rfunct_to_name[self.funct3][0]}")
                    case 32:
                        print(f"Name: {Rfunct_to_name[self.funct3][1]}")
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint} rs2={self.rs2.uint}")
                print(f"Instruction: {(self.gen_R_instr()).bin} \n")
            case "I-Type": #note: sltiu will be printed as sltui    
                if(self.imm.int > 1024 & (self.funct3.uint == 5)): #srai special case
                    print(f"Name: srai")
                else:
                    print(f"Name: {Rfunct_to_name[self.funct3][0] + "i"}")
                actual_imm = self.imm[0:12] #sanity check
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={actual_imm.int}")
                print(f"Instruction: {(self.gen_I_instr()).bin} \n")

# @cocotb.test()
#NOTE: This test requires fetch_reg_file/DUT_instr to be commented out, due to race conditions between inserting 
#the instruction through this testbench and fetching from the instruction
async def adder_randomized_test(dut):
    """Test for adding 2 random numbers, reset on overflow"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut)
    # print("Available DUT signals:")
    # print(dir(dut))  # Shows top-level signals
    # Check if register file is accessible
    try:
        print(f"RF accessible: {dut.DUT_RF}")
        print(f"RF.RF accessible: {dut.DUT_RF.RF}")
        print(f"RF.R[3] accessible: {dut.DUT_RF.RF[3].value}\n")
    except:
        print("Register file not accessible at this path")
    # """Will consist of only add and addi instructions"""
    for i in range(10000):
        reg1 = random.randint(1, 31) #not using getrandbits to exclude x0
        reg2 = random.randint(1, 31)
        reg_dest = random.randint(1, 31)
        
        #bit-width preservation for instruction fields
        rs1 = Bits(uint=reg1, length=5) #x0-31 randomly chosen
        rs2 = Bits(uint=reg2, length=5) #x0-31 randomly chosen
        rd  = Bits(uint=reg_dest, length=5)
        funct3 = Bits(bin='000', length=3) #add instruction to ALU. add + addi
        
        #generating add vs addi
        instr_type = random.randint(0, 5) #0 is R, else is I
        
        #register/immediate values to be used in add instructions. 
        prior_rs1 = dut.DUT_RF.RF[reg1].value.signed_integer
        prior_rs2 = dut.DUT_RF.RF[reg2].value.signed_integer
        prior_rd = dut.DUT_RF.RF[reg_dest].value.signed_integer
        
        
        if(instr_type == 0): #R-type instruction. Need == 0 instead of ~ for some resaon
            expected = prior_rs1 + prior_rs2
            funct7 = Bits(bin='0000000', length=7)
            opcode = Bits(bin='0110011', length=7)
            instr = Bits().join([funct7, rs2, rs1, funct3, rd, opcode])
            print(f"Test {i}: R-type add")
            print(f"rd=x{reg_dest}={prior_rd}, rs1=x{reg1}={prior_rs1}, rs2=x{reg2}={prior_rs2}")
            
            
        else: #I-type instruction
            opcode = Bits(bin="0010011", length=7) 
            imm = Bits(int=random.randint(-(2)**11, 2**11 - 1), length=12) #immediate field
            instr = Bits().join([imm, rs1, funct3, rd, opcode])
            print(f"Test {i}: I-type addi")
            print(f"rd=x{reg_dest}={prior_rd}, rs1=x{reg1}={prior_rs1}, imm={imm.int}")
            imm_out = dut.imm_out.value.signed_integer #immediate value stored in dut
            expected = prior_rs1 + imm.int
            
        print(f"Instruction bits: {instr.bin}")
            
        dut.instr.value = int(instr.bin, 2) #feed instruction 

        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")
        actual = dut.DUT_RF.RF[reg_dest].value.signed_integer
                
        if((expected >= MAX_32B_signed) | (expected <= MIN_32B_signed)): #Overflow check
            print(f"Overflow detected: {expected}")
            await reset_dut(dut)
        else:
            if(instr_type == 0): #R-type
                assert (expected) == (actual), ( #add/addi instruction is incorrect
                    f"Randomized test failed with: x{reg1} + x{reg2} = x{reg_dest}\n"
                    f"{prior_rs1} + {prior_rs2} = {expected}, not {actual}"
                )
            else: #I-type
                assert (expected) == (actual), (
                    f"Randomized test failed with: x{reg1} + {imm_out} = x{reg_dest}\n"
                    f"{prior_rs1} + {imm_out} = {expected}, not {actual}"
                )       
        print(f"rd = {actual}\n")
        # print(f"expected:{expected} got: {dut.DUT_RF.RF[reg_dest]}")

@cocotb.test()
async def R_I_OOP_test(dut):
    """Test for R-type and I-type Instructions"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut)
    #Testcase
    for i in range(100):
        test = instruction()
        test = instruction.gen_random(test) #constrained random generation
        instr_type = random.choice([0,1])  #randomize instruction type
        if(instr_type == 0):
            instr = test.gen_R()
        else:
            instr = test.gen_I()
        instruction.decode(instr)
        dut.instr.value = int(instr.bin(), 2)
        
        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")
        