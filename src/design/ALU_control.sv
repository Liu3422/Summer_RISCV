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
    parameter [3:0] ADD = 4'b0010,
                    SUB = 4'b0110,
                    AND = 4'b0000,
                    OR = 4'b0001;

    always_comb begin
        case(ALU_Op)
        00: assign ALU_Operation = ADD;
        01: assign ALU_Operation = SUB;
        10: begin
            case(instr)
            0000: assign ALU_Operation = ADD;
            1000: assign ALU_Operation = SUB;
            0111: assign ALU_Operation = AND;
            0110: assign ALU_Operation = OR;
            endcase
        end
        endcase
    end
endmodule
