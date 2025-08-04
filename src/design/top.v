module top (
        clk,
        n_rst,
        write_data
);
        reg _sv2v_0;
        input wire clk;
        input wire n_rst;
        output wire [31:0] write_data;
        reg PC_wait;
        reg [31:0] PC;
        reg [31:0] PC_Next;
        wire [31:0] instr;
        always @(posedge clk or negedge n_rst)
                if (!n_rst) begin
                        PC <= 0;
                        PC_wait <= 0;
                end
                else begin
                        if (PC_wait)
                                PC <= PC_Next;
                        PC_wait <= 1'b1;
                end
        wire zero;
        wire UncondJump;
        wire jal_cond;
        wire jalr_cond;
        reg branch_cond;
        wire [1:0] PCSrc;
        wire [2:0] funct3;
        wire [31:0] imm_out;
        wire [31:0] rd1;
        wire [31:0] signed_imm;
        wire [31:0] J_imm;
        assign funct3 = instr[14:12];
        wire [31:0] ALU_Out;
        always @(*) begin
                if (_sv2v_0)
                        ;
                branch_cond = 0;
                if (PCSrc == 2'b01)
                        case (funct3)
                                3'd0: branch_cond = zero;
                                3'd1: branch_cond = !zero;
                                3'd4: branch_cond = $signed(ALU_Out) < 0;
                                3'd5: branch_cond = $signed(ALU_Out) >= 0;
                                3'd6: branch_cond = ALU_Out > rd1;
                                3'd7: branch_cond = ALU_Out <= rd1;
                                default: branch_cond = 0;
                        endcase
        end
        assign jal_cond = UncondJump & (PCSrc == 2'b01);
        assign jalr_cond = UncondJump & (PCSrc == 2'b10);
        assign signed_imm = {{19 {imm_out[12]}}, imm_out[12:0]};
        assign J_imm = {{11 {imm_out[20]}}, imm_out[20:1], 1'b0};
        always @(*) begin
                if (_sv2v_0)
                        ;
                if (jal_cond)
                        PC_Next = PC + J_imm;
                else if (branch_cond)
                        PC_Next = PC + signed_imm;
                else if (jalr_cond)
                        PC_Next = rd1 + signed_imm;
                else
                        PC_Next = PC + 4;
        end
        fetch_instr #(.NUM_INSTR(64)) DUT_instr(
                .clk(clk),
                .n_rst(n_rst),
                .PC(PC),
                .instr(instr)
        );
        wire RegWr;
        wire ALUSrc;
        wire MemWr;
        wire MemRead;
        wire MemtoReg;
        wire Auipc;
        wire Utype;
        wire [1:0] ALUOp;
        control DUT2(
                .instr(instr[6:0]),
                .PCSrc(PCSrc),
                .RegWr(RegWr),
                .ALUSrc(ALUSrc),
                .MemWr(MemWr),
                .MemRead(MemRead),
                .MemtoReg(MemtoReg),
                .ALUOp(ALUOp),
                .UncondJump(UncondJump),
                .Auipc(Auipc),
                .Utype(Utype)
        );
        wire [9:0] debug_control;
        assign debug_control = {PCSrc, RegWr, ALUSrc, MemWr, MemRead, MemtoReg, ALUOp, UncondJump};
        wire [31:0] writeback;
        wire [31:0] rd2;
        decode_reg_file DUT_RF(
                .clk(clk),
                .n_rst(n_rst),
                .RegWr(RegWr),
                .read_reg1(instr[19:15]),
                .read_reg2(instr[24:20]),
                .write_reg(instr[11:7]),
                .write_data(writeback),
                .rd1(rd1),
                .rd2(rd2)
        );
        wire [3:0] ALU_Operation;
        wire [31:0] ALU_in1;
        wire [31:0] ALU_in2;
        assign ALU_in2 = (ALUSrc ? imm_out : rd2);
        assign ALU_in1 = (Utype ? (Auipc ? PC : 32'b00000000000000000000000000000000) : rd1);
        ALU DUT4(
                .ALU_Operation(ALU_Operation),
                .in1(ALU_in1),
                .in2(ALU_in2),
                .out(ALU_Out),
                .zero(zero)
        );
        ALU_control DUT5(
                .instr({instr[30], funct3}),
                .ALUOp(ALUOp),
                .ALU_Operation(ALU_Operation)
        );
        wire [31:0] data_read;
        memory_reg_file #(.NUM_WORDS(1024)) DUT_Data(
                .clk(clk),
                .n_rst(n_rst),
                .MemWr(MemWr),
                .MemRead(MemRead),
                .addr(ALU_Out[11:0]),
                .write_data(rd2),
                .data_read(data_read),
                .funct3(funct3)
        );
        assign writeback = (UncondJump ? PC + 4 : (MemtoReg ? data_read : ALU_Out));
        imm_gen DUT7(
                .instr(instr),
                .imm_out(imm_out)
        );
        initial _sv2v_0 = 0;
endmodule