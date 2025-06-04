`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 07:00:03 PM
// Design Name: 
// Module Name: Program_counter
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


module program_counter(
    input logic clk,
    input logic n_rst,
    input logic [31:0] PC,
    output logic [31:0] PC_Next
    );

    always_ff@(posedge clk, negedge n_rst) begin //PC Logic
        if(!n_rst) 
            PC <= 0;
        else
            PC <= PC_Next; 
    end

    logic beq_cond, branch, zero;

    assign beq_cond = branch & zero;

    always_comb begin
        if(beq_cond) 
            PC_next = PC + imm_gen;
        else
            PC_next = PC + 4;
    end
endmodule
