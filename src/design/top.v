module top (
	clk,
	n_rst,
	write_data
);
	reg _sv2v_0;
	input wire clk;
	input wire n_rst;
	output wire [31:0] write_data;
	reg [31:0] PC;
	reg [31:0] PC_Next;
	wire [31:0] instr;
	always @(posedge clk or negedge n_rst)
		if (!n_rst)
			PC <= 0;
		else
			PC <= PC_Next;
	wire beq_cond;
	wire bne_cond;
	wire zero;
	wire [1:0] PCSrc;
	wire [2:0] funct3;
	wire [31:0] imm_out;
	assign funct3 = instr[14:12];
	assign beq_cond = (PCSrc[0] & zero) & (funct3 == 3'b000);
	assign bne_cond = (PCSrc[0] & !zero) & (funct3 == 3'b001);
	wire [31:0] rd1;
	always @(*) begin
		if (_sv2v_0)
			;
		if (beq_cond | bne_cond)
			PC_Next = PC + ({{20 {imm_out[11]}}, imm_out[11:0]} << 1);
		else if (PCSrc == 2'b10)
			PC_Next = rd1 + ({{20 {imm_out[11]}}, imm_out[11:0]} << 1);
		else
			PC_Next = PC + 4;
	end
	fetch_instr #(.NUM_INSTR(1024)) DUT_instr(
		.clk(clk),
		.n_rst(n_rst),
		.PC(PC),
		.instr(instr)
	);
	wire RegWr;
	wire ALUSrc;
	wire MemWr;
	wire MemRead;
	wire MemtoReg;
	wire UncondJump;
	wire [1:0] ALUOp;
	control DUT2(
		.instr(instr[6:0]),
		.PCSrc(PCSrc),
		.RegWr(RegWr),
		.ALUSrc(ALUSrc),
		.MemWr(MemWr),
		.MemRead(MemRead),
		.MemtoReg(MemtoReg),
		.ALUOp(ALUOp),
		.UncondJump(UncondJump)
	);
	wire [9:0] debug_control;
	assign debug_control = {PCSrc, RegWr, ALUSrc, MemWr, MemRead, MemtoReg, ALUOp, UncondJump};
	wire [31:0] writeback;
	wire [31:0] rd2;
	decode_reg_file DUT_RF(
		.clk(clk),
		.n_rst(n_rst),
		.RegWr(RegWr),
		.read_reg1(instr[19:15]),
		.read_reg2(instr[24:20]),
		.write_reg(instr[11:7]),
		.write_data(writeback),
		.rd1(rd1),
		.rd2(rd2)
	);
	wire [3:0] ALU_Operation;
	wire [31:0] ALU_Out;
	wire [31:0] ALU_in1;
	wire [31:0] ALU_in2;
	assign ALU_in2 = (ALUSrc ? {{20 {imm_out[11]}}, imm_out[11:0]} : rd2);
	assign ALU_in1 = (UncondJump ? rd1 : PC);
	ALU DUT4(
		.ALU_Operation(ALU_Operation),
		.rd1(ALU_in1),
		.rd2(ALU_in2),
		.out(ALU_Out),
		.zero(zero)
	);
	ALU_control DUT5(
		.instr({instr[30], funct3}),
		.ALUOp(ALUOp),
		.ALU_Operation(ALU_Operation)
	);
	wire [31:0] execute_data;
	memory_reg_file #(.NUM_WORDS(32)) DUT_Data(
		.clk(clk),
		.n_rst(n_rst),
		.MemWr(MemWr),
		.MemRead(MemRead),
		.addr(ALU_Out),
		.write_data(rd2),
		.execute_data(execute_data)
	);
	assign writeback = (MemtoReg ? execute_data : ALU_Out);
	assign write_data = writeback;
	imm_gen DUT7(
		.instr(instr),
		.imm_out(imm_out)
	);
	initial _sv2v_0 = 0;
endmodule
