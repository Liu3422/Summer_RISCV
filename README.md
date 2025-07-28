This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb**

    Errors:
    !! rd1 value is only being rewritten after the clk cycle!
        -Current! use li/addi instead of directly writing to DUT.

    - Indexing error for memory instructions.
        - Have error-checking and bounds for checking whether a memory access is valid.
        - Unexpected values for addresses > 1024:
            M[660764(rs1)+0x008(imm)]=107935
            - Solution: constrain addressing to rd1 + imm <1024.
            - rd1 is not changing sometimes
        - lb incorrectly sign-extends
        
    - memory_reg_file has data_memory indexed by a word address, which involves addr>>2 to index.
        - What if I want to store a byte to, say, byte address 3?
        - Word address conversion would result in bytes always being stored at the first byte of each word. 
        Solution: implement byte-offset, byte addressing per word in memory. Only support naturally aligned address.
        - Do I want to support misaligned address? Say, store word at addr 3?
            - NO! This implementation will always assume naturally aligned addressing. It will also always store the first/lowest byte of the address.
            - This constraint must be added into cocotb. If misaligned, round down to natural alignment.
            - Currently constraining imm. If +rd1 leads to misalign, how to change? How to detect?
            - rd1 isn't changing for whatever reason. 
    - model is incorrect, sometimes doesn't include the full expected half-word.
    - FIXED: Address of cocotb and dut aren't matching.
        - When generating instruction + rewriting registers, cocotb doesn't get the rewritten values.
        
    - for lh/other load instructions, do I load upper or lower
        - Follow natural alignment rules: 
        lb: any. 
        lh: 0 -> lower, 2 -> upper. 
        lw: 0 -> word (self-explanatory)
        - This allow applies to store
    - memory != word_data, even though they should. 

        RISCV Instruction Set Manual: 
        The JALR instruction now clears the lowest bit of the calculated target address, to simplify hardware
and to allow auxiliary information to be stored in function pointers.
        SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

    In-Progress:
    - S-type (Memory) instruction coverage. Also the I-type load + lui instructions.  

    
    Current:
    - 0% error with N=10,000 in < 5 seconds (100k < 60 sec)
    - ~3 overflow cases (.03%), 10% illegal shift -> swapped to alternative instruction. 0 illegal shift instructions actually occur.
    - directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
    - basic overflow error + instruction error (negative shift) handling
    - hash maps for converting opcode, funct3, and ALU_Operation to names
    - every testbench component (is model + checker sufficient for scoreboard?) featured in the instruction() class
    - Randomize state of DUT: random RF and data_memory and a random_reset_dut which randomizes and resets. 
    - Claude coded the entirety of the log parser (parser.py). Do I want to code my own in the future?
        - Honestly not even that useful, just a cool little log-checker. 
    
    Future:
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
    - Use cocotb's built-in "logging" library instead of manually printing.
        - Moving from hardcoded debug prints to OOP logging. 

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
        -Data memory = 1024 words. Instruction memory = 64 words/instructions
        -Thus, limit rs1 value to 1024 unsigned for memory instructions? Limit addr to ALU_Out[10:0]?
            - Or assign data memory to 32-bit address? Kind of overkill, since that's 2^28 bytes. 
        - variable amount of data to store/assign in memory. 
        - Combinational read from memory? 
    Current iteration:
        -11 bit addr 
        -combinational read, clk'd write
        -always write first byte, then write half word or full word based on funct3.
    - Little or big endian?
