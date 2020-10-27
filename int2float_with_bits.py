# int转32位float
def int2float(num, bits=32, accuracy=6):
    # 判断是否为浮点数
    if num == int(num):
        return
    if bits == 32:
        ex_num = 127
        ex_bits = 8
    else:
        ex_num = 1023
        ex_bits = 11
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
    if len(integercom) > 1:
        ex = bin(ex_num + len(integercom) - 1)[2:]
        ex = '0' * (ex_bits - len(ex)) + ex
        data = f + ex + integercom[1:] + flocom
    elif integercom == '1':
        ex = bin(ex_num)[2:]
        ex = '0' * (ex_bits - len(ex)) + ex
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
        ex = bin(ex_num + ex)[2:]
        ex = '0' * (ex_bits - len(ex)) + ex
        data = f + ex + flocom
    if len(data) > bits:
        data = data[:bits]
    else:
        data += '0' * (bits - len(data))
    # return data
    return int(data, 2)
