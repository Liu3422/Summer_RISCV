`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/01/2025 12:29:20 PM
// Design Name: 
// Module Name: ALU
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


module ALU(
    input logic [3:0] ALU_Operation,
    input logic [31:0] rd1, rd2,
    output logic [31:0] out
    );
    always_comb begin
        case (ALU_Operation)
            0000: assign out = rd1 & rd2;
            0001: assign out = rd1 | rd2;
            0010: assign out = rd1 + rd2;
            0110: assign out = rd1 - rd2;
            default: assign out = 0; //undefined region of operation
        endcase    
    end
endmodule
