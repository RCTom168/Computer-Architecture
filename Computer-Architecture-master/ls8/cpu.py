"""CPU functionality."""

import sys

# print(sys.argv)

# Arithmetic Logic Unit Branch Table OP_codes
ADD  = 0b10100000
AND  = 0b10101000
CALL = 0b01010000
CMP  = 0b10100111
DEC  = 0b01100110
DIV  = 0b10100011
HLT  = 0b00000001
INC  = 0b01100101
IRET = 0b00010011
JEQ  = 0b01010101
JLE  = 0b01011001
JLT  = 0b01011000
JMP  = 0b01010100
JNE  = 0b01010110
LD   = 0b10000011
LDI  = 0b10000010
MUL  = 0b10100010
OR   = 0b10101010
POP  = 0b01000110
PRA  = 0b01001000
PRN  = 0b01000111
PUSH = 0b01000101
RET  = 0b00010001
SHL  = 0b10101100
ST   = 0b10000100
SUB  = 0b10100001
XOR  = 0b10101011


NOP = 0b00000000

ADDI = 0b001000

 # Stack Pointer
SP = 7

# Flags
LT = 0b00000100
GT = 0b00000010
EQ = 0b00000001

class CPU:
    """Main CPU class."""  

    def __init__(self):
        """Construct a new CPU."""

        # Flag Register is cleared to 0
        self.fl = 0

        # Program Counter is cleared to 0
        # This is the index of the current instructions
        self.pc = 0
        
        # Initiate memory with 256 bits
        self.ram = [0] * 256

        # Create our 8 general purpose registers
        self.reg = [0] * 8

        # R0 - R6 are cleared to 0 at boot up
        self.reg[0] = 0
        self.reg[1] = 0
        self.reg[2] = 0
        self.reg[3] = 0
        self.reg[4] = 0
        self.reg[5] = 0
        self.reg[6] = 0

        # R7 is set to 0xF4
        self.reg[7] = 0xF4

        # Branch table with Instructions & OP_codes
        self.branch_table = {
            CALL  : self.call,
            HLT  : self.hlt,
            JEQ  : self.jeq,
            JMP  : self.jmp,
            JNE  : self.jne,
            LDI  : self.ldi,
            NOP  : self.nop,
            POP  : self.pop,
            PRN  : self.prn,
            PUSH  : self.push,
            RET  : self.ret,
            ST  : self.st,
            ADDI    : self.addi,
        }

    # CALL Register: Calls a subroutine (function) at the address stored in the register.
    def call(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram_write(self.pc + 2, self.reg[SP])
        self.pc = self.reg[operand_a]

    # HALT: Halt the CPU (and exit the emulator).
    def hlt(self, operand_a, operand_b):
        sys.exit(0)

    # JUMP to EQUAL: If equal flag is set (true), jump to the address stored in the given register.
    def jeq(self, operand_a, operand_b):
        # if flag is E (equal) jump to address stored in given register
        if self.fl == "E":
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2 

    # JUMP: Jump to the address stored in the given register.
    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    # JNE:
    def jne(self, operand_a, operand_b):
        if self.fl != "E":
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    # Load Immediate: Set the value of a register to an integer.
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        # Increment program counter by 3 steps in RAM
        self.pc += 3

    # No Operation: Passes when the value given is 0s
    def nop(self, operand_a, operand_b):
        self.pc += 1

    # POP: Pop the value at the top of the Stack into the given register.
    def pop(self, operand_a, operand_b):
        # get the value of SP and overwrite next register
        value = self.ram_read(self.reg[SP])
        self.reg[operand_a] = value
        # increment SP
        self.reg[SP] += 1
        self.pc += 2

    # PRINT: Print numeric value stored in the given register.
    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    #PUSH: Push the value in the given register on to the Stack. Decrement the Stack Pointer
    def push(self, operand_a, operand_b):
        # decrement SP
        self.reg[SP] -= 1
        # Get the value we want to store from the register and store it in ram
        self.ram_write(self.reg[operand_a], self.reg[SP])
        self.pc += 2

    # RETURN: Returns from a subroutine back to where we called from
    def ret(self, operand_a, operand_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    # STORE: Store value in registerB into the address stored in registerA.
    def st(self):
        reg_a = self.pc + 1
        reg_b = self.pc + 2
        reg_a_add = self.reg[self.ram_read(reg_a)]
        reg_b_val = self.reg[self.ram_read(reg_b)]
        self.ram_write(reg_a_add, reg_b_val)
        return True 

    # ADDI Extension: Add an immediate value to a register
    def addi(self, op_a, op_b):
        self.reg[op_a] += self.reg[op_b]
        
        self.pc += 2


    def load(self, filename=None):
        """Load a file from disk into memory."""
        address = 0
        with open(filename) as fp:
            for line in fp:
                comment_split = line.split("#")
                num = comment_split[0].strip()
                if num == '':  # ignore blanks
                    continue
                val = int(num, 2)
                self.ram[address] = val
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # ADDITION: Add the value in two registers and store the result in registerA.
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # SUBTRACTION: Subtract the value in the second register from the first, storing the result in registerA.
        elif op == "SUB": 
            self.reg[reg_a] -= self.reg[reg_b]

        # AND: Bitwise-AND the values in registerA and registerB, then store the result in registerA.
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]

        # COMPARE: Compare the values in 2 registers, change the flag accordingly depending on the values.
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = "LT"
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = "GT"
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl = "EQ"
            else:
                self.fl = 0
        
        # MODULO: Divide the value in the first register by the value in the second, storing the remainder of the result in registerA.
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]

        # MULTIPLY: Multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        
        # NOT: Perform a bitwise-NOT on the value in a register, storing the result in the register.
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]

        # OR: Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

        # SHIFT LEFT: Shift the value in registerA left by the number of bits specified in registerB, filling the low bits with 0.
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << 2

        # SHIFT RIGHT: Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> 2
        
        # XOR: Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        """prints what's stored in that specified address in RAM"""
        return self.ram[address]

    def ram_write(self, value, address):
        """Overwrites the address in ram with the value"""
        self.ram[address] = value


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while True:

            op_code = self.ram[self.pc]

            operand_a = self.ram[self.pc + 1]

            operand_b  = self.ram[self.pc + 2]

            if op_code in self.branch_table:
                self.branch_table[op_code](operand_a, operand_b)
                print("Hello World") 
                print(self.reg)
                print(self.pc)
            else: 
                self.pc += 1

if __name__ == '__main__':
    LS8 = CPU()
    LS8.load()

    for i in range(8):
        print(LS8.ram_read(i))