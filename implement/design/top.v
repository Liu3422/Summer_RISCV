module top (
        clk,
        n_rst,
        SSEG_CA,
        SSEG_AN
);
        input wire clk;
        input wire n_rst;
        output wire [7:0] SSEG_CA;
        output wire [7:0] SSEG_AN;
        wire [31:0] PC_Next;
        wire [31:0] instr;
        wire [31:0] core_out;
        wire [31:0] writeback;
        RV32I_core DUT_core(
                .clk(clk),
                .n_rst(n_rst),
                .writeback(core_out)
        );
        wire [5:0] buffer_occ;
        Data_Buffer DUT_Buffer(
                .clk(clk),
                .n_rst(n_rst),
                .data_in(core_out),
                .data_out(writeback),
                .buffer_occ(buffer_occ)
        );
        wire write_ready;
        assign write_ready = buffer_occ != 0;
        gpio DUT_GPIO(
                .clk(clk),
                .n_rst(n_rst),
                .SSEG_AN(SSEG_AN),
                .SSEG_CA(SSEG_CA),
                .write_ready(write_ready),
                .writeback(writeback)
        );
        wire core_clk;
        flex_counter Clock_Divider_9to1(
                .clk(clk),
                .n_rst(n_rst),
                .clear(1'b0),
                .count_enable(1'b1),
                .rollover_val(4'd9),
                .rollover_flag(core_clk),
                .count_out()
        );
endmodule