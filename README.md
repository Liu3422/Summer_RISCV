This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Errors:
- model is false positive when rd = rs1/rs2 (for example, sub would expect double subtraction)
- model is sometimes wrong on shift instructions 
    - expects a -1 instead of 0 when shifting a lot (more than 10 bits)
- model has some errors with signed vs unsigned rep
- model is not decrementing imm by 1024 on srai
- negative shift error (fix implement -> ~.3% occurance only on sll)
- DUT is incorrect on sltu when 
    - rd1 is less than -1
    - rd2 > 2^31 (note no overflow)

Current:
- ~3% error with N=10,000
- directly feeding instruction without use of instruction memory/fetch register
- basic overflow error + instruction error (negative shift) handling

Future:
- Scoreboard/log parsing
- "Fail-mode" with truly random/incorrect instructions
- Randomize state of DUT: random RF?