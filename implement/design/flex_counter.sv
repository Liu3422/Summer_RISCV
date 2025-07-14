`timescale 1ns / 10ps

module flex_counter #(
    parameter SIZE = 4
)(
    input logic clk, n_rst, clear, count_enable,
    input logic [SIZE - 1:0] rollover_val,
    output logic rollover_flag,
    output logic [SIZE - 1:0] count_out
);
logic [SIZE - 1:0] next_count; 
logic register_flag;
always_ff @(posedge clk, negedge n_rst) begin
    if(n_rst == 1'b0) begin
        count_out <= 4'b0; //this will also set next_count to zero in the comb block. 
        rollover_flag <= 0;
    end
    else begin
        rollover_flag <= register_flag; //this flag turns on. 
        count_out <= next_count; //count = 8
    end
end

always_comb begin
    next_count = count_out;
    // rollover_flag = register_flag;
    if(clear) begin //clear > enable
        next_count = 4'b0; 
    end
    else begin //clear is not asserted. //next = 7
        if (count_enable) begin
            if (count_out >= rollover_val) begin //rollover occurs
                next_count = 4'b0001;
            end else begin
                next_count += 4'b0001; //next = 8 at this point. 
            end
        end
        else begin
            next_count = next_count; //sanity check. asserts count_out when there is no clear. 
        end
    end
end
always_comb begin   
    if(next_count >= rollover_val) begin //next_count = 8 at this point. 
        register_flag = 1'b1; //flag is turned on. next_count = 8, count = 7]
        // next_count = 1'b1;
    end
    else begin
        register_flag = 1'b0;
    end 
  
end
    

endmodule
