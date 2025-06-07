`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/03/2025 09:28:37 PM
// Design Name: 
// Module Name: Control
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


module control(
    // input logic clk, n_rst, 
    input logic [6:0] instr,
    //change below into bus?
    output logic PCSrc, //0: PC + 4. 1: Branch Target (PC + imm_gen)
    RegWr, //1: register is written 
    ALUSrc, //0: Rd2. 1: imm_gen from instr 
    MemWr, //1:Data at the address input is replaced by write data input. 
    MemRead, 
    MemtoReg, // write data input is:  0: ALU. 1:data memory
    output logic [1:0] ALUOp
    );
    parameter BEQ   = 7'b1100011, 
              RTYPE = 7'b0110011,
              STORE = 7'b0100011,
              LOAD  = 7'b0000011,
              ITYPE = 7'b0010011;
    always_comb begin //note: MemRead is not implemented yet.
        case(instr)
        BEQ: {PCSrc, ALUSrc, ALUOp, RegWr} = 5'b10100; //how to raise "Zero" for BEQ? Review how ALU behaves during B-type
        RTYPE: {ALUSrc, ALUOp} = 3'b010;
        STORE: {MemWr, RegWr, ALUSrc} = 3'b101; 
        LOAD: {MemtoReg, ALUSrc} = 3'b110;
        default: {PCSrc, ALUSrc, ALUOp, MemWr, MemtoReg, RegWr} = 8'b0100001;
        endcase
    end
    assign MemRead = 0;
endmodule
