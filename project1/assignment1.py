"""
    Author: sheqijin
    Update: 2019/11/2
"""


# converting BIN to DEC
# input: bit list (char list)
# output: int
def bin_to_dec(bits_list):
    return int(''.join(bits_list), base=2)


# converting DEC to BIN
# input: int
# output: bit list (char list)
def dec_to_bin(num):
    bits = bin(num)[2:]
    bits = '0' * max(0, 32 - len(bits)) + bits
    bits = list(bits)
    return bits


class Register(object):
    def __init__(self, name='default'):
        # the num of bits
        self.bits = 32
        # 32-bit store
        self.store = ['0' for _ in range(self.bits)]
        # then name of the register
        self.name = name

    def pulse(self, input_bits):
        assert len(input_bits) == self.bits
        for i in range(self.bits):
            self.store[i] = input_bits[i]
        print('<register %s has been updated>' % self.name)

    def get_register_bits(self):
        output_bit = [bit for bit in self.store]
        return output_bit


class Memory(object):
    class Cell(object):
        def __init__(self):
            # 8-bit cell
            self.bits = 8
            self.store = ['0' for _ in range(self.bits)]

        def read(self):
            output_bits = [bit for bit in self.store]
            return output_bits

        def write(self, input_bits):
            assert len(input_bits) == self.bits
            self.store = [bit for bit in input_bits]

    def __init__(self, cell_num=256):
        # the num of memory cells
        # regard of cost, the real cell num is 2^8
        self.cell_num = cell_num
        # the imitation of memory: a list of cells
        self.cell_list = [Memory.Cell() for _ in range(cell_num)]

    # read value from memory cells pointed by MAR value
    # mar_bits：value from MAR(binary)
    def read(self, mar_bits):
        mar_trans = bin_to_dec(mar_bits)
        assert mar_trans < self.cell_num
        # read the data from memory cell
        # ATTENTION: in normal situation, we should read 4 cell(Byte)
        output_bits_1 = self.cell_list[mar_trans].read()
        output_bits_2 = self.cell_list[mar_trans + 1].read()
        output_bits_3 = self.cell_list[mar_trans + 2].read()
        output_bits_4 = self.cell_list[mar_trans + 3].read()
        print('Read Data from Cell %d-%d' % (mar_trans, (mar_trans + 3)))
        # using small endian
        output_bits = output_bits_4 + output_bits_3 + output_bits_2 + output_bits_1
        return output_bits

    # write value from MDR to memory cells pointed by MAR value
    # mdr_bits: value from MDR(binary)
    # mar_bits：value from MAR(binary)
    def write(self, mdr_bits, mar_bits):
        mar_trans = bin_to_dec(mar_bits)
        assert mar_trans < self.cell_num
        # write the data to memory cell
        # ATTENTION: in normal situation, we should write 4 cell(Byte)
        # using small endian
        byte = 8
        self.cell_list[mar_trans].write(mdr_bits[byte * 3:byte * 4])
        self.cell_list[mar_trans + 1].write(mdr_bits[byte * 2:byte * 3])
        self.cell_list[mar_trans + 2].write(mdr_bits[byte * 1:byte * 2])
        self.cell_list[mar_trans + 3].write(mdr_bits[byte * 0:byte * 1])
        print('Write Data to Cell %d - %d' % (mar_trans, (mar_trans + 3)))

    def show(self):
        for i in range(self.cell_num // 8):
            ot = 'ob' + '0' * (8 - len(bin(i)[2:])) + bin(i)[2:]
            print(ot + '|' + ''.join(self.cell_list[i].read()))


class Simulation(object):
    def __init__(self):
        # memory
        self.MM = Memory()
        # program register
        self.PC = Register('PC')
        # memory address register
        self.MAR = Register('MAR')
        # memory data register
        self.MDR = Register('MDR')
        # code segment register(8086)
        self.CS = Register('CS')
        # data segment register(8086)
        self.DS = Register('DS')
        # instruction register
        self.IR = Register('IR')
        # general purpose registers (32)
        self.GR = [Register('GR' + str(i)) for i in range(32)]

    # update the PC register
    def _pc_increase(self):
        pc_bits = self.PC.get_register_bits()
        pc_trans = bin_to_dec(pc_bits)
        pc_trans = pc_trans + 4
        pc_bits = dec_to_bin(pc_trans)
        self.PC.pulse(pc_bits)

    # Instruction: Add
    def _add(self, r3_code, r1_code, r2_code):
        r1 = self.GR[bin_to_dec(r1_code)]
        r2 = self.GR[bin_to_dec(r2_code)]
        r3 = self.GR[bin_to_dec(r3_code)]
        # add value from r1 to r2, get new value
        r1_bits = r1.get_register_bits()
        print('read value from GR%d' % bin_to_dec(r1_code))
        r2_bits = r2.get_register_bits()
        print('read value from GR%d' % bin_to_dec(r2_code))
        r1_trans = bin_to_dec(r1_bits)
        r2_trans = bin_to_dec(r2_bits)
        r_sum_trans = r1_trans + r2_trans
        sum_bits = dec_to_bin(r_sum_trans)
        print(str(r1_trans), '+', str(r2_trans), '=', str(r_sum_trans))
        # write new value to r3
        r3.pulse(sum_bits)
        print('Write new value to GR%d' % bin_to_dec(r3_code))

    # Instruction: Load
    def _load(self, r_code, real_address_code):
        self.MAR.pulse(real_address_code)
        self.MDR.pulse(self.MM.read(self.MAR.get_register_bits()))
        self.GR[bin_to_dec(r_code)].pulse(self.MDR.get_register_bits())

    # Instruction: Store
    def _store(self, r_code, real_address_code):
        self.MDR.pulse(self.GR[bin_to_dec(r_code)].get_register_bits())
        self.MAR.pulse(real_address_code)
        self.MM.write(self.MDR.get_register_bits(), self.MAR.get_register_bits())

    def _get_instruction(self):
        print('[Get new instruction from PC]')
        self.MAR.pulse(self.PC.get_register_bits())
        self.MDR.pulse(self.MM.read(self.MAR.get_register_bits()))
        self.IR.pulse(self.MDR.get_register_bits())
        print("[New instruction has been load]")

    def _decode_and_execute(self):
        ir = self.IR.get_register_bits()
        op_code = ''.join(ir[:8])
        if op_code == '00000100':
            r1 = ir[8:16]
            r2 = ir[16:24]
            r3 = ir[24:32]
            print("Instruction: \'Add r%d, r%d, r%d\'" % (bin_to_dec(r1), bin_to_dec(r2), bin_to_dec(r3)))
            self._add(r1, r2, r3)
        if op_code == '00000010':
            r = ir[16:24]
            a = ir[24:32]
            print("Instruction: \'Load r%d, #%d\'" % (bin_to_dec(r), bin_to_dec(a)))
            # Direct addressing
            a = ['0' for _ in range(24)] + a
            self._load(r, a)
        if op_code == '00000011':
            r = ir[16:24]
            a = ir[24:32]
            print("Instruction: \'Store r%d, #%d\'" % (bin_to_dec(r), bin_to_dec(a)))
            # Direct addressing
            a = ['0' for _ in range(24)] + a
            self._store(r, a)

    def initialize(self):
        print('-----initalization-----')
        print('Initalize PC value')
        self.PC.pulse(list('00000000000000000000000000010000'))
        # data
        self.MM.write(list(dec_to_bin(37)), list(dec_to_bin(0)))
        self.MM.write(list(dec_to_bin(1697)), list(dec_to_bin(4)))
        # code
        self.MM.write(list('00000010' + '0' * 8 + '00000001' + '00000000'), list(dec_to_bin(16)))
        self.MM.write(list('00000010' + '0' * 8 + '00000010' + '00000100'), list(dec_to_bin(20)))
        self.MM.write(list('00000100' + '00000011' + '00000001' + '00000010'), list(dec_to_bin(24)))
        self.MM.write(list('00000011' + '0' * 8 + '00000011' + '00001000'), list(dec_to_bin(28)))
        print('------------------------------')

    def main(self):
        self.initialize()
        for i in range(4):
            # 取址
            self._get_instruction()
            # 译码,执行
            self._decode_and_execute()
            # 地址自增
            self._pc_increase()
            print('------------------------------')


if __name__ == '__main__':
    sim = Simulation()
    sim.main()
