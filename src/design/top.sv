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
    input logic clk, n_rst
    ); 

logic [31:0] PC;
logic [31:0] PC_Next;

always_ff @(posedge clk, negedge n_rst) begin //does it need to be outside of module, since feeding Next_PC back into program_counter.sv is weird?
    if(!n_rst) 
        PC <= 0;
    else
        PC <= PC_Next; 
end

logic beq_cond, bne_cond, PCSrc, zero;
logic [31:0] imm_out;
assign beq_cond = (PCSrc & zero) & (funct3 == 3'b000); //zero is raised when alu_out == 0
assign bne_cond = (PCSrc & !zero) & (funct3 == 3'b001); //zero is raised when alu_out != 0, for bne instr
// assign zero = (ALU_Out == 32'b0); // zero is raised

always_comb begin
    if(beq_cond | bne_cond) 
        PC_Next = PC + imm_out;
    else
        PC_Next = PC + 4;
end

logic [31:0] instr; 
fetch_reg_file #(.NUM_INSTR(32)) DUT_instr (.clk(clk), .n_rst(n_rst),
    .PC(PC), //watch for potential timing hazards (PC vs PC_Next)
    .instr(instr)
);

logic RegWr, ALUSrc, MemWr, MemRead, MemtoReg; //Control signals
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

logic [31:0] writeback; //output from execute/writeback reg file
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
assign ALU_in2 = (ALUSrc) ? imm_out : rd2; 

logic [1:0] ALUOp;
logic [2:0] funct3;
assign funct3 = instr[14:12];
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

// logic [11:0] imm_out;
imm_gen DUT7(/*.clk(clk), .n_rst(n_rst), */
    .instr(instr),
    .imm_out(imm_out)
);
endmodule


