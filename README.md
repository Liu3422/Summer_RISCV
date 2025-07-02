This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Errors:
- monitor is displaying irrelevant (prior) immediate values
- sltiu is displayed as sltui in testbench.
- all slt instructions are incorrect
- model is false positive when rd = rs1/rs2 (for example, sub would expect double subtraction)
- model is sometimes wrong on xor/xori
- model is sometimes wrong on shift instructions 
- model has some errors with signed vs unsigned rep

Current:
- ~2% error with N=10,000
- directly feeding instruction without use of instruction memory/fetch register
- uses prior testbench (add/addi) to randomize registers before operation
- basic overflow error + instruction error (negative shift) handling

Future:
- Scoreboard/log parsing