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
    input logic [11:0] addr, //byte-address
    input logic [31:0] write_data,
    input logic [2:0] funct3,
    output logic [31:0] data_read
    );
    logic [31:0] data_memory [0:NUM_WORDS-1]; //word-address
    logic [31:0] out, word_data;
    logic [9:0] word_addr;
    logic [1:0] byte_offset; 
    logic [15:0] half_read; //2-byte to be loaded into memory

    assign byte_offset = addr[1:0];
    assign word_addr = addr[11:2]; //equal to >>2, /4
    assign word_data = data_memory[word_addr]; //debug

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            for(int i = 0; i < NUM_WORDS; i++) begin 
                data_memory[i] = 'b0; // = instead of <= for verilator
            end
        end
        else begin
            if (MemWr) begin
                case(byte_offset)
                2'd0: data_memory[word_addr][7:0] <= write_data[7:0]; //sb
                2'd1: data_memory[word_addr][15:8] <= write_data[7:0]; 
                2'd2: data_memory[word_addr][23:16] <= write_data[7:0]; 
                2'd3: data_memory[word_addr][31:24] <= write_data[7:0]; 
                endcase
                if(funct3 == 3'd1) begin //sh NOTE: byte_offset = 0 or 2 here
                    case(byte_offset)
                    2'd0: data_memory[word_addr][15:8] <= write_data[15:8]; //store into next byte
                    // 2'd1: data_memory[word_addr][15:8] <= write_data[15:8]; //misaligned address
                    2'd2: data_memory[word_addr][15:8] <= write_data[15:8]; 
                    // 2'd3: data_memory[word_addr][15:8] <= write_data[15:8]; //misaligned address
                    default: data_memory[word_addr][15:8] <= 'b0;
                    endcase
                end
                else if(funct3 == 3'd2 & (byte_offset == 2'b0)) begin //sw NOTE: byte_offset = 0 here
                    data_memory[word_addr][15:8] <= write_data[15:8]; //store next 3 bytes
                    data_memory[word_addr][23:16] <= write_data[23:16]; 
                    data_memory[word_addr][31:24] <= write_data[31:24];  
                end        
            end
        end
    end

    always_comb begin //combinational read. 
        if(MemRead) begin 
            case(byte_offset) //choosing which byte in word to read
            2'd0: half_read = data_memory[word_addr][15:0]; //set for both lb and lh 
            2'd1: half_read = {8'b0, data_memory[word_addr][15:8]}; //only want byte for misaligned address.
            2'd2: half_read = data_memory[word_addr][31:16]; //set for both lb and lh 
            2'd3: half_read = {8'b0, data_memory[word_addr][31:24]}; 
            endcase
            case(funct3)
            3'd0: data_read = {{24{half_read[7]}}, half_read[7:0]}; //lb
            3'd1: data_read = {{16{half_read[15]}}, half_read}; //lh
            3'd2: data_read = data_memory[word_addr]; //lw
            3'd4: data_read = {24'b0, half_read[7:0]}; //lbu
            3'd5: data_read = {16'b0, half_read}; //lhu
            default: data_read = 0; //undefined S-type funct3
            endcase
        end
        else begin//if MemtoReg and !MemRead. 
            data_read = 0; //undefined region of operation
            half_read = 0; //avoid latch
        end
    end
endmodule
