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
        // @(negedge clk);
        // @(negedge clk);

        // @(posedge clk); //start testing again. Put/command occurs at posedge clk.
    end
    endtask

    initial begin
        n_rst = 1;

        //test 1, featuring addi, add, sub
        $display("Test 1, Arith");
        reset_dut;
        $readmemh("test1_arith.mem", DUT.DUT_instr.instruction_memory);

        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
        end
        $display("Test 1 complete");
        
        //test 2, featuring addi, sw, lw
        $display("Test 2, Memory");
        reset_dut;
        $readmemh("test2_memory.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
        end
        $display("Test 2 complete");
        
        //test 3, featuring addi, bne
        $display("Test 3, Branch");
        reset_dut;
        $readmemh("test3_branch.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 20; i++) begin
            @(posedge clk);
        end
        $display("Test 3 complete");

        $finish;
    end
endmodule