"""
关于分支跳转指令能否压缩的判断：
处寄存器限制以外，决定能否压缩的一个关键因素是offset的位宽会不会溢出。
- 对jalr和jr来说，压缩指令本身就限制了offset==0，因此可以压缩；
- 对branch指令以及j和jal来说，offset的值是不确定的，与目标指令的位置有关，下面分两类讨论：
    1. 目标指令在该指令前，那么可以直接得到offset的值，进而确定是否压缩；
    2. 目标指令在该指令后，这两条指令间的压缩指令个数会影响offset值，一次遍历无法确定

一个草率的解决方案：
因为编写的程序都比较短，offset基本上不会溢出，所以可以都判断为压缩
"""

X0 = "00000"
X1 = "00001"
X2 = "00010"


self_op_list = ["sub", "xor", "or", "and"]


def compress(cmd: list[str]) -> list[str]:
    """判断能否压缩指令"""
    cmd_c = cmd
    if(cmd[0] == "add"):
        rd = cmd[1]
        rs1 = cmd[2]
        rs2 = cmd[3]
        if(rd != X0 and rd == rs1 and rs2 != X0):  # c.add
            cmd_c = ["c.add", cmd[1], cmd[3]]
        elif(rd != X0 and rd == rs2 and rs1 != X0):
            cmd_c = ["c.add", cmd[1], cmd[2]]
        elif(rs1 == X0 and rs2 != X0):  # c.mv
            cmd_c = ["c.mv", cmd[1], cmd[3]]
        elif(rs1 != X0 and rs2 == X0):
            cmd_c = ["c.mv", cmd[1], cmd[2]]
    elif(cmd[0] == "addi"):
        rd = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rd == rs1):
            if(rd == X2 and imm != 0 and imm % 16 == 0 and -512 <= imm <= 511):  # c.addi16sp
                cmd_c = ["c.addi16sp", cmd[1], cmd[2]]
            elif(-32 <= imm <= 31):  # c.addi
                cmd_c = ["c.addi", cmd[1], cmd[3]]
        elif(rs1 == X2 and imm % 4 == 0 and 0 < imm <= 1023 and rd[0:2] == "01"):  # c.addi4spn
            cmd_c = ["c.addi4spn", cmd[1], cmd[3]]
        elif(rs1 == X0 and -32 <= imm <= 31):  # c.li
            cmd_c = ["c.li", cmd[1], cmd[3]]
    elif(cmd[0] in ["beq", "bne"]):
        rs1 = cmd[1]
        rs2 = cmd[2]
        if(rs2 == X0 and rs1[0:2] == "01"):
            cmd_c = ["c."+cmd[0]+"z", cmd[1], cmd[3]]
        elif(rs1 == X0 and rs2[0:2] == "01"):
            cmd_c = ["c."+cmd[0]+"z", cmd[2], cmd[3]]
    elif(cmd[0] == "jal"):
        rs1 = cmd[1]
        if(rs1 == X0):
            cmd_c = ["c.j", cmd[2]]
        elif(rs1 == X1):
            cmd_c = ["c.jal", cmd[2]]
    elif(cmd[0] == "jalr"):
        rs2 = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rs2 == X1 and imm == 0 and rs1 != X0):  # c.jalr
            cmd_c = ["c.jalr", cmd[2]]
        elif(rs2 == X0 and imm == 0 and rs1 != X0):  # c.jr
            cmd_c = ["c.jr", cmd[2]]
    elif(cmd[0] == "lui"):
        rd = cmd[1]
        imm = eval(cmd[2])
        if(rd == X2 and imm != 0 and -32 <= imm <= 31):  # c.lui
            cmd_c = ["c.lui", cmd[1], cmd[2]]
    elif(cmd[0] == "lw"):
        rd = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rd != X0 and rs1 == X2 and imm % 4 == 0 and 0 <= imm <= 255):  # c.lwsp
            cmd_c = ["c.lwsp", cmd[1], cmd[3]]
        elif(imm % 4 == 0 and 0 <= imm <= 127 and rd[0:2] == "01" and rs1[0:2] == "01"):  # c.lw
            cmd_c = ["c.lw", cmd[1], cmd[2], cmd[3]]
    elif(cmd[0] == "sw"):
        rs2 = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rs1 == X2 and 0 <= imm <= 255 and imm % 4 == 0):  # c.swsp
            cmd_c = ["c.swsp", cmd[1], cmd[3]]
        elif(0 <= imm <= 127 and rs2[0:2] == "01" and rs1[0:2] == "01"):  # c.sw
            cmd_c = ["c.sw", cmd[1], cmd[2], cmd[3]]
    elif(cmd[0] == "slli"):
        rd = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rd == rs1):  # c.slli
            cmd_c = ["c.slli", cmd[1], cmd[3]]
    elif(cmd[0] in ["andi", "srai", "srli"]):
        rd = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(rd == rs1 and rd[0:2] == "01"):
            if(cmd[0] == "andi" and -32 <= imm <= 31):
                cmd_c = ["c.andi", cmd[1], cmd[3]]
            else:
                cmd_c = ["c."+cmd[0], cmd[1], cmd[3]]
    elif(cmd[0] in self_op_list):
        rd = cmd[1]
        rs1 = cmd[2]
        rs2 = cmd[3]
        if(rd == rs1 and rs1[0:2] == "01" and rs2[0:2] == "01"):
            cmd_c = ["c."+cmd[0], cmd[1], cmd[3]]
    return cmd_c

