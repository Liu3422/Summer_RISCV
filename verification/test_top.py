import os
import random
import sys
from pathlib import Path
import logging

from .testbench_components import * #relative import?

@cocotb.test()
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
        tb = testcase(instr, dut)    
        tb.decode(i)
        
        tb.feed()
        
        prior = tb.monitor("pre") #prior rs1, rs2, rd register values of DUT

        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")
        
        expected = tb.model(prior) #expected rd value
        actual = tb.monitor("post") #post-instruction rs1, rs2, rd, and/or imm values of DUT  
        
        if (expected.bit_length() > 64): #how to make this it's own function while also printing?
            print(f"Severe overflow detected: {expected.bit_length()} bits") #async def + print is weird
            await random_reset_dut(dut)
        elif((expected > MAX_32B_signed) or (expected < MIN_32B_signed)): #Overflow check
            print(f"Overflow detected: {expected} \n") 
        else:
            tb.checker(expected, actual)

@cocotb.test()
async def Memory_instr_test(dut): 
    """Test for load and store instructions"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut)
    await randomize_data(dut, 32) 
    await randomize_rf(dut, 11) #11 = Num bits in addr - 1 
    
    for i in range(10000):
        test = instruction()
        instr_type = random.choice([0,1])
        if(instr_type == 0):
            (instr, dut) = test.gen_I_load(dut)
        else:
            (instr, dut) = test.gen_S(dut)

        await set_reg_addi(dut, instr.rs1, instr.funct3) #sets the rs1 value
        prior_rd1 = dut_fetch.reg(dut, instr.rs1) 
        prior_memory = dut_fetch.memory(dut, prior_rd1, instr.imm.int)
        #NOTE: rd1's value shouldn't change before or during the clk for memory access purposes. rd1 WILL change if rs1 = rd, but accessing the original rd1 will ensure correct operation.
        tb = testcase(instr, dut, prior_rd1, prior_memory)
        tb.decode(i)
        tb.feed()
        
        prior = tb.monitor("pre") #prior rs1, rs2, rd register values of DUT
        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")        
        
        expected = tb.model(prior) 
        actual = tb.monitor("post") 
        tb.checker(expected, actual)   
        
@cocotb.test()
async def Branch_Jump_instr_test(dut):
    """Test Branch and other jump instructions"""
    cocotb.start_soon(generate_clock(dut))
    await reset_dut(dut)
    await randomize_rf(dut, 11) #arbitrary for now. Need to determine limits of PC
    for i in range(10000):
        test = instruction()
        instr_type = random.choice([0,1,2,3])  #randomize instruction type
        match instr_type:
            case 0: instr = test.gen_B()
            case 1: instr = test.gen_J()
            case 2: instr = test.gen_U()
            case 3: instr = test.gen_I_jump()
        tb = testcase(instr, dut)
            
        tb.decode(i)
        tb.feed()
        
        prior = tb.monitor("pre") #prior rs1, rs2, rd register values of DUT
        await RisingEdge(dut.clk) 
        await Timer(10, units="ns")        
        
        expected = tb.model(prior) 
        actual = tb.monitor("post") 
        tb.checker(expected, actual)   