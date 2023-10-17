// Setup
@256
D=A
@SP
M=D
@1000
D=A
@LCL
M=D
@2000
D=A
@THIS
M=D
@3000
D=A
@THAT
M=D
// push constant 7
@7
D=A
@SP
M=M+1
A=M-1
M=D
// push constant 8
@8
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
