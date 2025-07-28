This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

**Cocotb**

    Errors:
        -M value is changing during some load instructions
            -It usually changes to 0, and the rd also sometimes ends up as 0
        -For the model, some instructions incorrectly mask
            - Still need to figure out the specifics of using the past rd1, it is messing up some normal tests!
            - Byte isn't properly masking, sometimes more than 8 bits.
            - half can differ between lower and upper half of word. If model is different from DUT, it prints incorrect.
        - 1/8 of failed tests have mismatching memory
        - writedata (rd2) is always 0, even for successful tests. Is this a race condition, or trace of a bug?
        - lh not checking for sign extension
            -Non-U type load/store are signed, treat them that way.
        - sb fails have 0 in memory. They also tend to not actually change memory at all
            - This is due to improper masking of the word in memory... sb passes when byte_offset is 0 (default mask)
            - Initial fix has been written in, more work may be needed
        - For a few correct lw tests, the memory doesn't match: data_memory[rd1 + imm] != data_memory[word_addr] (word_addr = addr[11:2])
            - This is super weird...
            Test 126
            Instruction type: I-Type Load
            Name: lw
            Registers: rd=21, rs1=2, Imm=8
            Instruction: 00000000100000010010101010000011
            Pre-instruction: rd=710, M[104(rd1)+0x008(imm)]=-894368293
            Word-Address:28, Byte-Address:112
            Actual: rd=-894368293, M[104(rd1)+8(imm)]=-894368293
            Expected rd: -894368293
            Memory doesn't match, probably address mismatch: memory=-0b110101010011101111101000100101, word_data=11001010101100010000010111011011
            addr=112,word_addr=28, byte_offset=0
            Instruction Failed
            1 incorrect test(s)

    Edgecases: 
        - rd = rs1 results in the rd1 value (used to increment in data_memory) changing. 
            - rs1's value is extracted at the start of the test, right after the addi instr.
            - fails also results in mismatching memory

        RISCV Instruction Set Manual: 
        The JALR instruction now clears the lowest bit of the calculated target address, to simplify hardware
and to allow auxiliary information to be stored in function pointers.
        SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

    In-Progress:
    - S-type (Memory) instruction coverage. Also the I-type load + lui instructions. 80% Pass rate
    Current: Using addi instead of directly writing to DUT.
    - constrain addressing to rd1 + imm <1024.
    - implement byte-offset, byte addressing per word in memory. Only support naturally aligned address.
        - This constraint must be added into cocotb. If misaligned, will inform of the test and only store first byte.
        - Currently no misaligns
        - Follow natural alignment rules: 
            lb: any. 
            lh: 0 -> lower, 2 -> upper. 
            lw: 0 -> word (self-explanatory)
            - This allow applies to store
    - mask memory to extract the correct value to compare to (say, upper half of memory if sh and byte_offset = 2)
        - Do I want this in monitor or model?
        - monitor will mean not seeing the whole word in memory. Do I need to?

    - convert more of the program into OOP classes/objects, its getting pretty long. 
    
    Current:
    - 0% error with N=10,000 in < 5 seconds (100k < 60 sec)
    - ~3 overflow cases (.03%), 10% illegal shift -> swapped to alternative instruction. 0 illegal shift instructions actually occur.
    - directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
    - basic overflow error + instruction error (negative shift) handling
    - hash maps for converting opcode, funct3, and ALU_Operation to names
    - every testbench component (is model + checker sufficient for scoreboard?) featured in the instruction() class
    - Randomize state of DUT: random RF and data_memory and a random_reset_dut which randomizes and resets. 
    
    Future:
    - Create more classes: Test_environment, dut_write (only a couple dut_fetch instructions change the dut currently) 
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
    - Split "instruction" class with "test" class (decode, monitor, model, etc.)
        - test class will be a child and inherit the instruction class. OOP opportunity!

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
        -Thus, limit rs1 value to 1024 unsigned for memory instructions? Limit addr to ALU_Out[11:0]?
            - Or assign data memory to 32-bit address? Kind of overkill, since that's 2^28 bytes. 
    Current iteration:
        -12 bit addr 
        -combinational read, clk'd write
        -Only accepts natural alignment memory.
    - Currently little endian (LSB in lower address first) in cocotb and memory_reg_file
