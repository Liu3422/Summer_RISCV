module tb_top ();
    localparam CLK_PERIOD = 10ns;

    logic clk, n_rst;

    top DUT (.clk(clk), .n_rst(n_rst));

    always begin
        clk = 0;
        #(CLK_PERIOD / 2.0);
        clk = 1;
        #(CLK_PERIOD / 2.0);
    end

    task reset_dut;
    begin
        n_rst = 0;
        @(posedge clk);
        @(posedge clk);
        @(negedge clk);
        n_rst = 1;
        @(negedge clk);
        @(negedge clk);

        @(posedge clk); //start testing again. Put/command occurs at posedge clk.
    end
    endtask

    initial begin
        n_rst = 1;
        // test = new[7];

        reset_dut;

        DUT.PC = 0;
        $display("Loading rom");
        $readmemh("instr_mem.mem", DUT.DUT_instr.instruction_memory);

        for(int i = 0; i < 9; i++) begin
            @(posedge clk);
        end
        $finish;
    end
endmodule