# @cocotb.test()
#NOTE: This test requires fetch_reg_file/DUT_instr to be commented out, due to race conditions between inserting 
#the instruction through this testbench and fetching from the instruction. 
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
    for i in range(1000):
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