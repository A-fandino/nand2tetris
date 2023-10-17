// push constant 17
@17
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 17
@17
D=A
@SP
M=M+1
A=M-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
AM=M-1
D=D-M
@END_IF_134
D;JEQ
D=-1
(END_IF_134)
@SP
A=M
M=!D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 16
@16
D=A
@SP
M=M+1
A=M-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
AM=M-1
D=D-M
@END_IF_327
D;JEQ
D=-1
(END_IF_327)
@SP
A=M
M=!D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 17
@17
D=A
@SP
M=M+1
A=M-1
M=D
// eq
@SP
AM=M-1
D=M
@SP
AM=M-1
D=D-M
@END_IF_520
D;JEQ
D=-1
(END_IF_520)
@SP
A=M
M=!D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 891
@891
D=A
@SP
M=M+1
A=M-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_685
D;JLT
D=0
@END_IF_685
0;JMP
(IF_TRUE_685)
D=-1
(END_IF_685)
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 892
@892
D=A
@SP
M=M+1
A=M-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_918
D;JLT
D=0
@END_IF_918
0;JMP
(IF_TRUE_918)
D=-1
(END_IF_918)
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 891
@891
D=A
@SP
M=M+1
A=M-1
M=D
// lt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_1151
D;JLT
D=0
@END_IF_1151
0;JMP
(IF_TRUE_1151)
D=-1
(END_IF_1151)
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 32766
@32766
D=A
@SP
M=M+1
A=M-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_1396
D;JGT
D=0
@END_IF_1396
0;JMP
(IF_TRUE_1396)
D=-1
(END_IF_1396)
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 32767
@32767
D=A
@SP
M=M+1
A=M-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_1641
D;JGT
D=0
@END_IF_1641
0;JMP
(IF_TRUE_1641)
D=-1
(END_IF_1641)
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 32766
@32766
D=A
@SP
M=M+1
A=M-1
M=D
// gt
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@IF_TRUE_1886
D;JGT
D=0
@END_IF_1886
0;JMP
(IF_TRUE_1886)
D=-1
(END_IF_1886)
@SP
A=M
M=D
@SP
M=M+1
// push constant 57
@57
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 31
@31
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 53
@53
D=A
@SP
M=M+1
A=M-1
M=D
// add
@SP
AM=M-1
D=M
@SP
AM=M-1
M=D+M
@SP
M=M+1
// push constant 112
@112
D=A
@SP
M=M+1
A=M-1
M=D
// sub
@SP
AM=M-1
D=M
@SP
AM=M-1
M=M-D
@SP
M=M+1
// neg
@SP
AM=M-1
M=-M
@SP
M=M+1
// and
@SP
AM=M-1
D=M
@SP
AM=M-1
M=D&M
@SP
M=M+1
// push constant 82
@82
D=A
@SP
M=M+1
A=M-1
M=D
// or
@SP
AM=M-1
D=M
@SP
AM=M-1
M=D|M
@SP
M=M+1
// not
@SP
AM=M-1
D=M
M=!D
@SP
M=M+1
