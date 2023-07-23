import compiler
import pandas as pd

def reorder(filepath: str):
    with open(filepath, "r") as f:
        mif = f.read().split("\n")
    txt = ""
    for i in mif:
        if(len(i)==32):
            txt = txt + i[16:] + i[0:16]
        else:
            txt = txt + i
    num = len(txt)//16
    if(num%2==1):
        txt = txt+"0000000001111111"
    with open("./assembler/code.txt", "w") as f:
        f.write("")
    with open("./assembler/code.txt", "a") as f:
        for i in range((num+1)//2):
            f.write(txt[32*i+16:32*i+32]+txt[32*i+0:32*i+16]+"\n")


NOP  = "00000000000000000000000000010011\n"
STOP = "00000000011111110000000001111111"


"""这里的操作会产生circular import，但为了方便，还是选择这么用"""
cmd_set = "RV32IC"
df_list = list()
for i in cmd_set[4:]:
    df_list.append(pd.read_excel("./assembler/command.xlsx", sheet_name="RV32"+i, index_col=0, dtype=str))
df = pd.concat(df_list, axis=0)
# df = pd.read_excel("./assembler/command.xlsx", index_col=0, dtype=str)

if __name__ == "__main__":
    filepath = "./assembler/demo.asm"
    with open(filepath, "r", encoding="utf-8") as f:  # 获取汇编代码
        asm_list = f.read().split("\n")
    flag = "C" in cmd_set
    print(flag)
    data = compiler.compiler(asm_list, flag)
    txt = data + NOP + STOP
    with open("./assembler/code.bit", "w") as f:
        f.write(txt)
    reorder("./assembler/code.bit")
