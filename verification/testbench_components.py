
from bitstring import Bits
import random
import asyncio 
import cocotb
from cocotb.triggers import Timer, RisingEdge


MAX_32B_signed = 2**31 - 1
MIN_32B_signed = -(2**31)
MAX_32B_unsigned = 2**32 - 1
SHIFT_MASK = 0x1F
BYTE_MASK = 0xFF
HALF_MASK = 0x0000FFFF
HALF_HIGH_MASK = 0xFFFF0000
WORD_MASK = 0xFFFFFFFF #Used for sll/i and U-Type imm
B_IMM_MASK = 0b1111_1111_1111_0
J_IMM_MASK = 0b1111_1111_1111_1111_1111_0
U_IMM_MASK = 0x000FFFFF #little endian
NUM_WORDS = 32
STORE_LIM = 1024 

async def generate_clock(dut):
    """Generate clock pulses."""

    for cycle in range(1000000):
        dut.clk.value = 0
        await Timer(10, units="ns")
        dut.clk.value = 1
        await Timer(10, units="ns")

# Make this into a class? These functions sets/resets the dut. How to make async def class?
async def reset_dut(dut):
    print("Resetting DUT \n")
    dut.n_rst.value = 0
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    await Timer(10, units="ns")
    dut.n_rst.value = 1
    await Timer(10, units="ns")
    # dut = dut_fetch.randomize_RF(dut)
    # dut = dut_fetch.randomize_data(dut)
    return #dut
async def randomize_rf(dut, N_bits):
    print("Randomizing DUT \n")
    for i in range(32):
            dut.DUT_RF.RF[i].value = random.getrandbits(N_bits)
    await RisingEdge(dut.clk) 
    await Timer(10, units="ns")
    return 
async def randomize_data(dut, N_bits):
    print("Randomizing DUT \n")
    for i in range(NUM_WORDS):
            dut.DUT_Data.data_memory[i].value = random.getrandbits(N_bits)
    await RisingEdge(dut.clk) 
    await Timer(10, units="ns")
    return 
async def random_reset_dut(dut, N_bits):
    await reset_dut(dut)
    await randomize_data(dut, N_bits)
    await randomize_rf(dut, N_bits)
    return
async def set_reg_addi(dut, reg, funct3): #sets reg to value using addi
    instr = instruction()
    instr.gen_I()
    
    match Mfunct3[funct3][0]:
        case "lb" | "lbu": value = random.choice(range(0,STORE_LIM)) #NOTE: S-Type has the same randomization for funct 0,1,2
        case "lh" | "lhu": value = random.choice(range(0,STORE_LIM,2)) 
        case "lw": value = random.choice(range(0,STORE_LIM,4))
    instr.funct3 = Bits(int="0", length=3) #addi
    instr.imm = Bits(int=value, length=12)
    instr.rs1 = Bits(int="0", length=5)
    instr.rd = reg
    tb = testcase(instr, dut)
    tb.feed()
    await RisingEdge(dut.clk) 
    await Timer(10, units="ns")        
    dut = tb.dut
    # prior_rd1 = dut_fetch.reg(dut, instr.rs1) 
    # prior_memory = dut_fetch.memory(dut, prior_rd1, instr.imm.int)
    # return (prior_rd1, prior_memory)

#bitwise operations
def binary_to_signed(val, n_bits):
    if(val >= 2**(n_bits-1)):
        val -= 2**n_bits #converts to signed
    return val
def signed_to_unsigned(val):
    return val & ((1 << 32) - 1) #2's complement
def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n #logical right shift
def lshift(val, n): return (val % 0x100000000) << n #logical left shift. This is not preserving sign. 
def imm_B(val):
    return binary_to_signed(val[0:13].int & B_IMM_MASK, 13) #remove the last bit
def imm_J(val):
    return binary_to_signed(val[0:21].int & J_IMM_MASK, 21)
def imm_U(val): #this extracts the instr field imm, not the "actual" << 12 value
    return binary_to_signed((val[0:32].int & U_IMM_MASK), 20)
def imm_U_actual(val): #this extracts the U-Type imm to be added to the upper word, already shifted.
    return imm_U(val) << 12

op = {
    Bits(bin="0110011", length=7) : "R-Type",
    Bits(bin="0010011", length=7) : "I-Type",
    Bits(bin="0000011", length=7) : "I-Type Load", 
    Bits(bin="0100011", length=7) : "S-Type", 
    Bits(bin="1100011", length=7) : "B-Type",
    Bits(bin="1101111", length=7) : "J-Type",
    Bits(bin="1100111", length=7) : "I-Type Jump",
    Bits(bin="0110111", length=7) : "U-Type Load",
    Bits(bin="0010111", length=7) : "U-Type PC"
}
Uop = {
    Bits(bin="0110111", length=7) : "lui",
    Bits(bin="0010111", length=7) : "auipc"
}
Rfunct3 = { #first entry is funct7=0, second is funct7=0x20
    #how to change this to something where I don't need to specify [0] normally?
    #gut reaction: linked list
    Bits(uint="0", length=3) : ["add", "sub"],
    Bits(uint="1", length=3) : ["sll"],
    Bits(uint="2", length=3) : ["slt"], 
    Bits(uint="3", length=3) : ["sltu"],
    Bits(uint="4", length=3) : ["xor"], 
    Bits(uint="5", length=3) : ["srl", "sra"],
    Bits(uint="6", length=3) : ["or"], 
    Bits(uint="7", length=3) : ["and"],
}
Mfunct3 = { #load and store funct3 conversion. NOTE: store only has 0,1,2, for funct3
    Bits(uint="0", length=3) : ["lb", "sb", "Byte"],
    Bits(uint="1", length=3) : ["lh", "sh", "Half"],
    Bits(uint="2", length=3) : ["lw", "sw", "Word"],
    Bits(uint="4", length=3) : ["lbu", "Unsigned-Byte"],
    Bits(uint="5", length=3) : ["lhu", "Unsigned-Half"]
}
Bfunct3 = { #B-Type conversion
    Bits(uint="0", length=3) : "beq",
    Bits(uint="1", length=3) : "bne",
    Bits(uint="4", length=3) : "blt",
    Bits(uint="5", length=3) : "bge",
    Bits(uint="6", length=3) : "bltu",
    Bits(uint="7", length=3) : "bgeu"
}
ALU_Operation = {
    int("0010", 2) : "ADD",
    int("0110", 2) : "SUB",
    int("0000", 2) : "AND",
    int("0001", 2) : "OR",
    int("0011", 2) : "XOR",
    int("0100", 2) : "SLL",
    int("0101", 2) : "SRL",
    int("0111", 2) : "SRA",
    int("1000", 2) : "SLT",
    int("1001", 2) : "SLTU",
    int("1100", 2) : "SLTI",
    int("1101", 2) : "SLTUI"
}

class dut_fetch(): #fetches value from DUT
    def __init__(DUT): #maybe have access to all submodules?
        DUT.rf = DUT.DUT_RF
    #Basic fetching without logic/checks
    def reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.signed_integer
    def set_reg(DUT, bits_index, value): #sets a single register value, returns the DUT. Consider making this a part of different class (write_dut)?
        DUT.DUT_RF.RF[bits_index.uint].value = value
        return DUT
    def unsigned_reg(DUT, bits_index):
        return DUT.DUT_RF.RF[bits_index.uint].value.integer
    def imm(DUT):
        return DUT.imm_out.value.signed_integer
    def imm_B(DUT):
        return DUT.signed_imm.value.signed_integer
    def imm_J(DUT):
        return DUT.J_imm.value.signed_integer
    def imm_U(DUT): #trivial. identical to dut_fetch.imm
        return dut_fetch.imm(DUT)
    def unsigned_imm(DUT):
        return DUT.imm_out.value.integer
    def control(DUT):
        # signals = DUT.debug_control #concate of control sigs
        # print(f"Control: {signals}")
        print(f"ALUOp: {DUT.ALUOp.value}")
        print(f"ALU_Operation: {ALU_Operation[DUT.ALU_Operation.value.integer]}")
        print(f"ALU_Control instr: {DUT.DUT5.instr.value}")
        print(f"MemtoReg: {DUT.MemtoReg.value}")
        print(f"MemRead: {DUT.MemRead.value}")
        print(f"RegWr: {DUT.RegWr.value}")
        print(f"MemWr: {DUT.MemWr.value}")
        # print(f"RegWr: {signals[1]}")
    def memory(DUT, rd1, imm): 
        word_addr = (rd1 + imm)>>2
        return DUT.DUT_Data.data_memory[word_addr].value.signed_integer 
    def unsigned_memory(DUT, rd1, imm):
        word_addr = (rd1 + imm)>>2
        return DUT.DUT_Data.data_memory[word_addr].value.integer
    def PC(DUT): #unsigned
        return DUT.PC.value.integer
    #More advanced fetching
    def memory_mask(rd1, imm, funct3, field): #(dut_fetch.reg(rs1), dut_fetch.imm, self.funct3)
        byte_offset = (rd1 + imm) % 4 #mask for last 2 bits
        match Mfunct3[funct3][0]: #monitor only the relevant place in memory
            case "lb" | "lbu": 
                field = (field & (BYTE_MASK << (8*byte_offset))) >> (8*byte_offset)
                if(Mfunct3[funct3][0] == "lb"): field = binary_to_signed(field, 8)
            case "lh" | "lhu": 
                if (byte_offset == 0):
                    field &= HALF_MASK
                elif (byte_offset == 2):
                    field = (field & HALF_HIGH_MASK) >> 16 #Right shift half a word, since we are only reading the half-word
                else: #memory address misalignment
                    print(f"Memory address is misaligned,{byte_offset} != 0 or 2")
                    field &= HALF_MASK #out of region of operation
                if(Mfunct3[funct3][0] == "lh"): field = binary_to_signed(field, 16)
            case "lw" : pass
        return field
    def register_mask(instr): #returns fetched (rd1, rd2, imm)
        DUT = instr.dut
        (rd1, rd2, imm) = (dut_fetch.reg(DUT, instr.rs1), dut_fetch.reg(DUT, instr.rs2), dut_fetch.imm(DUT))
        match Rfunct3[instr.funct3][0]: #This should only apply to R + I type.
            case "sltu":
                rd1 = dut_fetch.unsigned_reg(DUT, instr.rs1)
                rd2 = dut_fetch.unsigned_reg(DUT, instr.rs2)
                imm = dut_fetch.unsigned_imm(DUT)
            case "srl" | "sll": 
                imm &= SHIFT_MASK #only [0:4] bits count towards shift in RV spec
                rd2 &= SHIFT_MASK
        return (rd1, rd2, imm)
    def check_R_I(self, expected, actual): #returns fail value
        if(expected) != (actual):
            print(f"Instruction Failed")
            print(f"final={dut_fetch.reg(self.dut, self.rd)}, rd1={dut_fetch.reg(self.dut, self.rs1)}, imm={dut_fetch.imm(self.dut)}")
            print(f"unsigned: final={dut_fetch.unsigned_reg(self.dut, self.rd)}, rd1={dut_fetch.unsigned_reg(self.dut, self.rs1)}, imm={dut_fetch.unsigned_imm(self.dut)}")
            return 1
        else:
            return 0
    def check_memory_instr(self, expected, actual): #returns fail value
        fail = 0
        (dut, prior_rd1, prior_memory) = (self.dut, self.prior_rd1, self.prior_memory)
        memory = dut_fetch.memory(dut, prior_rd1, dut_fetch.imm(dut))
        if(self.rs1 == self.rd and op[self.opcode] == "I-Type Load"): 
            print(f"Edge case: rs1 = rd")
        elif (memory != dut.DUT_Data.word_data.value): #edge case results in a different memory address within the DUT, thus irrelevant to check model vs DUT memory values.
            print(f"Memory doesn't match, probably address mismatch: memory={bin(memory)}, word_data={dut.DUT_Data.word_data.value}")
        #basic checks    
        if(expected) != (actual): 
            print(f"Binary: expected={bin(expected)}, actual={bin(actual)}")
            print(f"half_read={dut.DUT_Data.half_read.value}")
            fail += 1
        if ((op[self.opcode] == "I-Type Load") and (memory != prior_memory)):
            print(f"FAIL: Detected change in memory during load: {memory}!={prior_memory}")
            fail += 1
            
        if(fail != 0):                
            print(f"Instruction Failed")
            if(op[self.opcode] == "I-Type Load"):
                if(memory != dut.data_read.value):
                    assert((dut.DUT_Data.MemWr.value == 0) and (dut.DUT_Data.MemRead.value == 1))
                    print(f"data_read: {dut.data_read.value}, memory: {memory}")
            elif(op[self.opcode] == "S-Type"):
                print(f"write_data:{dut.write_data.value}")                    
                assert((dut.DUT_Data.MemWr.value == 1) and (dut.DUT_Data.MemRead.value == 0))
            print(f"addr={dut.DUT_Data.addr.value.integer},word_addr={dut.DUT_Data.word_addr.value.integer}, byte_offset={dut.DUT_Data.byte_offset.value.integer}")
        return fail
    def check_branch_instr(self, expected, actual):
        fail = 0
        imm = imm_B(self.imm)
        imm_actual = dut_fetch.imm_B(self.dut)
        if(expected != actual):
            (rd1, rd2) = (dut_fetch.reg(self.dut, self.rs1), dut_fetch.reg(self.dut, self.rs2))
            unsigned_value = rd1 - rd2
            if((unsigned_value > MAX_32B_signed) or (unsigned_value < MIN_32B_signed)):
                print("Overflow occured")
                return -1 
            fail += 1
            print(f"Instruction failed: {(expected - actual)} difference")
            print(f"Signed: ALU_in1={self.dut.ALU_in1.value.signed_integer}, ALU_in2={self.dut.ALU_in2.value.signed_integer}, ALU_Out={self.dut.ALU_Out.value.signed_integer}")
            print(f"branch_cond: {self.dut.branch_cond.value}")
        if(imm != imm_actual):
            fail += 1
            print(f"Incorrect immediate value for model: {bin(imm)} != {bin(imm_actual)}")
            print(f"self.imm[1:13].bin = {self.imm[0:13].bin}")
            print(f"Difference between imm: {(imm - imm_actual)}")
            print(f"Raw imm bits [1:13]: {self.imm[0:13].bin}")
            print(f"Bit 12 (sign): {self.imm[12]}")
            print(f"After sign extension: {binary_to_signed(self.imm[0:13].int, 13)}")
        return fail
    def check_jump_instr(self, expected_rd, actual_rd, expected_PC, actual_PC, imm, imm_actual):
        fail = 0
        print(f"Expected rd: {expected_rd}")
        if(expected_rd != actual_rd):
            fail += 1
            print(f"Instruction failed: {(expected_rd - actual_rd)} difference")
        print(f"Expected PC: {expected_PC}")
        if(expected_PC != actual_PC):
            fail += 1
            print(f"PC failed: {(expected_PC - actual_PC)} difference")
            print(f"rd1={dut_fetch.reg(self.dut, self.rs1)} imm:{imm_actual}")
        if(imm != imm_actual): #this error prints twice, but I want it to only print for PC check
            print(f"Immediate mismatch: DUT={imm_actual}, Model={imm}")
            fail += 1
        return fail
    def check_U_instr(self, expected, actual):
        fail = 0
        imm_actual = dut_fetch.imm_U(self.dut)
        imm_actual_field = imm_U_actual(self.imm)
        if(expected != actual):
            fail += 1
            print(f"Instruction failed: {(expected - actual)} difference")
        if(imm_actual != imm_actual_field):
            print(f"Mismatching immediate values: DUT={bin(imm_actual)}")
            print(f"self.imm[0:32].bin: {self.imm[0:32].bin}")
            print(f"self.imm[12:32].bin: {self.imm[12:32].bin}")
            fail += 1
        return fail
class instruction(): #generates the instruction to feed into DUT/testbench
    def __init__(self):
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.funct3 = None
        self.funct7 = None
        self.opcode = None
        self.imm = None
    def gen_random(self): #generates all possible fields
        self.rs1 = Bits(uint=random.randint(1, 31), length=5) #x1-31 randomly chosen
        self.rs2 = Bits(uint=random.randint(1, 31), length=5) #x1-31 randomly chosen
        self.rd  = Bits(uint=random.randint(1, 31), length=5)
        self.funct3 = Bits(uint=random.getrandbits(3), length=3)
        self.funct7 = Bits(uint=random.choice(["0", "32"]), length=7) #32 would only apply to SUB and SRA
        self.opcode = Bits(uint=random.choice([int("0110011",2), int("0010011",2), int("0000011",2), int("0100011",2), int("1100011",2), 
                                            int("1101111",2), int("1100111",2), int("0110111",2), int("0010111",2)]),
                                            length=7)
        self.imm = Bits(int=random.randint(-(2**31), 2**31 - 1), length = 32)
        return self
    def gen_R(self, DUT): #generates a random R-type test
        self = self.gen_random()
        if((Rfunct3[self.funct3][0] != "add") and (Rfunct3[self.funct3][0] != "srl")): #Switches funct7 for invalid instructions
            self.funct7 = Bits(uint="0", length=7)
        if ((Rfunct3[self.funct3][0] == "sll") or (Rfunct3[self.funct3][0] == "srl")): #avoid illegal instruction: negative shift
            if(dut_fetch.reg(DUT, self.rs2) <= 0): 
                print("Illegal negative shift detected: swapping instruction")
                self.funct7 = Bits(uint="0", length=7) 
                self.funct3 = Bits(uint=random.choice([0,2,3,4,6,7]), length=3) #switch to everything other than shift 
        self.opcode = Bits(bin="0110011", length=7)
        return self
    def gen_R_instr(self): #generates the R-type instr
        return Bits().join([self.funct7, self.rs2, self.rs1, self.funct3, self.rd, Bits(bin='0110011', length=7)])
    def gen_I(self): #generates a random I-type test
        self = self.gen_random()
        self.opcode = Bits(bin="0010011", length=7)
        if(Rfunct3[self.funct3][0] == "sll"): #valid imm for SLLI
            self.imm = Bits(int=random.choice(range(0,31)), length=12)
        elif(Rfunct3[self.funct3][0] == "srl"): #valid imm for SRLI, SRAI
            self.imm = Bits(int=(random.choice([0,1024]) + random.choice(range(0, 127))), length=12)
            if(self.imm.int > 1024):
                self.funct7 = Bits(uint="32", length=7)
            else:
                self.funct7 = Bits(uint="0", length=7)
        return self
    def gen_I_instr(self): #generates the I-type instr
        return Bits().join([self.imm[0:12], self.rs1, self.funct3, self.rd, self.opcode])        
        # return Bits().join([self.imm[19:31], self.rs1, self.funct3, self.rd, self.opcode])
    def gen_I_load(self): #generates a random I-type load test
        self = self.gen_random()
        self.opcode = Bits(bin="0000011", length=7)
        self.funct3 = Bits(uint=random.choice([0,1,2,4,5]), length=3)
        match Mfunct3[self.funct3][0]: #natural alignment constraint
            case "lb" | "lbu": self.imm = Bits(uint=random.choice(range(32)), length=12)
            case "lh" | "lhu": self.imm = Bits(uint=random.choice(range(0,32,2)), length=12) 
            case "lw": self.imm = Bits(uint=random.choice(range(0,32,4)), length=12) 
        return self
    def gen_S(self):
        self = self.gen_random()
        self.opcode = Bits(bin="0100011", length=7)
        self.funct3 = Bits(uint=random.choice([0,1,2]), length=3)
        match Mfunct3[self.funct3][1]: #natural alignment constraint
            case "sb": self.imm = Bits(uint=random.choice(range(STORE_LIM)), length=12)
            case "sh": self.imm = Bits(uint=random.choice(range(0,STORE_LIM,2)), length=12) 
            case "sw": self.imm = Bits(uint=random.choice(range(0,STORE_LIM,4)), length=12) 
        return self
    def gen_S_instr(self): 
        return Bits().join([self.imm[0:7], self.rs2, self.rs1, self.funct3, self.imm[7:12], self.opcode])
        # return Bits().join([self.imm[20:26], self.rs2, self.rs1, self.funct3, self.imm[27:31], Bits(bin="0100011", length=7)])
    def gen_B(self):
        self = self.gen_random()
        self.funct3 = Bits(uint=random.choice([0,1,4,5,6,7]), length=3)
        self.opcode = Bits(bin="1100011", length=7)
        return self
    def gen_B_instr(self): #NOTE: imm for B is [12:1], not [11:0]. [0:1] is still 1 bit, converts boolean to 1-bit. Bits is Big Endian
        return Bits().join([self.imm[0:1], self.imm[2:8], self.rs2, self.rs1, self.funct3, self.imm[8:12], self.imm[1:2], self.opcode]) 
    def gen_J(self):
        self = self.gen_random()
        self.opcode = Bits(bin="1101111", length=7)
        return self
    def gen_J_instr(self): #NOTE: imm for J is [20:1]. 
        return Bits().join([self.imm[0:1], self.imm[10:20], self.imm[9:10], self.imm[1:9], self.rd, self.opcode])
    def gen_U(self):
        self = self.gen_random()
        self.opcode = Bits(bin=random.choice(["0110111", "0010111"]))
        return self
    def gen_U_instr(self): #NOTE: imm for U is [31:12]. The two U-Type instr have different op-codes
        return Bits().join([self.imm[12:32], self.rd, self.opcode])
    def gen_I_jump(self):
        self = self.gen_I()
        self.opcode = Bits(bin="1100111", length=7)
        self.funct3 = Bits(uint="0", length=3)
        return self
    def bin(self): #generates the binary instruction
        match op[self.opcode]:
            case "R-Type": return (self.gen_R_instr()).bin
            case "I-Type" | "I-Type Load" | "I-Type Jump": return (self.gen_I_instr()).bin
            case "S-Type": return (self.gen_S_instr()).bin
            case "B-Type": return (self.gen_B_instr()).bin
            case "J-Type": return (self.gen_J_instr()).bin
            case "U-Type PC" | "U-Type Load": return (self.gen_U_instr()).bin 

class testcase(instruction): #tests a singular instruction
    def __init__(self, instr, DUT, prior_rd1=0, prior_memory=0):
        self.__dict__.update(instr.__dict__)
        self.dut = DUT
        self.prior_rd1 = prior_rd1
        self.prior_memory = prior_memory
        
    def decode(self, test_num): #prints instr-type, name, register nums, imm value, and instruction binary
        print(f"Test {test_num}")
        print(f"Instruction type: {op[self.opcode]}")
        word_imm = self.imm[0:12] #sanity check
        match op[self.opcode]:
            case "R-Type":
                match self.funct7.uint:
                    case 0: print(f"Name: {Rfunct3[self.funct3][0]}") 
                    case 32: print(f"Name: {Rfunct3[self.funct3][1]}") #only place that uses self.funct3[1]
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint} rs2={self.rs2.uint}")
            case "I-Type" | "I-Type Jump" | "I-Type Load": #maybe make this look better?
                if((Rfunct3[self.funct3][0] == "srl") and (self.imm.int > 1024)): #srai special case
                    print(f"Name: srai")
                elif(Rfunct3[self.funct3][0] == "sltu"): #sltiu is unsigned
                    print(f"Name: sltiu")
                    print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={word_imm.uint}")
                    return
                elif(op[self.opcode] == "I-Type Load"):
                    print(f"Name: {Mfunct3[self.funct3][0]}")
                elif(op[self.opcode] == "I-Type Jump"): 
                    print(f"Name: jalr")
                else:
                    print(f"Name: {Rfunct3[self.funct3][0] + "i"}")
                print(f"Registers: rd={self.rd.uint}, rs1={self.rs1.uint}, Imm={word_imm.int}")
            case "S-Type":
                print(f"Name: {Mfunct3[self.funct3][1]}")
                print(f"Registers: rs1={self.rs1.uint}, rs2={self.rs2.uint}, Imm={word_imm.int}")
            case "B-Type":
                B_imm = imm_B(self.imm)
                print(f"Name: {Bfunct3[self.funct3]}")
                print(f"Registers: rs1={self.rs1.uint}, rs2={self.rs2.uint}, Imm={B_imm}")
            case "J-Type":
                J_imm = imm_J(self.imm)
                print(f"Name: jal ")
                print(f"Registers: rd={self.rd.uint}, imm={J_imm}")
            case "U-Type Load" | "U-Type PC":
                U_imm = imm_U(self.imm) #instr field displayed in instr
                print(f"Name: {Uop[self.opcode]}")
                print(f"Registers: rd={self.rd.uint}, imm={U_imm}")
        if(len(self.bin()) != 32):
            print(f"Invalid instruction length: {len(self.bin())} != 32")
        print(f"Instruction: {(self.bin())}") 
    def R_I_model(self, field, rd1):
        match Rfunct3[self.funct3][0]: #All R-type and their I-type counterparts
            case "add":
                if((self.funct7.uint == 32) and (op[self.opcode] == "R-Type")): return rd1 - field #sub
                else: return rd1 + field 
            case "sll": return binary_to_signed(lshift(rd1, field) & WORD_MASK, 32) #rd1 << field. Prevents all overflow with mask.
            case "slt": return 1 if (binary_to_signed(rd1,32) < binary_to_signed(field, 32)) else 0
            case "sltu": return 1 if rd1 < field else 0
            case "xor": return rd1 ^ field
            case "srl": #NOTE: python's >> is arithmetic
                if(self.funct7.uint == 32):  return rd1 >> (field) #arithmetic
                else: return binary_to_signed(rshift(rd1, field), 32) #logical
            case "or": return (rd1 | field)
            case "and": return (rd1 & field)
            case _: 
                print(f"Model Error")
                return 0
    def model(self, prior): #returns the expected rd value
        #prior always has prior[0] = rd, prior[1] = rd1, and prior[2] can be rd2 or none
        #load: prior = [rd, M, rd1]
        #store: prior =  [M, rd1, rd2] 
        #branch: prior = [PC, rd1, rd2]
        #jal/jalr = [rd, PC, (rd1 if jalr)]
        J_imm = imm_J(self.imm)
        U_imm = imm_U_actual(self.imm)
        #NOTE: DUT values shouldn't be extracted here, only expected test values.
        match op[self.opcode]: #setting field operand (masking, signed vs unsigned, rd2 vs memory vs imm, etc.)
            case "R-Type": return testcase.R_I_model(self, field=prior[2], rd1=prior[1])
            case "I-Type": 
                match Rfunct3[self.funct3][0]:
                    case "sltu": field = (self.imm[0:12]).uint
                    case "srl"|"sll": field = self.imm.int & SHIFT_MASK
                    case _: field = (self.imm[0:12]).int
                return testcase.R_I_model(self, field, rd1=prior[1])
            case "I-Type Load": return prior[1] #rd
            case "S-Type": #rd2 masking
                (rd1, rd) = (prior[1] , prior[2])
                rd = prior[2]
                match Mfunct3[self.funct3][1]: #expected value is always from rd, lsb first
                    case "sb": field = binary_to_signed((rd & BYTE_MASK),8) 
                    case "sh": 
                        field = rd & HALF_MASK
                        if(((rd1+self.imm.int)>>2) == 2): #NOTE: shift must occur before signed conversion
                            field = (field >> 16)     
                        if(Mfunct3[self.funct3][1] == "sh"): field = binary_to_signed(field, 16)
                    case "sw": field = rd
                return field
            case "B-Type": #if statement checking. Pretty simple here, since python already has it
                branch = signed_to_unsigned(prior[0] + imm_B(self.imm)) #PC = prior[0] 
                PC_inc = signed_to_unsigned(prior[0] + 4)
                match Bfunct3[self.funct3]:
                    case "beq": return branch if (prior[1] == prior[2]) else PC_inc
                    case "bne": return branch if (prior[1] != prior[2]) else PC_inc
                    case "blt": return branch if (prior[1] < prior[2]) else PC_inc
                    case "bge": return branch if (prior[1] >= prior[2]) else PC_inc
                    case "bltu": return branch if (prior[1] < prior[2]) else PC_inc 
                    case "bgeu": return branch if (prior[1] >= prior[2]) else PC_inc
            case "J-Type": return [binary_to_signed(prior[1] + 4, 32), signed_to_unsigned(prior[1] + J_imm)] #prior[1] = PC NOTE: 2 values to model. 
            case "I-Type Jump": return [binary_to_signed(prior[1] + 4, 32), signed_to_unsigned(prior[2] + self.imm[0:12].int)]#prior = [XX, PC, rd1] NOTE: 2 values to model
            case "U-Type Load": return U_imm
            case "U-Type PC": return binary_to_signed((prior[1] + U_imm), 32) #prior[1] = PC
    def monitor(self, operation): #returns values read from DUT. By far the longest object, look into making it shorter.
        #will match the order of fields in instructions: add rd, rs1, rs2
        # "pre"  : won't print imm 
        # "post" : will return only the expected value
        rd1 = self.prior_rd1
        rd = dut_fetch.reg(self.dut, self.rd)
        match op[self.opcode]: #fetches and prints relevant instruction values
            case "R-Type":
                (rd1, rd2, imm) = dut_fetch.register_mask(self)
                if(operation == "post"): 
                    print(f"Actual: rd={rd}, rd1={rd1}, rd2={rd2}")
                    return rd
                elif(operation == "pre"): 
                    print(f"Pre-instruction: rd={rd}, rd1={rd1}, rd2={rd2}")
                    return [rd, rd1, rd2]
            case "I-Type":
                (rd1, rd2, imm) = dut_fetch.register_mask(self)
                if(operation == "post"): #irrelevant prior imm field ignored
                    print(f"Actual: rd={rd}, rd1={rd1}, imm={imm}")
                    return rd
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, rd1={rd1}")
                    return [rd, rd1]
            case "I-Type Load": 
                memory = dut_fetch.memory_mask(rd1, self.imm.int, self.funct3, dut_fetch.memory(self.dut, rd1, self.imm.int))
                if(operation == "post"):
                    print(f"Actual: rd={rd}, M[{rd1}(rd1)+{dut_fetch.imm(self.dut)}(imm)]={memory}")
                    return rd
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, M[{rd1}(rd1)+{self.imm}(imm)]={memory}") #no immediate displayed here, less information available
                    print(f"Word-Address:{(rd1 + self.imm.int)>>2}, Byte-Address:{(rd1 + self.imm.int)}")
                    return [rd, memory, rd1]
            case "S-Type":
                rd2 = dut_fetch.reg(self.dut, self.rs2)
                memory = dut_fetch.memory_mask(rd1, self.imm.int, self.funct3, dut_fetch.memory(self.dut, rd1, self.imm.int))
                if(operation == "post"):
                    print(f"Actual: M={memory}, rd1={rd1}, imm={dut_fetch.imm(self.dut)}, rd2={rd2}")
                    return memory
                elif(operation == "pre"):
                    print(f"Pre-instruction: M={memory}, rd1={rd1}, rd2={rd2}")
                    print(f"Word-Address:{(rd1 + self.imm.int)>>2}, Byte-Address:{(rd1 + self.imm.int)}")
                    return [memory, rd1, rd2] #no imm value to obtain before clk 
            case "B-Type": 
                PC = dut_fetch.PC(self.dut)
                match Bfunct3[self.funct3]:
                    case "bltu" | "bgeu": (rd1, rd2) = (dut_fetch.unsigned_reg(self.dut, self.rs1), dut_fetch.unsigned_reg(self.dut, self.rs2))
                    case _: (rd1, rd2) = (dut_fetch.reg(self.dut, self.rs1), dut_fetch.reg(self.dut, self.rs2))
                if(operation == "post"):
                    print(f"Actual: PC={PC}, rd1={rd1}, rd2={rd2}, imm={dut_fetch.imm_B(self.dut)}")
                    return PC
                elif(operation == "pre"):
                    print(f"Pre-instruction: PC={PC}, rd1={rd1}, rd2={rd2}")
                    return [PC, rd1, rd2]
            case "J-Type": #jal
                PC = dut_fetch.PC(self.dut)
                if(operation == "post"):
                    print(f"Actual: rd={rd}, PC={PC}, imm={dut_fetch.imm_J(self.dut)}")
                    return [rd, PC]
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, PC={PC}")
                    return [rd, PC]
            case "I-Type Jump": #jalr               
                PC = dut_fetch.PC(self.dut)
                rd1 = dut_fetch.reg(self.dut, self.rs1)
                if(operation == "post"):
                    print(f"Actual: rd={rd}, PC={PC}, rd1={rd1}, imm={dut_fetch.imm(self.dut)}")
                    return [rd, PC]
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, PC={PC}, rd1={rd1}")
                    return [rd, PC, rd1]
            case "U-Type Load":
                if(operation == "post"):
                    print(f"Actual: rd={rd}, imm={dut_fetch.imm_U(self.dut)}")
                    return rd
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}")
                    return [rd,0] #just to make code work for now!
            case "U-Type PC":
                PC = dut_fetch.PC(self.dut)
                if(operation == "post"):
                    print(f"Actual: rd={rd}, PC={PC}, imm={dut_fetch.imm_U(self.dut)}")
                    return rd
                elif(operation == "pre"):
                    print(f"Pre-instruction: rd={rd}, PC={PC}")
                    return [rd, PC]
    def checker(self, expected, actual): #NOTE: doesn't feature overflow handling due to "await"/async property of reset_dut
        fail = 0
        match op[self.opcode]: #basic check of values/registers of each instruction
            case "R-Type" | "I-Type": 
                print(f"Expected rd: {expected}")
                fail = dut_fetch.check_R_I(self, expected, actual)  
            case "I-Type Load": 
                print(f"Expected rd: {expected}")
                fail = dut_fetch.check_memory_instr(self, expected, actual)
            case "S-Type": 
                print(f"Expected Memory: {expected}")
                fail = dut_fetch.check_memory_instr(self, expected, actual)
            case "B-Type":
                print(f"Expected PC: {expected}")
                fail = dut_fetch.check_branch_instr(self, expected, actual)
            case "J-Type":
                    fail = dut_fetch.check_jump_instr(self, expected[0], actual[0], expected[1], actual[1], imm_J(self.imm), dut_fetch.imm_J(self.dut))
            case "I-Type Jump":                
                    fail = dut_fetch.check_jump_instr(self, expected[0], actual[0], expected[1], actual[1], self.imm[0:12].int, dut_fetch.imm(self.dut))
            case "U-Type Load" | "U-Type PC":
                print(f"Expected rd: {expected}")
                fail = dut_fetch.check_U_instr(self, expected, actual)

        if(fail > 0): #take fail count out of individual checker, for possible future extension (more extensive checks, etc.)
            print(f"{fail} incorrect test(s)\n") #NOTE: This is per singular instruction
        elif(fail == -1): #invalid test due to overflow (will update to include other cases)
            print("Test is invalid\n")
        else:
            print(f"Success! \n")
        return
    def feed(self): #feeds instruction directly to DUT (beware of race conditions if using fetch_reg)
        self.dut.instr_cocotb.value = int(self.bin(), 2)        
class environment(testcase): #creates the whole testing environment
    def __init__(self, testcase, num_test):
        self.__dict__.update(testcase.__dict__)
        self.num_test = num_test
        self.prior = None
        self.expected = None
        self.types = None #Instruction types to test. Default is all

    async def basic_CRT(self): #the constrained random testing featured in previous cocotb testbenches.
        for i in range(self.num_test):
            await self.gen_all()
            self.decode(i)
            self.feed()
            
            self.prior = self.monitor("pre") #prior rs1, rs2, rd register values of DUT
            await RisingEdge(self.dut.clk) 
            await Timer(10, units="ns")        
            
            self.expected = self.model(self.prior) 
            self.actual = self.monitor("post")
            overflow_occured = await self.overflow_checker()
            if (overflow_occured == False):
                self.checker(self.expected, self.actual)
    async def gen_all(self): #directly updates self's attributes
        instr_type = random.choice([0,1,2,3,4,5,6,7])
        instr = instruction()
        match instr_type:
            case 0: instr.gen_R(self.dut)
            case 1: instr.gen_I()
            case 2: #need to return prior memory and rd1
                instr.gen_I_load()
                await set_reg_addi(self.dut, instr.rs1, instr.funct3) #how to make this all one function? NOTE: instr in this function are add/addi, not load/store 
                self.prior_rd1 = dut_fetch.reg(self.dut, instr.rs1) 
                self.prior_memory = dut_fetch.memory(self.dut, self.prior_rd1, instr.imm.int)
            case 3: instr.gen_I_jump()
            case 4: 
                instr.gen_S()
                await set_reg_addi(self.dut, instr.rs1, instr.funct3) 
                self.prior_rd1 = dut_fetch.reg(self.dut, instr.rs1) 
                self.prior_memory = dut_fetch.memory(self.dut, self.prior_rd1, instr.imm.int)
            case 5: instr.gen_B()
            case 6: instr.gen_J()
            case 7: instr.gen_U()
        self.__dict__.update(instr.__dict__)       
    async def overflow_checker(self): #returns whether overflow occurred
        match op[self.opcode]:
            case "J-Type" | "I-Type Jump":
                for expected_value in self.expected:
                    if((expected_value > MAX_32B_unsigned)): #Overflow check
                        print(f"Unsigned overflow detected: {expected_value} \n")
                        return True
                return False
            case "I-Type Load":
                if(Mfunct3[self.funct3][0] == "lbu" or Mfunct3[self.funct3][0] == "lhu"):
                    if((self.expected > MAX_32B_unsigned)): #Overflow check
                            print(f"Unsigned overflow detected: {expected_value} \n")
                            return True
                    return False
            case "B-Type": #needs another overflow check for rd1-rd2
                if((self.expected > MAX_32B_unsigned)): #Overflow check
                        print(f"Unsigned overflow detected: {expected_value} \n")
                        return True
                return False
        if (self.expected.bit_length() > 64): 
            print(f"Severe overflow detected: {self.expected.bit_length()} bits") 
            await random_reset_dut(self.dut)
            return True
        elif((self.expected > MAX_32B_signed) or (self.expected < MIN_32B_signed)): #Overflow check
            print(f"Signed overflow detected: {self.expected} \n")
            return True
        else:
            return False
        