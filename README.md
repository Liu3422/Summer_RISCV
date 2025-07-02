This is an implementation of the RV32I ISA, as seen in "Computer Organization and Design, RISC-V Edition" by Patterson and Hennessey. 
This repository consists of a single-cycle implementation, bitstreaming to the Nexys A7 dev board via Vivado and verification with cocotb.

Errors:
- immediate instructions aren't being properly decoded: ALU_control. Defaults to ADD (showing case isn't hit)
- model is sometimes subtracting negatives instead of adding 
- monitor is displaying irrelevant (prior) immediate values
- sltiu is displayed as sltui in testbench.
- all slt instructions are incorrect