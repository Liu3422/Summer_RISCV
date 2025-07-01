`timescale 1ns / 1ps
module gpio ( input logic clk, n_rst,
    // input logic [15:0] SW,
    input logic [31:0] writeback,
    // input logic [5:0] BTN,
    // output logic [15:0] LED,
    output logic [7:0] SSEG_AN, SSEG_CA 
);
    logic [7:0] seg_out; 
    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            SSEG_AN <= 8'b0;
            SSEG_CA <= 8'b0;
        end
        else begin
            SSEG_AN <= 8'hFF; //this will need to be changed to iterate through AN.
            SSEG_CA <= seg_out;
        end
    end
    // always_comb begin
    genvar i;
    generate
        for (i = 0; i < 7; i++) begin
            display_controller DUT_display (.in(writeback[4*i : 4*i+3]), .out(seg_out));
        end
    endgenerate
    // end
endmodule
