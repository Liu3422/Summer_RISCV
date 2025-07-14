`timescale 1ns/1ps

module Display_Controller (
    input logic clk, n_rst,
    input logic [31:0] writeback,
    input logic write_ready,
    output logic [7:0] SSEG_AN, SSEG_CA
);

logic rollover_flag, shift_strobe;
flex_counter Display_Count ( .clk(clk), .n_rst(n_rst),
    .clear(0),
    .count_enable(shift_strobe),
    .rollover_val(4'd10), //How to change with buttons and/or switches?
    .rollover_flag(rollover_flag),
    /* verilator lint_off PINCONNECTEMPTY */
    .count_out() 
);

logic [3:0] display_char;

display Display_Logic ( .clk(clk), .n_rst(n_rst),
    .write_ready(write_ready),
    .rollover_flag(rollover_flag),
    .writeback(writeback),
    .shift_strobe(shift_strobe),
    .display_char(display_char),
    .ssd_en(SSEG_AN)
);

display_decoder decode (
    .in(display_char),
    .out(SSEG_CA)
);
endmodule
