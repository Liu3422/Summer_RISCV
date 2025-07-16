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


module fetch_instr#(
    parameter NUM_INSTR=1024
    ) (
    input logic clk, n_rst, 
    input logic [31:0] PC,
    output logic [31:0] instr
    );
    logic [31:0] instruction_memory [0:NUM_INSTR]; 


    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            instr <= 0;
            for(int i = 0; i < NUM_INSTR; i++) begin //will this all be done in one clk cycle?
                instruction_memory[i] = '0;
            end
        end
        else 
            instr <= instruction_memory[PC / 4]; //convert from byte to word address
    end                
endmodule
