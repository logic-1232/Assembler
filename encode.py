from main import df

X0 = "00000"
X1 = "00001"
X2 = "00010"


def encode(cmd: list[str], pc: int, flags: dict) -> str:
    """将汇编指令编码成机器码"""
    cmd_type = df.loc[cmd[0]]["type"]
    if(cmd_type == "R2"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        funct7 = df.loc[cmd[0]]["funct7"]
        rd = cmd[1]
        rs1 = cmd[2]
        rs2 = df.loc[cmd[0]]["rs2"]
        mif = funct7 + rs2 + rs1 + funct3 + rd + opcode
    elif(cmd_type == "R4"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        funct7 = df.loc[cmd[0]]["funct7"]
        rd = cmd[1]
        rs1 = cmd[2]
        rs2 = cmd[3]
        rs3 = cmd[4]
        mif = rs3 + funct7[5:] + rs2 + rs1 + funct3 + rd + opcode
    elif(cmd_type == "R"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        funct7 = df.loc[cmd[0]]["funct7"]
        rd = cmd[1]
        rs1 = cmd[2]
        rs2 = cmd[3]
        mif = funct7 + rs2 + rs1 + funct3 + rd + opcode
    elif(cmd_type == "I"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        rd = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(imm < 0):
            imm += 2**12
        imm = "{:0>12}".format(bin(imm)[2:])
        mif = imm + rs1 + funct3 + rd + opcode
    elif(cmd_type == "IR"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        funct7 = df.loc[cmd[0]]["funct7"]
        rd = cmd[1]
        rs1 = cmd[2]
        imm = "{:0>5}".format(bin(eval(cmd[3]))[2:])
        mif = funct7 + imm + rs1 + funct3 + rd + opcode
    elif(cmd_type == "S"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        rs2 = cmd[1]
        rs1 = cmd[2]
        imm = eval(cmd[3])
        if(imm < 0):
            imm += 2**12
        imm = "{:0>12}".format(bin(imm)[2:])
        mif = imm[0:7] + rs2 + rs1 + funct3 + imm[7:] + opcode
    elif(cmd_type == "B"):
        opcode = df.loc[cmd[0]]["opcode"]
        funct3 = df.loc[cmd[0]]["funct3"]
        rs1 = cmd[1]
        rs2 = cmd[2]
        imm = (flags[cmd[3]]-pc)//2  # 偏移值
        if(imm < 0):  # 补码
            imm += 2**12
        imm = "{:0>12}".format(bin(imm)[2:])
        mif = imm[0] + imm[2:8] + rs2 + rs1 + funct3 + imm[8:12] + imm[1] + opcode
    elif(cmd_type == "U"):
        opcode = df.loc[cmd[0]]["opcode"]
        rd = cmd[1]
        imm = eval(cmd[2])
        if(imm < 0):
            imm += 2**20
        imm = "{:0>20}".format(bin(imm)[2:])
        mif = imm + rd + opcode
    elif(cmd_type == "J"):  # 只有`jal`指令
        opcode = df.loc[cmd[0]]["opcode"]
        rd = cmd[1]
        imm = (flags[cmd[2]]-pc)//2  # 偏移值
        if(imm < 0):  # 补码
            imm += 2**20
        imm = "{:0>20}".format(bin(imm)[2:])
        mif = imm[0] + imm[10:] + imm[9] + imm[1:9] + rd + opcode
    elif(cmd_type == "C"):
        mif = encode_c(cmd, pc, flags)
    # print(mif)  # 打印机器码（调试用）
    return mif


def encode_c(cmd: list, pc: int, flags: dict) -> str:
    """对压缩指令进行编码"""
    opcode = df.loc[cmd[0]]["opcode"]
    funct3 = df.loc[cmd[0]]["funct3"]
    funct7 = df.loc[cmd[0]]["funct7"]
    if(opcode == "00"):
        uimm = eval(cmd[-1])
        uimm = "{:0>12}".format(bin(uimm)[2:])
        if(funct3 == "000"):  # c.addi4spn
            rd = cmd[1]
            mif = funct3 + uimm[6:8] + uimm[2:6] + uimm[9] + uimm[8] + rd[2:] + opcode
        else:  # c.lw和c.sw
            rd = cmd[1]
            rs1 = cmd[2]
            mif = funct3 + uimm[6:9] + rs1[2:] + uimm[9] + uimm[5] + rd[2:] + opcode
    elif(opcode == "01"):
        if(funct3 == "000" or funct3 == "010"):  # c.addi和c.li
            imm = eval(cmd[-1])
            if(imm < 0):
                imm += 2**12
            imm = "{:0>12}".format(bin(imm)[2:])
            rd = cmd[1]
            mif = funct3 + imm[6] + rd + imm[7:] + opcode
        elif(funct3 == "101" or funct3 == "001"):  # c.j和c.jal
            imm = flags[cmd[-1]]-pc  # 偏移值
            if(imm < 0):
                imm += 2**12
            imm = "{:0>12}".format(bin(imm)[2:])
            mif = funct3 + imm[0] + imm[7] + imm[2:4] + imm[1] + imm[5] + imm[4] + imm[8:11] + imm[6] + opcode
        elif(funct3 == "110" or funct3 == "111"):  # c.beqz和c.bnez
            imm = flags[cmd[-1]]-pc  # 偏移值
            if(imm < 0):
                imm += 2**12
            imm = "{:0>12}".format(bin(imm)[2:])
            rs1 = cmd[1]
            mif = funct3 + imm[3] + imm[7:9] + rs1[2:] + imm[4:6] + imm[9:11] + imm[6] + opcode
        elif(funct3 == "011"):
            imm = eval(cmd[-1])
            if(imm < 0):
                imm += 2**12
            imm = "{:0>12}".format(bin(imm)[2:])
            if(len(cmd) == 2):  # c.addi16sp
                mif = funct3 + imm[2] + X2 + imm[7] + imm[5] + imm[3:5] + imm[6] + opcode
            else:  # c.lui
                rd = cmd[1]
                mif = funct3 + imm[6] + rd + imm[7:] + opcode
        else:
            if(funct7 == "11"):  # c.and、c.or、c.xor、c.sub
                rd = cmd[1]
                rs2 = cmd[2]
                mif = "100011" + rd[2:] + df.loc[cmd[0]]["rs2"] + rs2[2:] + "01"
            else:  # c.andi、c.srai、c.srli
                imm = eval(cmd[-1])
                if(imm < 0):
                    imm += 2**12
                imm = "{:0>12}".format(bin(imm)[2:])
                rd = cmd[1]
                mif = funct3 + imm[6] + funct7 + rd[2:] + imm[7:] + opcode
    elif(opcode == "10"):
        if(funct3 == "000"):  # c.slli
            uimm = eval(cmd[-1])
            uimm = "{:0>12}".format(bin(uimm)[2:])
            rd = cmd[1]
            mif = funct3 + uimm[6] + rd + uimm[7:] + opcode
        elif(funct3 == "010"):  # c.lwsp
            uimm = eval(cmd[-1])
            uimm = "{:0>12}".format(bin(uimm)[2:])
            rd = cmd[1]
            mif = funct3 + uimm[6] + rd + uimm[7:10] + uimm[4:6] + opcode
        elif(funct3 == "110"):  # c.swsp
            uimm = eval(cmd[-1])
            uimm = "{:0>12}".format(bin(uimm)[2:])
            rs2 = cmd[1]
            mif = funct3 + uimm[6:10] + uimm[4:6] + rs2 + opcode
        elif(funct3 == "100"):
            if(len(cmd) == 2):  # c,jalr和c.jr
                rs1 = cmd[1]
                mif = funct3 + funct7 + rs1 + X0 + opcode
            else:  # c.add和c.mv
                rd = cmd[1]
                rs2 = cmd[2]
                mif = funct3 + funct7 + rd + rs2 + opcode
    return mif
