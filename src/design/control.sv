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
    UncondJump, //0: normal. 1: rd1 = PC + 4
    Auipc, //0: normal. 1: rd1 = PC 
    Utype, //0: signed imm. 1: Utype imm
    output logic [1:0] ALUOp,
    PCSrc //0: PC + 4. 1: Branch Target (PC += imm_gen). ??2: PC = rs1 + imm
    );
    parameter BTYPE   = 7'b1100011, //implemented beq, bne
              RTYPE = 7'b0110011,
              STORE = 7'b0100011,
              LOAD  = 7'b0000011,
              ITYPE = 7'b0010011,
              JAL   = 7'b1101111, 
              JALR  = 7'b1100111, 
              LUI   = 7'b0110111,
              AUIPC = 7'b0010111;
    always_comb begin //note: MemRead is not implemented yet.
        {PCSrc, ALUSrc, ALUOp, MemWr, MemtoReg, RegWr, MemRead, UncondJump, Auipc, Utype} = 12'b001000010000;
        case(instr)
        BTYPE: {PCSrc, ALUSrc, ALUOp, RegWr} = 6'b010010; 
        RTYPE: {ALUSrc, ALUOp} = 3'b010;
        STORE: {MemWr, RegWr} = 2'b10; 
        LOAD : {MemtoReg, MemRead, RegWr} = 3'b111;
        ITYPE: {ALUOp} = 2'b11;
        JAL  : {PCSrc, ALUSrc, ALUOp, RegWr, UncondJump} = 7'b011_00_11; 
        JALR : {PCSrc, ALUSrc, ALUOp, RegWr, UncondJump} = 7'b101_00_11;
        LUI  : {ALUOp, Utype} = 3'b001; 
        AUIPC: {Auipc, ALUOp, Utype} = 4'b1001;
        default: {PCSrc, ALUSrc, ALUOp, MemWr, MemtoReg, RegWr, MemRead, UncondJump, Auipc, Utype} = 12'b01000010000;
        endcase
    end
endmodule
