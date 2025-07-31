This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb**

    Errors:
        - For a lot of successful memory tests (6%), the memory doesn't match: data_memory[rd1 + imm] != data_memory[word_addr] (word_addr = addr[11:2])
            - This is super weird... especially since the tests themselves pass.
            - Is it prior vs post clk immediate values? One may take the prior instruction's imm while the other takes the current instr imm.
                - No indication of this with glance at code.

        - <5 cases (per 10k) where model outputs 0 for expected memory when it isn't.

    Info:
        - Difference between instruction immediate and actual immediate for U-Type.
            - Actual imm is the instr field left shifted 12.
        - Decode will show the instr field
        - Actual will show the actual imm

    Current:
    Full constrained random coverage of all instructions (other than ecall and ebreak).
    B-Type + Jump + U-Type
        - All instructions 100% pass rate! (even with 100k tests). 
        - This is the last set of instructions to fully verify!!!

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
    - hash maps for converting opcode, funct3, and ALU_Operation to names
    - instruction() class: creates instructions to feed to dut and testbench
    - testcase(instruction) class: 
        - tests a single instruction
        - every testbench component (is model + checker sufficient for scoreboard?)
        - inherits instruction class properties 
        - takes in DUT, prior memory and rd1 (for memory access/check)
    - dut_fetch() class: 
        - fetches values (reg, imm, memory) from DUT
        - more advanced methods involve operating on these values and printing statements.
    - Randomize state of DUT: random RF and data_memory and a random_reset_dut which randomizes both and resets. 

    Future:
    - Create more classes: Test_environment, dut_write (only a couple dut_fetch instructions change the dut currently) 
    - Store instructions into memory for DUT to fetch?
        - Idea: store batches (say 1000), execute them all, flush, repeat.
    - "Fail-mode" with truly random/incorrect instructions
        - Only start doing after all other instructions are done.
    - Use cocotb's built-in "logging" library instead of manually printing.
        - Moving from hardcoded debug prints to OOP logging. 

    Code Quality (in progress):
    - dut_fetch can be expanded to include instruction type, signed/unsigned pair, maybe names/special instr.

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
**RV32I_core**
   Completed!

    Current: 
    - Basic verification of all instructions.
    - Basic program (fibonnaci) is working and verified. 

    Concerns:
    - NONE!!!
    - Need to define specs more. How many instructions/data can it hold? Would determine PC and data_memory bounds. 
        -Data memory = 1024 words. Instruction memory = 64 words/instructions
        -Thus, limit rs1 value to 1024 unsigned for memory instructions? Limit addr to ALU_Out[11:0]?
            - Or assign data memory to 32-bit address? Kind of overkill, since that's 2^28 bytes. 
    Current iteration:
        -12 bit addr 
        -combinational read, clk'd write
        -Only accepts natural alignment memory.
    - Currently little endian (LSB in lower address first) in cocotb and memory_reg_file
