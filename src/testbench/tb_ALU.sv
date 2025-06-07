`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/07/2025 11:48:54 AM
// Design Name: 
// Module Name: tb_ALU
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_ALU();
    localparam CLK_PERIOD = 10ns;

    parameter [3:0] ADD = 4'b0010,
                    SUB = 4'b0110,
                    AND = 4'b0000,
                    OR = 4'b0001;

    ALU DUT (.clk(clk), .n_rst(n_rst), .rd1(rd1), .rd2(rd2), .ALU_Operation(ALU_Operation), .out(out));
    
endmodule

/* 337-style testbench
    localparam CLK_PERIOD = 10ns;

    logic clk, n_rst;
    logic [3:0] ALU_Operation;
    logic [31:0] rd1, rd2, out;

    ALU DUT (.clk(clk), .n_rst(n_rst), .ALU_Operation(ALU_Operation), .out(out));

    typedef struct {
        logic [3:0] ALU_Operation;
        logic [31:0] rd1, rd2, out;
    } testVector;
    testVector test [];

    //clockgen
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

    task ALU_test_gen;
        input logic [3:0] tv_ALU_Operation;
        input logic [31:0] tv_rd1, tv_rd2;
        input logic [31:0] exp_out;
        input int idx
    begin
        test[idx].ALU_Operation = tv_ALU_Operation;
        test[idx].rd1 = tv_rd1;
        test[idx].rd2 = tv_rd2;
        test[idx].out = exp_out; 
    end
    endtask

    initial begin
        rd1 = 0;
        rd2 = 0;
        ALU_Operation = 0;

        n_rst = 1;
        test = new[4];

        reset_dut;
    end */


/* proxy-driven testbench
    typedef struct {
        logic [31:0] rd1, rd2;
        logic [3:0] ALU_Operation;
    } cmd_t; //command/input

    typedef struct {
        logic [31:0] out;
    }

    interface ALU_proxy;
        logic [31:0] rd1, rd2;
        logic clk, n_rst;
        logic [3:0] ALU_Operation;
        //new stuff
        logic start, done; 
        logic [31:0] result;

        typedef mailbox #(cmd_t) cmd_mbx;
        typedef mailbox #(result_t) result_mbx; 

        initial begin
            cmd_mbx send_cmd_mbx, mon_cmd_mbx;
            result_mbx result_mbx;

            send_cmd_mbx = new(1);
            mon_cmd_mbx = new(0);
            result_mbx = new(0);
        end
    endinterface 

    task send_op;
        input logic [31:0] rd1, rd2;
        input logic [3:0] ALU_Operation;
    begin
        cmd_t cmd;
        cmd.rd1 = rd1;
        cmd.rd2 = rd2;
        cmd.ALU_Operation = ALU_Operation;
        send_cmd_mbx.put(cmd);
    end
    endtask

    task get_cmd;
        output cmd_t cmd;
    begin
        mon_cmd_mbx.get(cmd);
    end
    endtask

    task get_result;
        output result_t result;
    begin
        result_mbx.get(result);
    end
    endtask

//sending operations
    always_ff @(negedge clk) begin //negedge, since we want to load DUT before posedge clk
        cmd_t cmd;
        if(!start & !done) begin
            if(send_cmd_mbx.try_get(cmd)) begin
                rd1 = cmd.rd1;
                rd2 = cmd.rd2;
                ALU_Operation = cmd.ALU_Operation;
                start = 1;
            end
            else if (start) begin
                if(done)
                    start = 0;
            end
        end
    end

    //monitoring and result loops
    logic prev_start;
    always_ff @(negedge clk) begin
        cmd_t cmd;
        if(start && !prev_start) begin
            cmd.rd1 = rd1;
            cmd.rd2 = rd2;
            cmd.ALU_Operation = ALU_Operation; //video used an "op2enum" converter?
            mon_cmd_mbx.put(cmd);
        end
        prev_start = start;
    end
    logic prev_done;
    always_ff @(negedge clk) begin
        if(done && !prev_done) 
            result_mbx.put(result);
        prev_done = done;
    end

    initial begin
        cmd_t cmd;
        result_t result;
        ALU_proxy.reset();
        ALU_proxy.send_op(9, 10, ADD);
        ALU_proxy.get_cmd(cmd);
        ALU_proxy.get_result(result);
        $display("%d %s %d = %d", cmd.rd1, cmd.ALU_Operation, cmd.rd2, result);
        if(result == (9 + 10)) begin
            $display("PASSSED");
        end
        else begin
            $display("FAILED");
        end
        $finish();    
    end

    //completely lost
    class ALU_proxy extends uvm_object;
        static ALU_proxy proxy = null; 
        static virtual interface ALU_bfm bfm;
        protected function new(name="proxy");
            super.new();
            if(!uvm_config_db #(virtual ALU_bfm)::get(null, "*", "bfm", this.bfm))
                `uvm_fatal("MONITOR", "Failed to get BFM")
        endfunction //new()
        static function ALU_proxy get();
            if(proxy == null)
                proxy = new();
            return proxy;
        endfunction
    endclass //className extends superClass
    */