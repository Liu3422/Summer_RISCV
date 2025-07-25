`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/20/2025 05:10:43 PM
// Design Name: 
// Module Name: RV32I_core
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module RV32I_core(
    input logic clk, n_rst,
    // input logic [31:0] instr,
    output logic [31:0]  writeback //output from execute/writeback reg file
    //PC_Next, 
);

logic [31:0] PC; 
logic [31:0] PC_Next;
logic [31:0] instr; 

always_ff @(posedge clk, negedge n_rst) begin
    if(!n_rst) 
        PC <= 0;
    else
        PC <= PC_Next; 
end

fetch_instr #(.NUM_INSTR(1024)) DUT_instr (.clk(clk), .n_rst(n_rst),
    .PC(PC), //watch for potential timing hazards (PC vs PC_Next)
    .instr(instr)
); 

logic beq_cond, bne_cond, PCSrc, zero;
logic [2:0] funct3;
/* synthesis keep */ logic [31:0] imm_out; //synthesis directive
assign funct3 = instr[14:12];
assign beq_cond = (PCSrc & zero) & (funct3 == 3'b000); //zero is raised when alu_out == 0
assign bne_cond = (PCSrc & !zero) & (funct3 == 3'b001); //zero is raised when alu_out != 0, for bne instr
// assign zero = (ALU_Out == 32'b0); // zero is raised

always_comb begin
    if(beq_cond | bne_cond) 
        PC_Next = PC + ({{20{imm_out[11]}}, imm_out[11:0]} << 1); //sign extension for signed imm_out. 
    else
        PC_Next = PC + 4;
end



logic RegWr, ALUSrc, MemWr, MemRead, MemtoReg; //Control signals
logic [1:0] ALUOp;

control DUT2 (
    // .clk(clk), 
    // .n_rst(n_rst),
    .instr(instr[6:0]),
    .PCSrc(PCSrc),
    .RegWr(RegWr),
    .ALUSrc(ALUSrc),
    .MemWr(MemWr),
    .MemRead(MemRead),
    .MemtoReg(MemtoReg),
    .ALUOp(ALUOp)
);

// logic [31:0] writeback; //output from execute/writeback reg file
logic [31:0] rd1, rd2;
decode_reg_file DUT_RF (.clk(clk), .n_rst(n_rst),
    .RegWr(RegWr),
    .read_reg1(instr[19:15]),
    .read_reg2(instr[24:20]),
    .write_reg(instr[11:7]),
    .write_data(writeback),
    .rd1(rd1), 
    .rd2(rd2)
);

logic [3:0] ALU_Operation; //output from ALU_control
logic [31:0] ALU_Out, ALU_in2; //ALU_in2 is from mux of rd2 or imm_gen
ALU DUT4 (  //combinational?
    .ALU_Operation(ALU_Operation),
    .rd1(rd1),
    .rd2(ALU_in2),
    .out(ALU_Out),
    .zero(zero)
);
assign ALU_in2 = (ALUSrc) ? {{20{imm_out[11]}}, imm_out[11:0]} : rd2; 

ALU_control DUT5 (
    .instr({instr[30], funct3}),
    .ALUOp(ALUOp),
    .ALU_Operation(ALU_Operation)
);

logic [31:0] execute_data; //data memory
memory_reg_file #(.NUM_WORDS(32)) DUT_Data(.clk(clk), .n_rst(n_rst),
    .MemWr(MemWr),
    .MemRead(MemRead),
    .addr(ALU_Out),
    .write_data(rd2),
    .execute_data(execute_data)
);
assign writeback = (MemtoReg) ? execute_data : ALU_Out;
// assign upper_imm = imm_out[31:12]; //getting rid of warning
// logic [11:0] imm_out;
imm_gen DUT7(/*.clk(clk), .n_rst(n_rst), */
    .instr(instr),
    .imm_out(imm_out)
);
endmodule
