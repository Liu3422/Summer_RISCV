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
        end //NOTE: if you adjust the same register and check for the first change AFTER you run the full program, it would (incorrectly) print an error.
        if(DUT.DUT_RF.RF[1][31:0] != 32'd10)
            $display("addi x1, x0, 10 incorrect");
        if(DUT.DUT_RF.RF[2][31:0] != 32'd5)
            $display("addi x2, x0, 5 incorrect");
        if(DUT.DUT_RF.RF[3][31:0] != 32'd15)
            $display("add x2, x1, x2 incorrect");
        if(DUT.DUT_RF.RF[4][31:0] != 32'd5)
            $display("sub x4, x1, x2 incorrect");            
        $display("Test 1 complete");
        
        //test 2, featuring addi, sw, lw
        $display("Test 2, Memory");
        reset_dut;
        $readmemh("test2_memory.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
        end
        if(DUT.DUT_RF.RF[1][31:0] != 32'd100)
            $display("addi x1, x0, 100 incorrect");
        if(DUT.DUT_Data.data_memory[0] != 32'd100)
            $display("sw x1, 0(x0) incorrect");
        if(DUT.DUT_RF.RF[2] != 32'd100)
            $display("lw x2, 0(x0) incorrect");
        if(DUT.DUT_RF.RF[3] != 32'd101)
            $display("addi x3, x2, 1 incorrect");
        $display("Test 2 complete");
        
        //test 3, featuring addi, bne
        $display("Test 3, Branch");
        reset_dut;
        $readmemh("test3_branch.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 20; i++) begin
            @(posedge clk);
        end
        if(DUT.DUT_RF.RF[1] != 32'd5)
            $display("counter doesn't equal 5");
        $display("Test 3 complete");

        $finish;
    end
endmodule