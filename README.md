This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and constrained random verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb** Completed!

    Errors:
        - For a lot of successful memory tests (6%), the memory doesn't match: data_memory[rd1 + imm] != data_memory[word_addr] (word_addr = addr[11:2])
            - This is super weird... especially since the tests themselves pass.
            - Is it prior vs post clk immediate values? One may take the prior instruction's imm while the other takes the current instr imm.
                - No indication of this with glance at code.

    Current:
    Full constrained random coverage and verification of all instructions (other than ecall and ebreak).
    
    B-Type + Jump + U-Type
        - All instructions 100% pass rate! (even with 100k tests). 
        - This is the last set of instructions to fully verify!!!
        - Difference between instruction immediate and actual immediate for U-Type.
            - Actual imm is the instr field left shifted 12.
        - Decode will show the instr field, actual will show  imm_out

    R-Type (and I-Type counterpart)
        - 0% error with N=10,000 in < 5 seconds (100k < 60sec)
        - ~3 overflow cases (.03%), 10% illegal shift -> swapped to alternative instruction. 0 illegal shift instructions actually occur.
        - directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
        - basic overflow error + instruction error (negative shift) handling

    Memory (I-Type Load and S-Type)
        - ~0% error with N=10,000 in <10 seconds (100k ~ 60sec)
        - Uses an addi instruction to write/set rs1 value prior to test.
        - All instructions follow natural alignment.
            - constrain addressing to rd1 + imm <2048.
        - implement byte-offset, byte addressing per word in memory
        - Currently no misaligns
        - Follow natural alignment rules: 
            lb: any. 
            lh: 0 -> lower, 2 -> upper. 
            lw: 0 -> word (self-explanatory)
            - This also applies to store
        - mask memory to extract the correct value to compare to (say, upper half of memory if sh and byte_offset = 2)
        
    Hash maps, bit-wise functions, and DUT setting:
    - hash maps for converting opcode, funct3, and ALU_Operation to names    
    - Randomize state of DUT: random RF and data_memory and a random_reset_dut which randomizes both and resets. 
    - Logical left/right shift, different instr-type immediate generations, and signed/unsigned conversion.
    - set_reg_addi: sets register values in the DUT to natural memory alignment constraints. 

    Classes:
    - instruction(): creates instructions to feed to dut and testbench
    - testcase(instruction): 
        - tests a single instruction
        - every testbench component (is model + checker sufficient for scoreboard?)
        - takes in DUT, prior memory and rd1 (for memory access/check)
    - dut_fetch(DUT): 
        - fetches values (reg, imm, memory, etc) from DUT
        - more advanced methods involve operating on these values and printing statements.
    - environment(testcase):
        - Basically a wrapper for prior testbenches, and basic_CRT() tests all instructions in one testbench.
        - Is an async def/coroutine object. Thus, it has gen_all (which handles setting for memory instructions) and overflow_checker (which resets upon severe overflow).

    Future:
    - Create more classes/objects: dut_write, bitwise
    - Store instructions into memory for DUT to fetch?
        - Idea: store batches (say 1000), execute them all, flush, repeat.
    - "Fail-mode" with truly random/incorrect instructions
    - Use cocotb's built-in "logging" library instead of manually printing.
        - Moving from hardcoded debug prints to OOP logging. 
    - GTKWave? Verilator can produce this, though actually tracing through that much data is a challenge. 


    RISCV Instruction Set Manual: 
    The JALR instruction now clears the lowest bit of the calculated target address, to simplify hardware and to allow auxiliary information to be stored in function pointers.
    SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

**Nexys A7 100T**

    Goal: output writeback (RV32I_core output) to the seven-segment displays for a customizable time. Do this with Fibonacci, or maybe some other programs.

    Current:
    - No code violations with Verilator nor Vivado (xsim)
    - Skeleton code for Data Buffer
    - ***GPIO***: 
        - at normal clk, RV32I_core at 1/9 clk speed
        - consists only of display controller currently
    - sv2v used to convert top.sv of RV32I_core and implement. RV32I_core packaged as custom IP. 
        - Do I need to copy RV32I_core into design if I plan on importing it as custom IP? I don't think there are difference anyway
    - wavedroms:
        - display_controller

**RV32I_core** Completed!

    Current: 
    - Basic CRT verification of all instructions.
    - Basic program (fibonnaci) is working and verified. 

    Concerns:
    - NONE!!!

    Current iteration:
        - 12 bit addr 
        - Single-cycle: combinational read, clk'd write
        - Only accepts natural alignment memory. Undefined behavior with misaligned memory.
        - Data memory = 1024 words. Instruction memory = 64 words/instructions
        - Currently little endian (LSB in lower address first) in cocotb and memory_reg_file
