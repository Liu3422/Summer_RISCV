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
        
        // //test 3, featuring addi, bne
        $display("Test 3, Branch");
        reset_dut;
        $readmemh("test3_branch.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 20; i++) begin
            @(posedge clk);
        end
        if(DUT.DUT_RF.RF[1] != 32'd5) //FOR WHATEVER REASON, ALU OUTPUTS 1 + 1 = 1 (RD1 = 1, RD2 = 2, ALU_OPERATION = ADD (2))
            $display("counter doesn't equal 5");
        $display("Test 3 complete");
        /*The Code in question:
        addi x1, x0, 0       # counter = 0
        addi x2, x0, 5       # limit = 5
        loop:
        addi x1, x1, 1       # counter++
        bne x1, x2, loop     # if counter != 5, loop
        */


        //test 4, adding multiple times to a single register
        $display("Test 4, Add to same register");
        reset_dut;
        $readmemh("test4_add_same_reg.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 6; i++) begin
            @(posedge clk);
        end
        if(DUT.DUT_RF.RF[1] != 32'd5)
            $display("x1 doesn't equal 5");        
        if(DUT.DUT_RF.RF[2] != 32'd3)
            $display("x2 doesn't equal 3");
        $display("Test 4 complete");

        // //test5, fibonaci test. Takes in an index term 'n' on t0/x10 and returns the Fn fib term.
        // $display("Test 5, fibonacci test");
        // reset_dut;
        // $readmemh("test5_fib.mem", DUT.DUT_instr.instruction_memory);
        // DUT.DUT_RF.RF[5] = 32'd10; //10th term
        // for(int i = 0; i < 100; i++) 
        //     @(posedge clk);
        // if(DUT.DUT_RF.RF[10] != 32'd55)
        //     $display("test is wrong");
        // $display("Actual, %d", DUT.DUT_RF.RF[10]);
        // $display("Test 5 complete");

        //test6, jal and jalr tests.
        $display("Test 6, basic jal and jalr tests");
        reset_dut;
        $display("Test 6, jal");
        $readmemh("test6_jump.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 5; i++) 
            @(posedge clk);
        if(DUT.DUT_RF.RF[2] == 32'd1)
            $display("test is wrong, jump didn't occur and instr not skipped");
        else if(DUT.DUT_RF.RF[3] != 32'd2)
            $display("jal test is wrong, didn't jump to right location");
        else
            $display("Test Passed!");
        reset_dut;
        $display("Test 6a, jalr");
        $readmemh("test6a_jalr.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 6; i++) 
            @(posedge clk);
        if(DUT.DUT_RF.RF[5] != 32'd12)
            $display("test is wrong, incorrect return address (12):", DUT.DUT_RF.RF[5]);
        else if(DUT.DUT_RF.RF[3] != 32'd2)
            $display("test is wrong, jumped to wrong place (missed important instruction, 2): ", DUT.DUT_RF.RF[3]);
        else if(DUT.DUT_RF.RF[2] != 0)
            $display("test is wrong, didn't jump (0):", DUT.DUT_RF.RF[2]);
        else
            $display("Test Passed!");

        $finish;
    end
endmodule