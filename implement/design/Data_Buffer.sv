`timescale 1ns/1ps

module Data_Buffer #(
    parameter SIZE = 32
) ( input logic clk, n_rst,
    input logic [31:0] data_in,
    output logic [31:0] data_out,
    output logic [4:0] buffer_occ
);

endmodule
