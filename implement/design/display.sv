`timescale 1ns / 1ps
module display ( 
    input logic clk, n_rst, 
    input logic write_ready, rollover_flag,
    input logic [31:0] writeback,
    output logic shift_strobe, 
    output logic [3:0] display_char,
    output logic [7:0] ssd_en
);
// Displays MSB first and continuously cycles until rollover_flag from display_count. 
typedef enum logic [4:0] {INIT, FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH, SEVENTH, EIGHTH} state_t;
state_t state, next;

    always_ff @(posedge clk, negedge n_rst) begin
        if(!n_rst) begin
            state <= INIT;
            shift_strobe <= 0;
            display_char <= 4'b0;
            ssd_en <= 8'b0;
        end
        else begin
            state <= next;
            shift_strobe <= n_shift_strobe;
            display_char <= n_display_char;
            ssd_en <= n_ssd_en;
        end
    end

    logic n_shift_strobe;
    logic [3:0] n_display_char;
    logic [7:0] n_ssd_en;

    always_comb begin   
        //common state
        n_shift_strobe = 0;
        n_display_char = 4'b0;
        n_ssd_en = 8'b0;

        next = state;
        case(state)
        default: begin
            n_shift_strobe = 0;
            n_display_char = 4'b0;
            n_ssd_en = 8'b0;
        end
        INIT: begin //nothing changes from default
            n_ssd_en = 8'b0;
            n_display_char = 4'b0;
            n_shift_strobe = 0; 
            if(write_ready) 
                next = FIRST;
        end
        FIRST: begin
            n_ssd_en = 8'b1 << 7;
            n_display_char = writeback[31:28];
            next = SECOND;
        end
        SECOND: begin
            n_ssd_en = 8'b1 << 6;
            n_display_char = writeback[27:24];
            next = THIRD;
        end
        THIRD: begin
            n_ssd_en = 8'b1 << 5;
            n_display_char = writeback[23:20];
            next = FOURTH;
        end
        FOURTH: begin
            n_ssd_en = 8'b1 << 4;
            n_display_char = writeback[19:16];
            next = FIFTH;
        end
        FIFTH: begin
            n_ssd_en = 8'b1 << 3;
            n_display_char = writeback[15:12];
            next = SIXTH;
        end
        SIXTH: begin
            n_ssd_en = 8'b1 << 2;
            n_display_char = writeback[11:8];
            next = SEVENTH;
        end
        SEVENTH: begin
            n_ssd_en = 8'b1 << 1;
            n_display_char = writeback[7:4];
            next = EIGHTH;
        end
        EIGHTH: begin
            n_ssd_en = 8'b1;
            n_display_char = writeback[3:0];
            n_shift_strobe = 1'b1;
            if(rollover_flag) 
                next = INIT;
            else
                next = FIRST;
        end
        endcase
    end
endmodule
