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


module imm_gen( //without swizzle. INCOMPLETE!!!
    // input logic clk, n_rst,
    input logic [31:0] instr,
    output logic [11:0] imm_out
    );
    parameter I  = 7'b0010011,
              S  = 7'b0100011,
              SB = 7'b1100011,
              UJ = 7'b1101111,
              JALR = 7'b1100111,
              U  = 7'b0110111; //no auipc
    always_comb begin
        case(instr[6:0]) //opcode
            I: imm_out = {instr[31:20]};
            JALR: imm_out = {instr[31:20]}; //in I format?
            S: imm_out = {instr[31:25], instr[11:7]};
            SB: imm_out = {instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};
            UJ: imm_out ={instr[31], instr[19:12], instr[20], instr[30:21], 1'b0};
            U: imm_out = 0;
            default: imm_out = 0; //edge case?
        endcase
    end
    //note: only the first 12 bits of the Imm_gen needs to be implemented here. 
endmodule
