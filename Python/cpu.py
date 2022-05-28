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

# Cycles
cycles = np.uint8(0)
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


def tick():
    global cycles
    while cycles != 0:
        print("Tick!")
        cycles -= 1
        time.sleep(558.65922*10**(-9)) # Sleep for 1.79 MHz = 558.65922 nanoseconds

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
