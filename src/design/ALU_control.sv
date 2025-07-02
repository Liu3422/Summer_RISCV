`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:46:51 PM
// Design Name: 
// Module Name: ALU_control
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


module ALU_control( //strictly combinational?
    input logic [3:0] instr, // {30, 14-12}
    input logic [1:0] ALUOp,
    output logic [3:0] ALU_Operation
    );
    parameter [3:0] ADD  = 4'b0010,
                    SUB  = 4'b0110,
                    AND  = 4'b0000,
                    OR   = 4'b0001,
                    XOR  = 4'b0011,
                    SLL  = 4'b0100,
                    SRL  = 4'b0101,
                    SRA  = 4'b0111,
                    SLT  = 4'b1000,
                    SLTU = 4'b1001;

    always_comb begin
        case(ALUOp)
        2'b00: ALU_Operation = ADD;
        2'b01: ALU_Operation = SUB;
        2'b10: begin //R-types
            case(instr)
            4'b0000: ALU_Operation = ADD;
            4'b1000: ALU_Operation = SUB;
            4'b0111: ALU_Operation = AND;
            4'b0110: ALU_Operation = OR;
            4'b0100: ALU_Operation = XOR;
            4'b0001: ALU_Operation = SLL;
            4'b0101: ALU_Operation = SRL;
            4'b1101: ALU_Operation = SRA;
            4'b0010: ALU_Operation = SLT;
            4'b0011: ALU_Operation = SLTU;
            default: ALU_Operation = ADD; //default ALU mode
            endcase
        end
        2'b11: begin
            //I-type instructions have instr[30] high sometimes (except SRL and SLL)
            case(instr)
            4'b1000: ALU_Operation = ADD;
            4'b1111: ALU_Operation = AND;
            4'b1110: ALU_Operation = OR;
            4'b1100: ALU_Operation = XOR;
            4'b0001: ALU_Operation = SLL;
            4'b0101: ALU_Operation = SRL;
            4'b1101: ALU_Operation = SRA;
            4'b1010: ALU_Operation = SLT;
            4'b1011: ALU_Operation = SLTU;

            4'b0000: ALU_Operation = ADD;
            4'b0111: ALU_Operation = AND;
            4'b0110: ALU_Operation = OR;
            4'b0100: ALU_Operation = XOR;
            // 4'b0001: ALU_Operation = SLL;
            // 4'b0101: ALU_Operation = SRL;
            4'b0101: ALU_Operation = SRA;
            4'b0010: ALU_Operation = SLT;
            4'b0011: ALU_Operation = SLTU;
            default: ALU_Operation = ADD;
            endcase
        end
        endcase
    end
endmodule
