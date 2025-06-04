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
    input logic clk, n_rst, 
    input logic [6:0] instr,
    //change below into bus?
    output logic PCSrc, //0: PC + 4. 1: Branch Target (PC + imm_gen)
    RegWr, //1: register is written 
    ALUSrc, //0: Rd2. 1: imm_gen from instr 
    ALUOp, 
    MemWr, //1:Data at the address input is replaced by write data input. 
    MemRead, 
    MemtoReg // write data input is:  0: ALU. 1:data memory
    );
endmodule
