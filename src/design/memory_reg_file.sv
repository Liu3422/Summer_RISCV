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


module memory_reg_file#(
    parameter NUM_WORDS = 1024 //Convert to NUM_BITS?
    ) (
    input logic clk, n_rst, MemWr, MemRead,
    input logic [10:0] addr, //This is assuming NUM_WORDS=1024.  
    input logic [31:0] write_data,
    input logic [2:0] funct3,
    output logic [31:0] data_read
    );
    logic [31:0] data_memory [0:NUM_WORDS];
    logic [31:0] out;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            for(int i = 0; i < NUM_WORDS; i++) begin 
                data_memory[i] = 'b0; // = instead of <= for verilator
            end
        end
        else begin
            if (MemWr) //S-type
                data_memory[addr/4][7:0] <= write_data[7:0]; //sb
                if(funct3 == 3'd1) //sh
                    data_memory[addr/4][15:8] <= write_data[15:8]; //byte -> word address
                else if(funct3 == 3'd2) //sw
                    data_memory[addr/4][31:8] <= write_data[31:8]; 
        end
    end

    always_comb begin //combinational read
        if(MemRead)
            case(funct3)
            3'd0: data_read = {{24{data_memory[addr][7]}}, data_memory[addr][7:0]};
            3'd1: data_read = {{16{data_memory[addr][15]}}, data_memory[addr][15:0]};
            3'd2: data_read = data_memory[addr][31:0];
            3'd4: data_read = {24'b0, data_memory[addr][7:0]};
            3'd5: data_read = {16'b0, data_memory[addr][15:0]};
            default: data_read = 0; //undefined S-type funct3
            endcase
        else //if MemtoReg and !MemRead. 
            data_read = 0;  //undefined region of operation
    end
endmodule
