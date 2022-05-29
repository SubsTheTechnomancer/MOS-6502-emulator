import sys
import numpy as np
import time

# Program Counter
pc = np.uint16(0)
# Stack Pointer 
sp = np.uint8(0)
# Accumulator
a = np.uint8(0)
# Index Register X
x = np.uint8(0)
# Index Register Y
y = np.uint8(0)
# Status Register
st = np.uint8(0)

# RAM of size 64KB
ram = np.zeros(shape=(64000),dtype=np.uint8)

# Flipped page
flipped = 0
# Cycles
cycles = 0
# Tickspeed
tickspeed = 558.65922*10**(-9) # 1.79 MHz = 558.65922 ns, default for non-PAL

def get_flag(flag):

    # Get only flag value of st
    flag_val={
        'c': st & 0x01,
        'z': st & 0x02,
        'i': st & 0x04,
        'd': st & 0x08,
        'b': st & 0x10,
        'u': st & 0x20,
        'v': st & 0x40,
        'n': st & 0x80 
    }

    return flag_val.get(flag,0)

def set_flag(flag,bit):
    global st

    # Flag is being set: OR operation
    flagon={
        'c': st | 0x01,
        'z': st | 0x02,
        'i': st | 0x04,
        'd': st | 0x08,
        'b': st | 0x10,
        'u': st | 0x20,
        'v': st | 0x40,
        'n': st | 0x80 
    }

    # Flag is being unset: AND NOT operation
    flagoff={
        'c': st & ~0x01,
        'z': st & ~0x02,
        'i': st & ~0x04,
        'd': st & ~0x08,
        'b': st & ~0x10,
        'u': st & ~0x20,
        'v': st & ~0x40,
        'n': st & ~0x80 
    }

    if bit != 0:
        st = flagon.get(flag,st)
    else:
        st = flagoff.get(flag,st)

def interrupt_request():
    global ram,sp

    if get_flag('i'):
        return
    
    hi_byte = np.uint8(pc>>8)
    lo_byte = np.uint8(pc)
    ram[0x0100 + sp],sp = hi_byte,sp-1
    ram[0x0100 + sp],sp = lo_byte,sp-1

    ram[0x0100 + sp],sp = st,sp-1

    lo_byte = ram[0xfffe]
    hi_byte = ram[0xffff]
    pc = np.uint8((hi_byte<<8)|lo_byte)

    set_flag('i',1)
    set_flag('b',1)

def nonmaskable_interrupt():
    global ram,sp
    
    hi_byte = np.uint8(pc>>8)
    lo_byte = np.uint8(pc)
    ram[0x0100 + sp],sp = hi_byte,sp-1
    ram[0x0100 + sp],sp = lo_byte,sp-1

    ram[0x0100 + sp],sp = st,sp-1

    lo_byte = ram[0xfffa]
    hi_byte = ram[0xfffb]
    pc = np.uint8((hi_byte<<8)|lo_byte)

    set_flag('i',1)
    set_flag('b',1)

# All Addressing Modes that require pc

def zp():
    # Zero page addressing
    global pc
    pc = np.uint8(pc+1)
    addr = np.uint16(ram[pc-1])
    return addr

def zpx():
    # Zero page with X register offset
    global pc
    pc = np.uint8(pc+1)
    addr = np.uint16(ram[pc-1]+x)
    return addr

def zpy():
    # Zero page with Y register offset
    global pc
    pc = np.uint8(pc+1)
    addr = np.uint16(ram[pc-1]+y)
    return addr

def abs():
    # Absolute addressing
    global pc
    lo,pc = ram[pc],np.uint8(pc+1)
    hi,pc = ram[pc],np.uint8(pc+1)
    addr = np.uint16((hi<<8)|lo)
    return addr

def absx():
    # Absolute with X register offset
    global pc,flipped
    lo,pc = ram[pc],np.uint8(pc+1)
    hi,pc = ram[pc],np.uint8(pc+1)
    addr = np.uint16(((hi<<8)|lo)+x)
    if hi < np.uint8((addr & 0xff00)>>8):
        flipped = 1
    return addr

def absy():
    # Absolute with Y register offset
    global pc,flipped
    lo,pc = ram[pc],np.uint8(pc+1)
    hi,pc = ram[pc],np.uint8(pc+1)
    addr = np.uint16(((hi<<8)|lo)+y)
    if hi < np.uint8((addr & 0xff00)>>8):
        flipped = 1
    return addr

def ind():
    # Indirect addressing
    global pc
    lo,pc = ram[pc],np.uint8(pc+1)
    hi,pc = ram[pc],np.uint8(pc+1)
    addr = np.uint16((hi<<8)|lo)
    return addr

def idx():
    # Indexed Indirect
    global pc
    offset,pc = ram[pc]+x,np.uint8(pc+1)
    lo = ram[offset]
    hi = ram[offset+1]
    addr = np.uint16((hi<<8)|lo)
    return addr

def idy():
    # Indirect Indexed
    global pc
    loloc,pc = ram[pc],np.uint8(pc+1)
    lo = ram[loloc]
    hi = ram[loloc+1]
    addr = np.uint16(((hi<<8)|lo)+y)
    if hi < np.uint8((addr & 0xff00)>>8):
        flipped = 1
    return addr

##########################
#   INSTRUCTIONS
##########################
# There are 255 slots, lots of them are unused.
##########################

#   OPCODE: $AD
#   Instruction: LDA
#   Addr Mode: abs

opcode={
    0x00 : '_00',
    0x01 : '_01',
    0xad : '_ad'
}

def _ad():
    global a,cycles

    addr = np.uint16(abs())
    a = ram[addr]

    cycles = 4
    if(flipped):
        cycles += 1
    
    set_flag('n',a&0x80)    # a is negative?
    set_flag('z',(a==0))    # a is zero?


def tick():
    global cycles
    while cycles != 0:
        print("Tick!")
        cycles -= 1
        flipped = 0
        time.sleep(558.65922*10**(-9)) # Sleep for 1.79 MHz = 558.65922 nanoseconds

def reset(vector):
    global pc
    pc = vector
    while(1):
        instr = np.uint8(ram[pc])
        pc = np.uint8(pc+1)
        opcode[instr]()
        tick()

def main():
    global tickspeed
    if(len(sys.argv)>1):
        if sys.argv[1] == 'NTSC':
            tickspeed = 558.65922*10**(-9) # 1.79 MHz = 558.65922 ns
        elif sys.argv[1] == 'PAL':
            tickspeed = 602.40964*10**(-9) # 1.66 MHz = 602.40964 ns

    tick()

if __name__ == '__main__':
    main()
