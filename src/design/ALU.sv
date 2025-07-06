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
    parameter [3:0] ADD  = 4'b0010,
                    SUB  = 4'b0110,
                    AND  = 4'b0000,
                    OR   = 4'b0001,
                    XOR  = 4'b0011,
                    SLL  = 4'b0100,
                    SRL  = 4'b0101,
                    SRA  = 4'b0111,
                    SLT  = 4'b1000,
                    SLTU = 4'b1001,
                    SLTI = 4'b1100,
                    SLTIU = 4'b1101;

module ALU(
    input logic [3:0] ALU_Operation,
    input logic [31:0] rd1, rd2,
    output logic [31:0] out,
    output logic zero
    );
    assign zero = (out == 0);
    logic [11:0] imm;
    assign imm = rd2[11:0];
    always_comb begin
        case (ALU_Operation)
            AND : out = rd1 & rd2;
            OR  : out = rd1 | rd2;
            ADD : out = rd1 + rd2;
            XOR : out = rd1 ^ rd2;
            SLL : out = rd1 << (rd2[4:0]);
            SRL : out = rd1 >> (rd2[4:0]);
            SUB : out = rd1 - rd2;
            SRA : out = ($signed(rd1)) >>> rd2[4:0]; //shift right arithmetic, extends MSB
            SLT : out = ($signed(rd1) < $signed(rd2)) ? 32'b1 : 32'b0; // signed slt
            SLTU: out = ($unsigned(rd1) < $unsigned(rd2)) ? 32'b1 : 32'b0; 
            /* verilator lint_off WIDTHEXPAND */
            SLTI: out = ($signed(rd1) < $signed(imm)) ? 32'b1 : 32'b0;
            SLTIU: out = ($unsigned(rd1) < $unsigned(imm)) ? 32'b1 : 32'b0; 

            default: out = 0; //undefined region of operation
        endcase    
    end
endmodule
