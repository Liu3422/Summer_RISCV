This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb**

    Errors:
    - NONE!!!

        RISCV Instruction Set Manual: 
        Note: SLTIU rd, rs1, 1 sets rd to 1 if rs1 equals zero, otherwise sets rd to 0 (assembler pseudoinstruction SEQZ rd, rs).
        Note: XORI rd, rs1, -1 performs a bitwise logical inversion of register rs1 (assembler pseudoinstruction NOT rd, rs).
        SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

    Current:
    - 0% error with N=10,000 in < 5 seconds (100k < 60 sec)
    - 1% overflow rate, 10% illegal shift -> swapped to alternative instruction. 0 illegal shift instructions actually occur.
    - directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
    - basic overflow error + instruction error (negative shift) handling
    - hash maps for converting opcode, funct3, and ALU_Operation to names
    - every testbench component (except scoreboard) featured in the instruction() class
    - attempting fibonacci test on SV testbench

    Future:
    - Scoreboard/log parsing
    - "Fail-mode" with truly random/incorrect instructions
    - Randomize state of DUT: random RF?
    - Create more classes: Testcase, (idk yet) 
    - Store instructions into memory for DUT to fetch.
        - Idea: store batches (say 1000), execute them all, flush, repeat.
    - S-type (Memory) instruction coverage. Also the I-type load + lui instructions.  
    - Constrained random coverage with branch instructions?
        - Extremely unpredictable behavior prone to looping.
        
        - What exactly would this prove verification-wise?

    Code Quality (in progress):
    - Rfunct3: change to linked list so you don't have to specify [0] normally
    - dut_fetch can be expanded to include instruction type, signed/unsigned pair, maybe names/special instr.

    Concerns:
    - What exactly makes something OOP? 

**Nexys A7 100T**

    Goal: output writeback (RV32I_core output) to the seven-segment displays for a customizable time. 

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
    Mostly done, a couple more instructions to go. 

    In progress: 
    - More complex SV testcases, like fibonacci 


    Concerns:
    - When processing a jump/branch instruction, the PC still increments and the subsequent instruction is fed into the DUT. Would this be a problem?
    - PC increments before the testbench "officially" runs the instructions.
    - PC increments when fetching the first instruction (during PC = 0), leading to the second instruction being fetched no matter what.
        - It goes PC = 0 instr = 0 *CLK* PC=4, instr=(1st instr) *CLK* PC=X, instr(2nd instr)
        - Thus, PC=4 (2nd instr) is always going to be hit, which would lead to the instruction there always being hit. 
        Solution ideas:
        - make fetch happen on the same clk cycle as decode, rather than the clk cycle before. 
            - Make fetch_instr a combinational block.
            - Better: combinational read of instr. NOTE: reading from registers is already combinational.
        - Iterated solution: PC_wait. Hardcoded waiting to increment PC during first instruction.
            - Problem: First instruction is now iterated twice. 
            - Solution: Combine with combinational read of DUT_instr