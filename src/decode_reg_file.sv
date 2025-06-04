`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:45:34 PM
// Design Name: 
// Module Name: decode_reg_file
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


module decode_reg_file(
    input logic clk, n_rst, RegWr,
    input logic [4:0] read_reg1, read_reg2, write_reg,
    input logic [31:0] write_data,
    output logic [31:0] rd1, rd2
    );
endmodule
