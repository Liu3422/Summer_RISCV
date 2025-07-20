This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb**

    Errors:
    - Indexing error for memory instructions.
        - Find out the parameters of memory access. Define how much memory will be in this RV32I_core. 
        - Have error-checking and bounds for checking whether a memory access is valid.


        RISCV Instruction Set Manual: 
        Note: SLTIU rd, rs1, 1 sets rd to 1 if rs1 equals zero, otherwise sets rd to 0 (assembler pseudoinstruction SEQZ rd, rs).
        Note: XORI rd, rs1, -1 performs a bitwise logical inversion of register rs1 (assembler pseudoinstruction NOT rd, rs).
        SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

    In-Progress:
    - S-type (Memory) instruction coverage. Also the I-type load + lui instructions.  
    
    Current:
    - 0% error with N=10,000 in < 5 seconds (100k < 60 sec)
    - ~3 overflow cases (.03%), 10% illegal shift -> swapped to alternative instruction. 0 illegal shift instructions actually occur.
    - directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
    - basic overflow error + instruction error (negative shift) handling
    - hash maps for converting opcode, funct3, and ALU_Operation to names
    - every testbench component (except scoreboard) featured in the instruction() class
    - Randomize state of DUT: random RF and data_memory and a random_reset_dut which randomizes and resets. 
    
    Future:
    - Scoreboard/log parsing
    - Create more classes: Testcase, (idk yet) 
    - Store instructions into memory for DUT to fetch?
        - Idea: store batches (say 1000), execute them all, flush, repeat.
    - Constrained random coverage with jumping instructions?
        - Extremely unpredictable behavior prone to looping.
        - What exactly would this prove verification-wise?
        Solution: only check the PC. 
        - Would have to keep in mind PC's bounds (negative and overflow?) 
        - Whether feeding instructions directly would still be verifying jumps
    - "Fail-mode" with truly random/incorrect instructions
        - Only start doing after all other instructions are done.

    Code Quality (in progress):
    - dut_fetch can be expanded to include instruction type, signed/unsigned pair, maybe names/special instr.

    Concerns:
    - What exactly makes something OOP? 

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
        -Data memory = 64 words. Instruction memory = 1024 words
    - Concurrency/parallelism with Rust?
