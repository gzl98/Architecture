# Question：
# Memory
#   32-bit address
#   8-bit cell
# Register
#   32 32-bit
# Program
#   Add the number in memory address 0 and 1 to address 3
#   Load r1, #0
#   Load r2, #1
#   Add r3, r1, r2
#   Store r3, #3
Separate_len = 76


def int2binstr(num, bits):
    """int类型转指定位数2进制字符串"""
    b = bin(num)[2:]
    return '0' * (bits - len(b)) + b


class Cell:
    """单元类，用于实现寄存器或Memory中的单元格，可指定位数，例如Register为32位，Memory为8位"""

    def __init__(self, bits):
        self.bits = bits  # 单元的总长度
        self.data = ''.join(['0' for _ in range(self.bits)])  # 设置全0初始化

    def read(self):
        """read函数，直接返回data"""
        return self.data

    def write(self, data: str):
        """write函数，直接将data写入，但是会先检测data的长度是否一致"""
        assert len(data) == self.bits
        self.data = data


class Register:
    """寄存器类"""

    def __init__(self, register_name=None, cells=1):
        """
        :param register_name: 寄存器类型
        :param cells: 寄存器内包含的单元个数
        """
        self.register = []  # 默认使用一个列表来表示寄存器
        self.register_name = register_name  # 寄存器的名字
        self.cells = cells  # 寄存器的单元数量，默认为1
        self.cell_list = [Cell(bits=32) for _ in range(self.cells)]  # 初始化

    def read(self, index=0):
        """从寄存器中读取32位数据"""
        if self.cells == 1:
            return self.cell_list[0].read()
        elif 0 <= index < self.cells:
            return self.cell_list[index].read()

    def write(self, data: str, index=0):
        """将32位数据写入寄存器，需要检测data的长度是否一致"""
        assert len(data) == self.cell_list[0].bits
        if self.cells == 1:
            self.cell_list[0].write(data)
        elif 0 <= index < self.cells:
            self.cell_list[index].write(data)


class MyMemory:
    """内存类"""

    def __init__(self, address_len=256):
        self.address_len = address_len  # 寻址长度，默认为8位寻址，即256长度
        self.memory = [Cell(bits=8) for _ in range(self.address_len)]  # 初始化内存
        self.program_index = self.address_len  # 初始化代码段指针

    def extend_memory(self, extend_size):
        """扩展内存数组"""
        for i in range(extend_size):
            self.memory.insert(self.program_index, Cell(bits=8))  # 添加一个内存单元
            self.program_index += 1  # 代码段指针向后移位

    def check_data_extend(self, index):
        """检查是否要扩展内存空间"""
        if index * 4 >= self.program_index:
            # 当数据段不够用时，扩展内存空间，实际上此方法不会触发，因为设定了寻址长度最大为8位
            self.extend_memory((index + 1) * 4 - self.program_index)

    def get_data(self, index):
        """获取指定index的数据"""
        index *= 4  # 乘以4来进行对齐
        return ''.join(reversed([self.memory[index + i].read() for i in range(4)]))  # 采用倒序读取的方式来读取数据

    def write_data(self, index, data: str, is_program=False):
        """向指定index写入数据"""
        if not is_program:
            # 如果写入的是非程序数据，则检测是否要进行内存扩展
            self.check_data_extend(index)
        index *= 4  # 乘以4来进行对齐
        bits = 32
        i = 0
        for j in range(4):
            self.memory[index + j].write(data[bits - (i + 8):bits - i])  # 采用倒序存储的方式来存入数据
            i += 8


class Instruction:
    """指令类"""

    def __init__(self, memory: MyMemory, MDR: Register, MAR: Register, GR: Register):
        self.memory = memory  # 获取内存变量
        self.GR = GR  # 获取通用寄存器
        self.MDR = MDR  # 获取MDR寄存器
        self.MAR = MAR  # 获取MAR寄存器
        self.instruction_name = None  # 定义指令名称
        self.instruction_code = None  # 定义指令代码

    def execute(self, operands: list):
        """定义指令的执行函数，用于具体执行"""
        pass

    def check_format(self, operands: list, address):
        """定义指令的格式检测函数，用于程序编译"""
        pass

    def mem2reg(self, src, des):
        # 实现内存到寄存器
        self.GR.write(self.memory.get_data(src), des)

    def reg2mem(self, src, des):
        # 实现寄存器到内存
        self.memory.write_data(des, self.GR.read(src))


class LoadInstruction(Instruction):
    """Load指令类"""

    def __init__(self, memory: MyMemory, MDR: Register, MAR: Register, GR: Register):
        super(LoadInstruction, self).__init__(memory, MDR, MAR, GR)
        self.instruction_name = "Load"  # 指令名称
        self.instruction_code = "10000001"  # 指令代码

    def check_format(self, operands: list, address):
        # 检测命令格式
        if len(operands) != 2:
            raise Exception(r"Operand error!")
        des, src = operands[0], operands[1]
        if not des.startswith('r') or not src.startswith('#'):
            raise Exception(r"Operand error!")
        else:
            # 命令格式正确后，提取操作数并转为机器码写入内存
            rs = int2binstr(int(src[1:]), 8)
            rt = '0' * 8
            rd = int2binstr(int(des[1:]), 8)
            machine_code = self.instruction_code + rs + rt + rd  # 构建机器码
            self.memory.write_data(address, machine_code, is_program=True)

    def execute(self, operands: list):
        """执行Load命令"""
        des, src = operands[0], operands[1]  # 获取源操作数和目的操作数
        print('Memory %d: %s' % (src, self.memory.get_data(src)))
        print('Register %d: %s' % (des, self.GR.read(des)))
        print("Load #%d to r%d" % (src, des))
        self.mem2reg(src=src, des=des)  # 执行内存到寄存器的转移
        print('Register %d: %s' % (des, self.GR.read(des)))


class AddInstruction(Instruction):
    """Add指令类"""

    def __init__(self, memory: MyMemory, MDR: Register, MAR: Register, GR: Register):
        super(AddInstruction, self).__init__(memory, MDR, MAR, GR)
        self.instruction_name = "Add"  # 指令名称
        self.instruction_code = "10000011"  # 指令代码

    def check_format(self, operands: list, address):
        # 检测命令格式
        if len(operands) != 3:
            raise Exception(r"Operands error!")
        des, src1, src2 = operands[0], operands[1], operands[2]

        if not des.startswith('r') or not src1.startswith('r') or not src2.startswith('r'):
            raise Exception(r"Operand error!")
        else:
            # 命令格式正确后，提取操作数并转为机器码写入内存
            rs = int2binstr(int(src1[1:]), 8)
            rt = int2binstr(int(src2[1:]), 8)
            rd = int2binstr(int(des[1:]), 8)
            machine_code = self.instruction_code + rs + rt + rd  # 构建机器码
            self.memory.write_data(address, machine_code, is_program=True)

    def execute(self, operands: list):
        """执行Add命令"""
        des, src1, src2 = operands[0], operands[1], operands[2]  # 获取源操作数和目的操作数
        print('Register %d: %s' % (src1, self.GR.read(src1)))
        print('Register %d: %s' % (src2, self.GR.read(src2)))
        print('Register %d: %s' % (des, self.GR.read(des)))
        print("Add r%d r%d to r%d" % (src1, src2, des))
        self.GR.write(self.binary_add(self.GR.read(src1), self.GR.read(src2)), des)  # 执行加法命令
        print('Register %d: %s' % (des, self.GR.read(des)))

    @staticmethod
    def binary_add(a: str, b: str):
        """加法器，简单实现了按位加"""
        a = a[::-1]
        b = b[::-1]
        f = False
        res = ''
        for i in range(32):
            if a[i] == '1' and b[i] == '1':
                if f:
                    res += '1'
                else:
                    res += '0'
                f = True
            elif a[i] == '0' and b[i] == '0':
                if f:
                    res += '1'
                else:
                    res += '0'
                f = False
            else:
                if f:
                    res += '0'
                    f = True
                else:
                    res += '1'
                    f = False
        return res[::-1]


class StoreInstruction(Instruction):
    """Store指令类"""

    def __init__(self, memory: MyMemory, MDR: Register, MAR: Register, GR: Register):
        super(StoreInstruction, self).__init__(memory, MDR, MAR, GR)
        self.instruction_name = "Store"  # 指令名称
        self.instruction_code = "10000010"  # 指令代码

    def check_format(self, operands: list, address):
        # 检测命令格式
        if len(operands) != 2:
            raise Exception(r"Operands error!")
        des, src = operands[1], operands[0]
        if not des.startswith('#') or not src.startswith('r'):
            raise Exception(r"Operands error!")
        else:
            # 命令格式正确后，提取操作数并转为机器码写入内存
            rs = int2binstr(int(src[1:]), 8)
            rt = '0' * 8
            rd = int2binstr(int(des[1:]), 8)
            machine_code = self.instruction_code + rs + rt + rd  # 构建机器码
            self.memory.write_data(address, machine_code, is_program=True)

    def execute(self, operands: list):
        """执行Load命令"""
        des, src = operands[1], operands[0]  # 获取源操作数和目的操作数
        print('Register %d: %s' % (src, self.GR.read(src)))
        print('Memory %d: %s' % (des, self.memory.get_data(des)))
        print("Store r%d to #%d", (src, des))
        self.reg2mem(src=src, des=des)  # 执行寄存器到内存的转移
        print('Memory %d: %s' % (des, self.memory.get_data(des)))


class Instructions:
    """
    指令集集合类
    """

    def __init__(self, memory: MyMemory, MDR: Register, MAR: Register, GR: Register):
        self.MAR = MAR
        self.MDR = MDR
        self.instructions = []  # 定义指令集集合
        self.memory = memory  # 载入内存对象
        self.GR = GR  # 载入通用寄存器对象
        self.init_instructions()  # 初始化指令集集合

    def init_instructions(self):
        """初始化指令集集合"""
        self.instructions.append(LoadInstruction(memory=self.memory, MDR=self.MDR, MAR=self.MAR, GR=self.GR))
        self.instructions.append(AddInstruction(memory=self.memory, MDR=self.MDR, MAR=self.MAR, GR=self.GR))
        self.instructions.append(StoreInstruction(memory=self.memory, MDR=self.MDR, MAR=self.MAR, GR=self.GR))


class Translater:
    """
    编译器类
    """

    def __init__(self, memory: MyMemory):
        self.memory = memory  # 载入内存对象
        self.instructions = Instructions(self.memory, None, None, None)  # 构建指令集集合对象

    def compile_code(self, file_name):
        """编译代码"""
        # 读取代码文件
        with open(file_name, 'r') as f:
            lines = f.readlines()
        print('Compile Codes:')
        # 计算代码段地址
        program_address = int(self.memory.address_len / 4) - len(lines)
        self.memory.program_index = program_address
        # 逐行编译
        for code_line in lines:
            # 读取代码
            print(code_line, end='')
            code_a = code_line.split(',')
            # 分割代码与参数
            instruction_name, p1 = tuple(code_a[0].strip().split(' '))
            p = [p1]
            for s in code_a[1:]:
                p.append(s.strip())
            # 代码与参数分割完毕
            for instruction in self.instructions.instructions:
                # 遍历指令集
                assert isinstance(instruction, Instruction)
                if instruction.instruction_name == instruction_name:
                    # 将对应的指令编译为机器码
                    instruction.check_format(p, program_address)
                    # 代码段地址加一
                    program_address += 1
                    break
        print('\nCodes compiled!')
        print('-' * Separate_len)


class CPU:
    """CPU类"""

    def __init__(self):
        self.memory = MyMemory()  # 构建内存对象
        self.memory_init()  # 初始化内存对象
        self.PC = Register('PC')  # PC寄存器
        self.MAR = Register('MAR')  # MAR寄存器
        self.MDR = Register('MDR')  # MDR寄存器
        self.IR = Register('IR')  # IR指令寄存器
        self.GR = Register('GR', cells=32)  # GR通用寄存器
        print('Registers initialized!')
        self.instructions = Instructions(memory=self.memory, MDR=self.MDR, MAR=self.MAR, GR=self.GR)  # 构建指令集集合对象
        print('Instructions initialized!')
        print('-' * Separate_len)

    def pc_auto_increase(self):
        # PC寄存器自增
        print('PC寄存器自增:')
        print(self.PC.read() + '(' + str(int(self.PC.read(), 2)) + ') => ', end='')
        self.PC.write(int2binstr(int(self.PC.read(), 2) + 1, 32))  # 向下一条代码的地址移动
        print(self.PC.read() + '(' + str(int(self.PC.read(), 2)) + ')')
        print('-' * Separate_len)

    def get_instruction(self):
        """取指令"""
        self.MAR.write(self.PC.read())  # 读取PC寄存器中的代码地址
        self.MDR.write(self.memory.get_data(int(self.MAR.read(), 2)))  # 从内存中读取数据到MDR寄存器
        self.IR.write(self.MDR.read())  # 将MDR寄存器的数据写入IR寄存器
        print('Get Instruction [' + self.IR.read() + ']')

    def memory_init(self):
        # 内存初始化
        self.memory.write_data(0, int2binstr(10, 32))  # 向内存的0号位添加数字10
        self.memory.write_data(1, int2binstr(15, 32))  # 向内存的1号位添加数字15
        print('Memory initialized!')

    def PC_instruction_init(self):
        # PC寄存器初始化
        self.PC.write(int2binstr(self.memory.program_index, 32))  # 向PC寄存器写入代码段地址
        print('PC Instructions initialized')
        print('-' * Separate_len)

    def execute_code(self):
        # 执行代码
        instruction_address = self.IR.read()  # 从IR寄存器中读取机器代码
        op_code = instruction_address[0:8]  # 读取指令代码
        src1 = int(instruction_address[8:16], 2)  # 读取源操作数1
        src2 = int(instruction_address[16:24], 2)  # 读取源操作数2
        des = int(instruction_address[24:32], 2)  # 读取目的操作数
        parameters = [des, src1, src2]  # 构成参数列表
        for instruction in self.instructions.instructions:
            # 寻找对应指令
            if instruction.instruction_code == op_code:
                # 执行相应的操作
                instruction.execute(parameters)
                break

    def program_is_end(self):
        # 识别程序是否执行完毕
        return int(self.PC.read(), 2) * 4 >= self.memory.address_len

    def run(self):
        translater = Translater(self.memory)  # 编译器
        translater.compile_code('codes.txt')  # 编译代码
        del translater
        self.PC_instruction_init()  # 初始化PC寄存器
        # 执行程序
        while not self.program_is_end():
            print('Run Code:')
            self.get_instruction()  # 取指令
            self.execute_code()  # 执行指令
            self.pc_auto_increase()  # PC自增
        print("Program End!")
        print('-' * Separate_len)

    def show_memory(self):
        # 展示内存
        i = 0
        for m in self.memory.memory:
            print(m.read())
            i += 1
            if i % 4 == 0:
                print()


if __name__ == '__main__':
    cpu = CPU()
    cpu.run()
    # cpu.show_memory()
