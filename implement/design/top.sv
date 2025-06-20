`timescale 1ns / 1ps
module top (
    input logic clk, n_rst,
    input logic [15:0] SW,
    input logic [4:0] BTN,
    output logic [15:0] LED
    output logic [7:0] SSEG_CA, SSEG_AN

    // output logic RGB1_Blue, RGB1_Green, RGB1_Red, RGB2_Blue, RGB2_Green, RGB2_Red,
    // input logic CPU_RESET //set as n_rst?
);



logic [31:0] PC_Next, instr;

RV32I_core DUT_core (.clk(clk), .n_rst(n_rst), 
    .instr(instr), 
    .PC_Next(PC_Next),
    .writeback(writeback) //data written to memory or ALU outputs.
);

fetch_reg_file #(.NUM_INSTR(32)) DUT_instr (.clk(clk), .n_rst(n_rst), //external instruction memory
    .PC(PC_Next), //watch for potential timing hazards (PC vs PC_Next)
    .instr(instr)
);

gpio DUT_GPIO (.clk(clk), .n_rst(n_rst),
    //FPGA/peripheral I/O
    .SW(SW),
    .BTN(BTN),
    .LED(LED),
    .SSEG_AN(SSEG_AN),
    .SSEG_CA(SSEG_CA),
    //core inputs
    .writeback(writeback)
);
endmodule
