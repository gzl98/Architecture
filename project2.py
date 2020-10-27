accuracy = 5  # 小数部分精度


# 十进制直接转二进制
def dtb(num):
    # 判断是否为浮点数
    if num == int(num):
        # 若为整数
        integer = str(bin(num))
        integer = integer[2:]
        return integer
    else:
        # 若为浮点数
        # 取整数部分
        integer = int(num)
        # 取小数部分
        flo = num - integer
        # 整数部分进制转换
        integercom = str(bin(integer))
        integercom = integercom[2:]
        # 小数部分进制转换
        tem = flo
        tmpflo = []
        for i in range(accuracy):
            tem *= 2
            tmpflo += str(int(tem))
            tem -= int(tem)
        flocom = tmpflo
        return integercom + '.' + ''.join(flocom)


# int转32位float
def int2float(num):
    # 判断是否为浮点数
    if num == int(num):
        return
    # 判断正负
    f = '0'
    if num < 0:
        f = '1'
    # 若为浮点数
    # 取整数部分
    integer = int(num)
    # 取小数部分
    flo = num - integer
    # 整数部分进制转换
    integercom = str(bin(integer))
    integercom = integercom[2:]
    # 小数部分进制转换
    tem = flo
    tmpflo = []
    for i in range(accuracy):
        tem *= 2
        tmpflo += str(int(tem))
        tem -= int(tem)
    flocom = tmpflo
    flocom = ''.join(flocom)
    # 取指数
    data = ''
    if len(integercom) > 1:
        ex = bin(127 + len(integercom) - 1)[2:]
        ex = '0' * (8 - len(ex)) + ex
        data = f + ex + integercom[1:] + flocom
    elif integercom == '1':
        ex = bin(127 + 0)[2:]
        ex = '0' * (8 - len(ex)) + ex
        data = f + ex + flocom
    else:
        # 负指数
        ex = 0
        for i in flocom:
            if i == '1':
                pass
            else:
                ex -= 1
        flocom = flocom[-ex:]
        ex = bin(127 + ex)[2:]
        ex = '0' * (8 - len(ex)) + ex
        data = f + ex + flocom
    data += '0' * (32 - len(data))
    return int(data, 2)


print(dtb(176.0625))
int2float(176.0625)
