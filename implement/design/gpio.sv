`timescale 1ns/1ps

module gpio(
    input logic clk, n_rst,
    //internal input 
    input logic write_ready,
    input logic [31:0] writeback,
    //Nexys A7 I/O
    output logic [7:0] SSEG_AN, SSEG_CA
);

Display_Controller SSEG ( .clk(clk), .n_rst(n_rst),
    .writeback(writeback),
    .write_ready(write_ready),
    .SSEG_AN(SSEG_AN),
    .SSEG_CA(SSEG_CA)
);

endmodule
