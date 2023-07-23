import pandas as pd
from compress import compress
from encode import encode
from main import df

reg_code_df = pd.read_excel("./assembler/reg_code.xlsx", index_col=0, dtype=str)
flags = dict()  # 记录汇编代码中的跳转标记位置


def decode_reg(reg: str) -> str:
    if(reg[0]=="x"):
        code = "{:0>5}".format(bin(eval(reg[1:]))[2:])
    elif(reg[0]=="f" and reg[1:].isdigit()):
        code = "{:0>5}".format(bin(eval(reg[1:]))[2:])
    else:
        code = "{:0>5}".format(bin(eval(reg_code_df.loc[reg]["code"]))[2:])
    return code


def fp32(num: float):
    tmp = bin(int(abs(num) * (1 << 127)))[2:]
    sign = '1' if(num < 0) else '0'
    exp = "{:0>8}".format(bin(len(tmp) - 1)[2:])
    f = tmp[1:24]
    rslt = eval("0b" + sign + exp + f)
    return rslt


def transform(asm: str) -> list[list]:
    """将伪指令扩展成可以编码的指令，并将字符串形式的汇编代码中的有效信息拆分成列表"""
    l = asm.split(' ')
    while('' in l):
        l.remove('')
    cmd_type = df.loc[l[0]]["type"]
    if(cmd_type == "P"):  # 伪指令
        if(len(l) == 4):
            cmd = df.loc[l[0]]["cmd"].format(l[1], l[2], l[3])
        elif(len(l) == 3):
            cmd = df.loc[l[0]]["cmd"].format(l[1], l[2])
        elif(len(l) == 2):
            cmd = df.loc[l[0]]["cmd"].format(l[1])
        elif(len(l) == 1):
            cmd = df.loc[l[0]]["cmd"]
        cmd_list = transform(cmd)
    elif(cmd_type == "X"):  # 伪指令（需扩展为多条指令）
        cmd_list = list()
        if(l[0] == "li"):  # 这里的处理可能不规范
            rd = decode_reg(l[1])
            imm = eval(l[2])
            if(type(imm) != int):
                imm = fp32(imm)
            tmp = (imm % 4096) >> 11
            imm_1 = (imm >> 12)+tmp
            imm_2 = imm % 4096
            if(imm_1!=0):
                cmd_list.append(["lui", rd, str(imm_1)])
            cmd_list.append(["addi", rd, rd, str(imm_2)])
    else:
        cmd_type = df.loc[l[0]]["type"]
        if(cmd_type in ["R"]):
            rd = decode_reg(l[1])
            rs1 = decode_reg(l[2])
            rs2 = decode_reg(l[3])
            cmd_list = [[l[0], rd, rs1, rs2]]
        elif(cmd_type in ["I", "IR", "S", "B"]):
            rd = decode_reg(l[1])
            rs1 = decode_reg(l[2])
            cmd_list = [[l[0], rd, rs1, l[3]]]
        elif(cmd_type in ["U", "J"]):
            rd = decode_reg(l[1])
            cmd_list = [[l[0], rd, l[2]]]
        elif(cmd_type in ["R2"]):
            rd = decode_reg(l[1])
            rs1 = decode_reg(l[2])
            cmd_list = [[l[0], rd, rs1]]
        elif(cmd_type in ["R4"]):
            rd = decode_reg(l[1])
            rs1 = decode_reg(l[2])
            rs2 = decode_reg(l[3])
            rs3 = decode_reg(l[4])
            cmd_list = [[l[0], rd, rs1, rs2, rs3]]
        else:
            cmd_list = [l]
    return cmd_list


def first_ergodic(asm_list: list[str], flag: bool) -> list[list[str]]:
    """一次遍历：将汇编代码转为便于编码的标准格式，同时记录跳转标记"""
    i = 0
    n = len(asm_list)
    cmd = list()
    cnt_c = 0
    while(i < n):
        asm = asm_list[i].split("#")[0].lower()  # 过滤注释，并转为小写字母（大小写不敏感）
        if(asm == ""):
            asm_list.pop(i)
            n = n - 1
        elif(asm[-1] == ":"):
            flags.update({asm[:-1]: 4*len(cmd)-2*cnt_c})
            asm_list.pop(i)
            n = n - 1
        else:
            tmp = transform(asm)
            if(flag):
                for t in tmp:
                    c = compress(t)
                    cmd.append(c)
                    if(c[0][0:2] == "c."):
                        cnt_c = cnt_c + 1
            else:
                cmd.extend(tmp)  # 为了适应部分转译成两句的指令
            i = i + 1
    print(flags)
    return cmd


def second_ergodic(cmd_list: list[list[str]]) -> str:
    data = ""
    pc = 0
    for cmd in cmd_list:  # 二次遍历：编译汇编指令
        mif = encode(cmd, pc, flags)
        data += mif + "\n"
        pc += len(mif)//8
    return data


def compiler(asm_list: list[str], flag: bool) -> bytes:
    """编译"""
    flags.clear()
    cmd_list = first_ergodic(asm_list, flag)
    data = second_ergodic(cmd_list)
    return data
