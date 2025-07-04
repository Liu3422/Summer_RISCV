This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Requirements:
- Vivado
- Cocotb venv with WSL

Errors:
- model is sometimes wrong on shift instructions 
    - sign is not preserved on right shift
- DUT is incorrect on sltu when 
    - rd1 > 2^31
    RISCV Instruction Set Manual: 
    Note: SLTIU rd, rs1, 1 sets rd to 1 if rs1 equals zero, otherwise sets rd to 0 (assembler pseudoinstruction SEQZ rd, rs).
    Note: XORI rd, rs1, -1 performs a bitwise logical inversion of register rs1 (assembler pseudoinstruction NOT rd, rs).
    SLL, SRL, and SRA perform logical left, logical right, and arithmetic right shifts on the value in register rs1 by the shift amount held in the lower FIVE bits of register rs2.

Current:
- <1% error with N=10,000 in <5 seconds
- directly feeding instruction without use of instruction memory/fetch register. No longer need to uncomment fetch_reg_file for cocotb tests.
- basic overflow error + instruction error (negative shift) handling
- hash maps for converting opcode, funct3, and ALU_Operation to names
- every testbench component (except scoreboard) featured in the instruction() class
- attempting fibonacci test on SV testbench

Future:
- Scoreboard/log parsing
- "Fail-mode" with truly random/incorrect instructions
- Randomize state of DUT: random RF?
- Store instructions into memory for DUT to fetch.
    - Idea: store batches (say 1000), execute them all, flush, repeat.
- S-type (Memory) instruction coverage. Also the I-type load + lui instructions.  
- Constrained random coverage with branch instructions?
    - Extremely unpredictable behavior prone to looping.
    - What exactly would this prove verification-wise?