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
    input logic [31:0] in1, in2,
    output logic [31:0] out,
    output logic zero
    );
    assign zero = (out == 0);
    logic [11:0] imm;
    assign imm = in2[11:0];
    always_comb begin
        case (ALU_Operation)
            AND : out = in1 & in2;
            OR  : out = in1 | in2;
            ADD : out = in1 + in2;
            XOR : out = in1 ^ in2;
            SLL : out = in1 << (in2[4:0]);
            SRL : out = in1 >> (in2[4:0]);
            SUB : out = in1 - in2;
            SRA : out = ($signed(in1)) >>> in2[4:0]; //shift right arithmetic, extends MSB
            SLT : out = ($signed(in1) < $signed(in2)) ? 32'b1 : 32'b0; // signed slt
            SLTU: out = ($unsigned(in1) < $unsigned(in2)) ? 32'b1 : 32'b0; 
            /* verilator lint_off WIDTHEXPAND */
            SLTI: out = ($signed(in1) < $signed(imm)) ? 32'b1 : 32'b0;
            SLTIU: out = ($unsigned(in1) < $unsigned(imm)) ? 32'b1 : 32'b0; 

            default: out = 0; //undefined region of operation
        endcase    
    end
endmodule
