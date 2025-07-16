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
    output logic [31:0] write_data
    ); 
logic PC_wait; //hardcode PC increments only after the first instr.
logic [31:0] PC;
logic [31:0] PC_Next;
logic [31:0] instr; 
// logic n_rst;
// assign n_rst = n_rst1 | CPU_RESET; //trying C12 button on Nexys A7

always_ff @(posedge clk, negedge n_rst) begin 
    if(!n_rst) begin
        PC <= 0;
        PC_wait <= 0;
    end
    else begin
        if(PC_wait)
            PC <= PC_Next;
        PC_wait <= 1'b1;
    end

end

logic zero, UncondJump, jal_cond, jalr_cond, branch_cond, branch_unsigned;
logic [1:0] PCSrc;
logic [2:0] funct3;
/* synthesis keep */ logic [31:0] imm_out, rd1, beq_value; //synthesis directive
assign funct3 = instr[14:12];
// assign beq_cond = (PCSrc == 2'b1 & zero) & (funct3 == 3'b000); 
// assign bne_cond = (PCSrc == 2'b1 & !zero) & (funct3 == 3'b001);
// assign blt_cond = 
// assign bge_cond = 
// assign bltu_cond = 
// assign bgeu_cond = 
// assign branch_cond = beq_cond | bne_cond | blt_cond | bge_cond | bltu_cond | bgeu_cond;

always_comb begin
    branch_unsigned = 0;
    branch_cond = 0;
    if(PCSrc == 2'b1) begin
        case(funct3)
        3'd0: branch_cond = zero; //beq
        3'd1: branch_cond = !zero; //bne
        3'd4: branch_cond = ($signed(ALU_Out) < 0); //blt
        3'd5: branch_cond = ($signed(ALU_Out) >= 0); //bge
        3'd6: begin //bltu
            branch_cond = (ALU_Out >= 0);
            branch_unsigned = 1'b1;
        end
        3'd7: begin //bgeu
            branch_cond = (ALU_Out < 0);
            branch_unsigned = 1'b1;
        end
        default: branch_cond = 0; //undefined region of operation, no branch.
        endcase
    end
end
assign jal_cond = (UncondJump & PCSrc == 2'b01);
assign jalr_cond = (UncondJump & PCSrc == 2'b10);

assign beq_value = branch_unsigned ? {20'b0, imm_out[11:0]}: {{20{imm_out[11]}}, imm_out[11:0]}; // << 1; //debug purposes
always_comb begin
    if (jal_cond) 
        PC_Next = PC + imm_out;
    else if(branch_cond) 
        PC_Next = PC + beq_value; //sign extension for signed imm_out
    else if (jalr_cond) 
        PC_Next = rd1 + imm_out; 
    else
        PC_Next = PC + 4;
end
// logic enable;
`ifdef COCOTB_SIM
    logic [31:0] instr_cocotb;
    assign instr = instr_cocotb;
`else
    fetch_instr #(.NUM_INSTR(1024)) DUT_instr (.clk(clk), .n_rst(n_rst),
        .PC(PC), //watch for potential timing hazards (PC vs PC_Next)
        .instr(instr)
    ); 
`endif 

logic RegWr, ALUSrc, MemWr, MemRead, MemtoReg, Auipc, Unsigned; //Control signals
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
    .ALUOp(ALUOp),
    .UncondJump(UncondJump),
    .Auipc(Auipc),
    .Unsigned(Unsigned)
);
logic [9:0] debug_control;
assign debug_control = {PCSrc, RegWr, ALUSrc, MemWr, MemRead, MemtoReg, ALUOp, UncondJump};

logic [31:0] writeback; //output from execute/writeback reg file
logic [31:0] rd2;
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
logic [31:0] ALU_Out, ALU_in1, ALU_in2; //ALU_in1: rd1 or PC. ALU_in2: rd2 or imm_gen

assign ALU_in2 = (ALUSrc) ? (Unsigned ? (imm_out): {{20{imm_out[11]}}, imm_out[11:0]} ): rd2; 
assign ALU_in1 = (UncondJump) ? (PC + 4) : (Auipc) ? PC : rd1; 

ALU DUT4 (  //combinational?
    .ALU_Operation(ALU_Operation),
    .in1(ALU_in1),
    .in2(ALU_in2),
    .out(ALU_Out),
    .zero(zero)
);

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
assign write_data = writeback; //output of the RV32I_core

imm_gen DUT7(/*.clk(clk), .n_rst(n_rst), */
    .instr(instr),
    .imm_out(imm_out)
);

// assign LED = ALU_Out[15:0];
endmodule


