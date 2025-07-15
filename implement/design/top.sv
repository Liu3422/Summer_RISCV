`timescale 1ns / 1ps
module top (
    input logic clk, n_rst,
    // input logic [15:0] SW,
    // input logic [4:0] BTN,
    // output logic [15:0] LED,
    output logic [7:0] SSEG_CA, SSEG_AN

    // output logic RGB1_Blue, RGB1_Green, RGB1_Red, RGB2_Blue, RGB2_Green, RGB2_Red,
    // input logic CPU_RESET //set as n_rst?
);

logic core_clk;
flex_counter Clock_Divider_9to1 (.clk(clk), .n_rst(n_rst),
    .clear(1'b0),
    .count_enable(1'b1),
    .rollover_val(4'd9),
    /* verilator lint_off PINCONNECTEMPTY */
    .rollover_flag(core_clk), 
    .count_out() 
);

logic [31:0] core_out, writeback;

RV32I_core DUT_core (.clk(core_clk), .n_rst(n_rst), 
    .writeback(core_out) //data written to memory or ALU outputs.
);

logic [4:0] buffer_occ;
Data_Buffer DUT_Buffer ( .clk(clk), .n_rst(n_rst),
    .data_in(core_out),
    .data_out(writeback),
    .buffer_occ(buffer_occ)
);

logic write_ready;
assign write_ready = (buffer_occ != 0);

gpio DUT_GPIO ( .clk(clk), .n_rst(n_rst),
//FPGA/peripheral I/O
    // .SW(SW),
    // .BTN(BTN),
    // .LED(LED),
    .SSEG_AN(SSEG_AN), 
    .SSEG_CA(SSEG_CA),
//core inputs
    .write_ready(write_ready),
    .writeback(writeback)
);

endmodule
