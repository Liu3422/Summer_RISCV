`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:28:37 PM
// Design Name: 
// Module Name: Control
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


module control(
    // input logic clk, n_rst, 
    input logic [6:0] instr,
    //change below into bus?
    output logic RegWr, //1: register is written 
    ALUSrc, //0: Rd2. 1: imm_gen from instr 
    MemWr, //1:Data at the address input is replaced by write data input. 
    MemRead, 
    MemtoReg, // writeback:  0: ALU. 1:data memory
    UncondJump, //0: normal. 1: rd1 = PC 
    output logic [1:0] ALUOp,
    PCSrc //0: PC + 4. 1: Branch Target (PC += imm_gen). ??2: PC = rs1 + imm
    );
    parameter BTYPE   = 7'b1100011, //implemented beq, bne
              RTYPE = 7'b0110011,
              STORE = 7'b0100011,
              LOAD  = 7'b0000011,
              ITYPE = 7'b0010011,
              JAL   = 7'b1101111, //work in progress. How to move PC to rd? Or PC as one of the operands as an add instr??
              JALR  = 7'b1100111; //work in progress. funct3 = 0, use that?
    always_comb begin //note: MemRead is not implemented yet.
        {PCSrc, ALUSrc, ALUOp, MemWr, MemtoReg, RegWr, MemRead, UncondJump} = 10'b0010000100; //default/common case
        case(instr)
        BTYPE: {PCSrc, ALUSrc, ALUOp, RegWr} = 6'b010010; 
        RTYPE: {ALUSrc, ALUOp} = 3'b010;
        STORE: {MemWr, RegWr, ALUSrc} = 3'b101; 
        LOAD : {MemtoReg, ALUSrc, MemRead} = 3'b110;
        ITYPE: {ALUSrc, ALUOp} = 3'b111;
        JAL  : {PCSrc, ALUSrc, ALUOp, RegWr, UncondJump} = 7'b0100111; //try sub, bc b-type is also sub
        JALR : {PCSrc, ALUSrc, ALUOp, RegWr, UncondJump} = 7'b1010111;

        default: {PCSrc, ALUSrc, ALUOp, MemWr, MemtoReg, RegWr, MemRead, UncondJump} = 10'b010000100; //default/common case
        endcase
    end
endmodule
