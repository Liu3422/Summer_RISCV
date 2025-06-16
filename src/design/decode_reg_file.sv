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
    logic [31:0] RF [31:0]; //32 registers, each 32 bits long.
    logic [31:0] out;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            for(int i = 0; i < 32; i++) begin //will this all be done in one clk cycle?
                RF[i] <= '0;
            end
        end
        else 
            RF[write_reg] <= out; 
    end
    always_comb begin
        if(RegWr)
            out = write_data;
        else
            out = RF[write_reg]; //do nothing. Do I even need this line?
    end

    assign rd1 = RF[read_reg1];
    assign rd2 = RF[read_reg2];
endmodule
