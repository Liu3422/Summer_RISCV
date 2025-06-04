`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 05/31/2025 04:17:16 PM
// Design Name: 
// Module Name: top
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


module top(
    input logic clk, n_rst,
    );

logic [31:0] PC;
logic [31:0] PC_Next;

always_ff @(posedge clk, negedge n_rst) begin //does it need to be outside of module, since feeding Next_PC back into program_counter.sv is weird?
    if(!n_rst) 
        PC <= 0;
    else
        PC <= PC_Next; 
end

logic beq_cond, PCSrc, zero;

assign beq_cond = PCSrc & zero;

always_comb begin
    if(beq_cond) 
        PC_next = PC + imm_gen;
    else
        PC_next = PC + 4;
end

logic [31:0] instr; 
fetch_reg_file DUT1 (
    .clk(clk),
    .n_rst(n_rst),
    .PC(PC), //watch for potential timing hazards (PC vs PC_Next)
    .instr(instr)
);

logic PCSrc, RegWr, ALUSrc, MemWr, MemRead, MemtoREg; //Control signals
control DUT2 (
    .clk(clk), 
    .n_rst(n_rst),
    .instr(instr[6:0]),
    .PCSrc(PCSrc),
    .RegWr(RegWr),
    .ALUSrc(ALUSrc),
    .MemWr(MemWr),
    .MemRead(MemRead),
    .MemtoReg(MemtoReg)
);

logic [31:0] writeback; //output from execute/writeback reg file
logic [31:0] rd1, rd2;
decode_reg_file DUT3 (
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

logic [3:0] ALU_Operation; //output from ALU_control
logic [31:0] ALU_Out, ALU_in2; //ALU_in2 is from mux of rd2 or imm_gen
ALU DUT4 (  //combinational?
    .ALUOperation(ALU_Operation),
    .rd1(rd1),
    .rd2(ALU_in2),
    .out(ALU_Out)
);
assign ALU_in2 = (ALUSrc) ? imm_out : rd2; 


ALU_control DUT5 (
    .instr({instr[30], instr[14:12]}),
    .ALUOp(ALUOp),
    .ALU_Operation(ALU_Operation);
)

logic [31:0] execute_data; //data memory
execute_reg_file DUT6(
    .clk(clk),
    .n_rst(n_rst),
    .MemWr(MemWr),
    .MemRead(MemRead),
    .ALU_Out(ALU_Out),
    .write_data(execute_data)
);
assign writeback = (MemtoReg) ? execute_data : ALU_Out;

logic [11:0] imm_out;
imm_gen DUT7(
    .clk(clk),
    .n_rst(n_rst),
    .instr(instr),
    .imm_out(imm_out)
)
endmodule


