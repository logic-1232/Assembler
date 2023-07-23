# 寻找最大值

begin:
    j       load

func:
    bge     t1  t2  endfunc
    mv      t1  t2
endfunc:
    jr      ra 

load:
    li      a0  56
    li      a1  717
    li      a2  95
    li      a3  5057
main:
    mv      t1  a0 
    mv      t2  a1 
    jal     ra  func
    mv      t2  a2 
    jal     ra  func
    mv      t2  a3 
    jal     ra  func
output:
    mv      s0  t1
