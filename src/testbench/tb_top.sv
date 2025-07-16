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
        @(posedge clk); //start testing again. Put/command occurs at posedge clk.
    end
    endtask
// integer failed_tests;
    initial begin
        n_rst = 1;
        // failed_tests = 0;
        //test 1, featuring addi, add, sub
        $display("Test 1, Arith");
        reset_dut;
        $readmemh("test1_arith.mem", DUT.DUT_instr.instruction_memory);

        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
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
        $display("\nTest 2, Memory");
        reset_dut;
        $readmemh("test2_memory.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
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
        $display("\nTest 3, Branch");
        reset_dut;
        $readmemh("test3_branch.mem", DUT.DUT_instr.instruction_memory);
        for(int i = 0; i < 19; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if(DUT.DUT_RF.RF[1] != 32'd5) 
            $display("counter doesn't equal 5");
        $display("Test 3 complete\n");
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
        for(int i = 0; i < 7; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if(DUT.DUT_RF.RF[1] != 32'd5)
            $display("x1 doesn't equal 5");        
        if(DUT.DUT_RF.RF[2] != 32'd3)
            $display("x2 doesn't equal 3");
        $display("Test 4 complete\n");

        // //test5, fibonaci test. Currently too difficult
        // $display("Test 5, fibonacci test");
        // reset_dut;
        // $readmemh("test5_fib.mem", DUT.DUT_instr.instruction_memory);
        // for(int i = 0; i < 100; i++) 
        //     @(posedge clk);
        // if(DUT.DUT_RF.RF[10] != 32'd55)
        //     $display("test is wrong");
        // $display("Actual, %d", DUT.DUT_RF.RF[10]);
        // $display("Test 5 complete");

        //test6, jal and jalr tests.
        $display("Test 6, basic jal and jalr tests");
        reset_dut;
        $readmemh("test6_jump.mem", DUT.DUT_instr.instruction_memory);
        
        $display("Test 6, jal");
        for(int i = 0; i < 5; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if(DUT.DUT_RF.RF[2] == 32'd1)
            $display("jal test is wrong, jump didn't occur and instr not skipped");
        else if(DUT.DUT_RF.RF[3] != 32'd2)
            $display("jal test is wrong, didn't jump to right location");
        else if(DUT.DUT_RF.RF[1] != 32'd4)
            $display("jal test is wrong, didn't store return address");
        else
            $display("Test Passed!");
        
        reset_dut;
        $readmemh("test6a_jalr.mem", DUT.DUT_instr.instruction_memory);
        $display("Test 6a, jalr");
        for(int i = 0; i < 4; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if(DUT.DUT_RF.RF[5] != 32'd8)
            $display("jalr test is wrong, incorrect return address (8):", DUT.DUT_RF.RF[5]);
        else if(DUT.DUT_RF.RF[3] != 32'd2)
            $display("jalr test is wrong, jumped to wrong place (missed important instruction, 2): ", DUT.DUT_RF.RF[3]);
        else if(DUT.DUT_RF.RF[2] != 0)
            $display("jalr test is wrong, didn't jump (0):", DUT.DUT_RF.RF[2]);
        else
            $display("Test Passed!");
        $display("Test 6 complete\n");

        $display("Test 7, lui auipc");
        reset_dut;
        $readmemh("test7a_lui.mem", DUT.DUT_instr.instruction_memory);
        $display("Test 7a, lui");
        for(int i = 0; i < 3; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if (DUT.DUT_RF.RF[1] !== 32'h12345000)
            $display("lui x1 is wrong: %h != 12345000", DUT.DUT_RF.RF[1]);
        else if (DUT.DUT_RF.RF[2] !== 32'hFFFFF000)
            $display("lui x2 is wrong: %h != FFFFF000", DUT.DUT_RF.RF[2]);
        else    
            $display("Test Passed!");

        reset_dut;
        $readmemh("test7b_auipc.mem", DUT.DUT_instr.instruction_memory);
        $display("Test 7a, auipc");
        for(int i = 0; i < 5; i++) begin
            @(posedge clk);
            $display("PC: %08h, instr: %08h", DUT.PC, DUT.instr);
        end
        if (DUT.DUT_RF.RF[3] !== 32'h00001000)
            $display("auipc x3 is wrong: %h != 00001000", DUT.DUT_RF.RF[3]);
        else if (DUT.DUT_RF.RF[4] !== 32'h0000200C)
            $display("auipc x4 is wrong: %h != 0000200C", DUT.DUT_RF.RF[4]);
        else    
            $display("Test Passed!");
        $finish;
    end
endmodule