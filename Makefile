# Makefile

# defaults
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/src/design/top.sv
VERILOG_SOURCES += $(PWD)/src/design/imm_gen.sv
VERILOG_SOURCES += $(PWD)/src/design/control.sv
VERILOG_SOURCES += $(PWD)/src/design/decode_reg_file.sv
VERILOG_SOURCES += $(PWD)/src/design/memory_reg_file.sv
VERILOG_SOURCES += $(PWD)/src/design/fetch_reg_file.sv
VERILOG_SOURCES += $(PWD)/src/design/ALU_control.sv
VERILOG_SOURCES += $(PWD)/src/design/ALU.sv
# VERILOG_SOURCES += $(PWD)/tb/tb_top.sv

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = top

# MODULE is the basename of the Python test file
MODULE = verification.test_top

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

log:
	$(MAKE) -c verification \
		SIM=$(SIM) MODULE=test_top \
		> verification/results.log 2>&1