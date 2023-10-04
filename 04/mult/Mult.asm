// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
@R2 // Reset R2 Value
M=0

//inc = R0
@R0
D=M
@inc
M=D

//i=R1
@R1
D=M
@i
M=D

//if (inc>=i) goto LOOP
    @inc
    D=M-D
    @PRE_LOOP
    D;JGE

// else flip values
    @i
    D=M
    @temp
    M=D //temp = i

    @inc
    D=M
    @i
    M=D //i = inc

    @temp
    D=M
    @inc
    M=D //inc = temp

(PRE_LOOP) //Skips the loop if the lowest value is zero
@i
D=M
@END
D;JLE
(LOOP)
    @inc
    D=M
    @R2
    M=M+D
    @i // Decrement the iterator
    M=M-1
    D=M
    @LOOP // Loops stops when 'i' is 0
    D;JGT

(END)
    @END
    0;JMP