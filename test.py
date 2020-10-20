import math


class Memory(object):
    """ 本类实现仿真器的虚拟内存空间的各种功能 """

    def init_mem(self):
        """  用空白字符串清除 Cardiac 系统内存中的所有数据  """
        self.mem = ['' for i in range(0, 100)]
        self.mem[0] = '001'  #: 启动 Cardiac 系统.

    def get_memint(self, data):
        """  由于我们是以字符串形式(*string* based)保存内存数据的, 要仿真 Cardiac, 就要将字符串转化成整数. 如果是其他存储形式的内存, 如 mmap, 可以根据需要重写本函数.  """
        return int(self.mem[data])

    def pad(self, data, length=3):
        """  在数字前面补0  """
        orig = int(data)
        padding = '0' * length
        data = '%s%s' % (padding, abs(data))
        if orig < 0:
            return '-' + data[-length:]
        return data[-length:]


class IO(object):
    """ 本类实现仿真器的 I/O 功能. To enable alternate methods of input and output, swap this. """

    def init_reader(self):
        """  初始化 reader.  """
        self.reader = []  #: 此变量在类初始化后, 可以用来读取输入的数据.

    def init_output(self):
        """  初始化诸如： deck/paper/printer/teletype/ 之类的输出功能...  """
        self.output = []

    def read_deck(self, fname):
        """  将指令读到 reader 中.  """
        self.reader = [s.rstrip('\n') for s in open(fname, 'r').readlines()]
        self.reader.reverse()

    def format_output(self):
        """  格式化虚拟 I/O 设备的输出(output)  """
        return '\n'.join(self.output)

    def get_input(self):
        """  获取 IO 的输入(input), 也就是说用 reader 读取数据, 代替原来的 raw_input() .  """
        try:
            return self.reader.pop()
        except IndexError:
            # 如果 reader 遇到文件结束标志(EOF) 就用 raw_input() 代替 reader.
            return input('INP: ')[:3]

    def stdout(self, data):
        self.output.append(data)


class CPU(object):
    """ 本类模拟 cardiac CPU. """

    def __init__(self):
        self.init_cpu()
        self.reset()
        try:
            self.init_mem()
        except AttributeError:
            raise NotImplementedError('You need to Mixin a memory-enabled class.')
        try:
            self.init_reader()
            self.init_output()
        except AttributeError:
            raise NotImplementedError('You need to Mixin a IO-enabled class.')

    def reset(self):
        """  用默认值重置 CPU 的寄存器  """
        self.pc = 0  #: 指令指针
        self.ir = 0  #: 指令寄存器
        self.acc = 0  #: 累加器
        self.running = False  #: 仿真器的运行状态?

    def init_cpu(self):
        """  本函数自动在哈希表中创建指令集. 这样我们就可以使用 case/select 方式调用指令, 同时保持代码简洁. 当然, 在 process(） 中使用 getattr 然后用 try/except 捕捉异常也是可以的, 但是代码看起来就没那么简洁了.  """
        self.__opcodes = {}
        classes = [self.__class__]  #: 获取全部类, 包含基类.
        while classes:
            cls = classes.pop()  # 把堆栈中的类弹出来
            if cls.__bases__:  # 判断有没有基类
                classes = classes + list(cls.__bases__)
            for name in dir(cls):  # 遍历名称.
                if name[:7] == 'opcode_':  # 只需要把指令读出来即可
                    try:
                        opcode = int(name[7:])
                    except ValueError:
                        raise NameError('Opcodes must be numeric, invalid opcode: %s' % name[7:])
        self.__opcodes.update({opcode: getattr(self, 'opcode_%s' % opcode)})

    def fetch(self):
        """  根据指令指针(program pointer) 从内存中读取指令, 然后指令指针加 1.  """
        self.ir = self.get_memint(self.pc)
        self.pc += 1

    def process(self):
        """  处理当前指令， 只处理一条. 默认情况下是在循环代码中调用(running loop), 也可以自己写代码, 以单步调试方式调用, 或者利用 time.sleep() 降低执行速度. 在 TK/GTK/Qt/curses 做的界面的线程中调用本函数也是可以的.  """
        self.fetch()
        opcode, data = int(math.floor(self.ir / 100)), self.ir % 100
        self.__opcodes[opcode](data)

    def opcode_0(self, data):
        """ 输入指令 """
        self.mem[data] = self.get_input()

    def opcode_1(self, data):
        """ 清除累加器指令 """
        self.acc = self.get_memint(data)

    def opcode_2(self, data):
        """ 加法指令 """
        self.acc += self.get_memint(data)

    def opcode_3(self, data):
        """ 测试累加器内容指令 """
        if self.acc < 0:
            self.pc = data

    def opcode_4(self, data):
        """ 位移指令 """
        x, y = int(math.floor(data / 10)), int(data % 10)
        for i in range(0, x):
            self.acc = (self.acc * 10) % 10000
        for i in range(0, y):
            self.acc = int(math.floor(self.acc / 10))

    def opcode_5(self, data):
        """ 输出指令 """
        self.stdout(self.mem[data])

    def opcode_6(self, data):
        """ 存储指令 """
        self.mem[data] = self.pad(self.acc)

    def opcode_7(self, data):
        """ 减法指令 """
        self.acc -= self.get_memint(data)

    def opcode_8(self, data):
        """ 无条件跳转指令 """
        self.pc = data

    def opcode_9(self, data):
        """ 停止/复位指令"""
        self.reset()

    def run(self, pc=None):
        """ 这段代码会一直运行， 直到遇到 halt/reset 指令才停止. """
        if pc:
            self.pc = pc
        self.running = True
        while self.running:
            self.process()
        print("Output:\n%s" % self.format_output())
        self.init_output()


class Cardiac(CPU, Memory, IO):
    pass


if __name__ == '__main__':
    c = Cardiac()
    c.read_deck('deck1.txt')
    try:
        c.run()
    except:
        print("IR: %s\nPC: %s\nOutput: %s\n" % (c.ir, c.pc, c.format_output()))
        raise
