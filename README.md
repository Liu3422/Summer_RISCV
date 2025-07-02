This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Errors:
- model is sometimes wrong on shift instructions 
    - expects a -1 instead of 0 when shifting a lot (more than 10 bits)
- model is not decrementing imm by 1024 on srai
- DUT is incorrect on sltu when 
    - rd1 is less than -1
    - rd2 > 2^31 (note no overflow)
    - NOTE: both have the MSB high.

Current:
- ~3% error with N=10,000 in <5 seconds
- directly feeding instruction without use of instruction memory/fetch register
- basic overflow error + instruction error (negative shift) handling
- hash maps for converting opcode, funct3, and ALU_Operation to names
- every testbench component (except scoreboard) featured in the instruction() class

Future:
- Scoreboard/log parsing
- "Fail-mode" with truly random/incorrect instructions
- Randomize state of DUT: random RF?