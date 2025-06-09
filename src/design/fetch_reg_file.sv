`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:45:18 PM
// Design Name: 
// Module Name: fetch_reg_file
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


module fetch_reg_file(
    input logic clk, n_rst,
    input logic [31:0] PC,
    output logic [31:0] instr
    );
    logic [31:0] instruction_data [31:0] ;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            instr <= 0;
        end
        else begin
            instr <= instruction_data[PC];
        end
    end                
endmodule
