"""CPU functionality."""

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
SP = 7
MULT2PRINT = 0b00011000
# JMP = 0b01010100
# JEQ = 0b01010101
# JNE = 0b01010110
# CMP = 0b10100111
# PRA = 0b01001000

import sys
import pdb

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[SP] = 243
        self.ram = [0] * 256
        self.pc = 0
        self.fl = 0b0
        self.branchtable = {}
        self.branchtable[0b10000010] = self.reg_write
        self.branchtable[0b01000111] = self.print_reg
        self.branchtable[0b01000101] = self.push_stack
        self.branchtable[0b01000110] = self.pop_stack
        self.branchtable[0b00011000] = self.mult_2_print
        self.branchtable[0b01010100] = self.handle_jmp
        self.branchtable[0b01001000] = self.handle_pra

    def load(self):
        """Load a program into memory."""
        try:
            address = 0
            cmd_file = sys.argv[1]
            with open(cmd_file) as f:
                for line in f:
                    # remove any comments "#"
                    cmd_split = line.split("#")
                    command = cmd_split[0].strip()

                    if command == "":
                        # ignore blank lines
                        continue
                    
                    value = int(command, 2)
                    self.ram[address] = value
                    address += 1
                
        except FileNotFoundError:
            print(f"Error. File {cmd_file} not found")
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            return self.reg[reg_a]
        
        elif op == "CMP":
            if reg_a == reg_b:
                # set E flag to true
                set_bit = (1 | self.fl)
                self.fl = set_bit
            else:
                # set E flag to false
                set_bit = (0 | self.fl)
                self.fl = set_bit
            if reg_a > reg_b:
                # set G flag to true
                set_bit = (1 << 1 | self.fl)
                self.fl = set_bit
            else:
                # set G flag to false
                self.fl = self.fl | 0b0
                set_bit = (0 << 1 | self.fl)
                self.fl = set_bit
            if reg_a < reg_b:
                # set L flag to true
                set_bit = (1 << 2 | self.fl)
                self.fl = set_bit
            else:
                # set L flag to false
                set_bit = (0 << 2 | self.fl)
                self.fl = set_bit

        else:
            raise Exception("Unsupported ALU operation")

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
        # read value in self.pc
        running = True
        while running:
            IR = self.ram[self.pc]
            params = (IR >> 6)
            subroutine = ((IR >> 4) & 0b1) == 1

            if IR == 0b00000001: # HLT
                running = False
                break
            
            elif IR == 0b01010000: # CALL
                # push return address on stack
                return_address = self.pc + 2
                self.reg[SP] -= 1 #decrement sp
                self.ram[self.reg[SP]] = return_address
                # set the pc to the value in the register
                reg_num = self.ram[self.pc + 1]
                self.pc = self.reg[reg_num]
            
            elif IR == 0b00010001: # RET
                # pop the return address off stack
                # store it in the pc
                self.pc = self.ram[self.reg[SP]]
                self.reg[SP] += 1
            
            elif IR == 0b10100010: # MUL
                self.alu("MUL", self.ram[self.pc + 1], self.ram[self.pc + 2])
                self.pc += params
                self.pc += 1
            
            elif IR == 0b10100000: # ADD
                self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])
                self.pc += params
                self.pc += 1
                            
            elif IR == 0b10100111: #CMP
                self.alu("CMP", self.reg[self.ram[self.pc + 1]], self.reg[self.ram[self.pc + 2]])
                self.pc += params
                self.pc += 1
            
            elif IR == 0b01010101: # JEQ
                flag = (self.fl & 0b1)
                if flag:
                    # jump to the address stored in the given register
                    self.handle_jmp()
                else:
                    self.pc += params
                    self.pc += 1
             
            elif IR == 0b01010110: # JNE
                flag = (self.fl & 0b1)
                if not flag:
                    # jump to the address stored in the given register
                    self.handle_jmp()
                else:
                    self.pc += params
                    self.pc += 1
            
            else: # HELPER METHODS
                self.branchtable[IR]()
                if not subroutine:
                    self.pc += params
                    self.pc += 1
            
    def ram_write(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.ram[address] = value
        return f"Wrote {value} to RAM address: {address}"

    def ram_read(self, address):
        return self.ram[address]

    def reg_write(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[address] = value
        return f"Wrote {value} to REG address: {address}"

    def reg_read(self):
        address = self.ram[self.pc + 1]
        return self.reg[address]

    def print_reg(self):
        address = self.ram[self.pc + 1]
        print(self.reg[address])

    def push_stack(self):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.reg[self.ram[self.pc + 1]]

    def pop_stack(self):
        copy = self.ram[self.reg[SP]]
        self.reg[self.ram[self.pc + 1]] = copy
        self.reg[SP] += 1

    def mult_2_print(self):
        reg = 0
        print(self.reg[reg] * 2)

    def handle_jmp(self):
        self.pc = self.reg[self.ram[self.pc + 1]]

    def handle_pra(self):
        print(chr(self.reg[self.ram[self.pc + 1]]))
        self.pc += 2