`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:43:19 PM
// Design Name: 
// Module Name: imm_gen
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


module imm_gen(
    input logic [31:0] instr,
    output logic [31:0] imm_out
    );
    parameter I     = 7'b0010011,
              LOAD  = 7'b0000011,
              S     = 7'b0100011,
              SB    = 7'b1100011,
              UJ    = 7'b1101111,
              JALR  = 7'b1100111,
              U     = 7'b0110111, 
              AUIPC = 7'b0010111;
    logic [6:0] opcode;
    assign opcode = instr[6:0];
    always_comb begin
        case(opcode) //opcode
            I: imm_out        = {{20{instr[31]}}, instr[31:20]}; //sign extension
            LOAD: imm_out     = {{20{instr[31]}}, instr[31:20]}; //identical to I, since it is I-Type
            S: imm_out        = {{20{instr[31]}}, instr[31:25], instr[11:7]};
            SB: imm_out       = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0};
            UJ: imm_out       = {{12{instr[31]}}, instr[19:12], instr[20], instr[30:25], instr[24:21], 1'b0};
            JALR: imm_out     = {{20{instr[31]}}, instr[31:20]}; //jalr is I-type, should be identical
            //JALR: imm_out = {{20{instr[31]}}, instr[20], instr[30:25], instr[11:8], 1'b0}; //Unconditional Jump
            U: imm_out        = {instr[31:12], 12'b0};
            AUIPC: imm_out    = {instr[31:12], 12'b0}; 
            default: imm_out  = 32'b0; //edge case?
        endcase
    end
endmodule
