`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:43:19 PM
// Design Name: 
// Module Name: imm_gen
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


module imm_gen( //without swizzle
    // input logic clk, n_rst,
    input logic [31:0] instr,
    output logic [11:0] imm_out
    );
    parameter I = 7'b0010011,
              S = 7'b0100011,
              B = 7'b1100011,
              JAL = 7'b1101111;
              JALR = 7'b1100111; 
              //U is both 0110111 and 0010111
    always_comb begin
        case(instr[6:0]) //opcode
            I: imm_out = {instr[31:20]};
            S: imm_out = {instr[31:25], instr[11:7]};
            B: imm_out = {instr[30:24], instr[11:8], instr[0]};
        endcase
    end
    //note: only the first 12 bits of the Imm_gen needs to be implemented here. 
endmodule
