`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:45:54 PM
// Design Name: 
// Module Name: execute_reg_file
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

// x0 SHOULD BE HARDWIRED TO ZERO
module memory_reg_file#(
    parameter NUM_WORDS = 1024
    ) (
    input logic clk, n_rst, MemWr, MemRead,
    input logic [31:0] addr, write_data,
    output logic [31:0] execute_data
    );
    logic [31:0] data_memory [0:NUM_WORDS];
    logic [31:0] out;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            execute_data <= 32'b0;
            for(int i = 0; i < NUM_WORDS; i++) begin 
                data_memory[i] <= 'b0;
            end
        end
        else begin
            execute_data <= out;
            if (MemWr)
                data_memory[addr] <= write_data;
        end
    end

    always_comb begin 
        if(MemWr) begin
            out = write_data;
        end
        else if(MemRead)
            out = data_memory[addr];
        else //edge case?
            out = 0;
    end
endmodule
