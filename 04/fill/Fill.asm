// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)
    @KBD
    D=M
    @fill
    M=-1
    @START_PAINT
    D;JNE
    @fill
    M=0
    @START_PAINT
    0;JMP

(START_PAINT)
    @fill
    D=M
    @SCREEN
    D=M-D
    @LOOP
    D;JEQ
    @SCREEN
    D=M
    @8192
    D=A
    @i
    M=D
    @FILL_SCREEN
    0;JMP


(FILL_SCREEN)
    @SCREEN
    D=A
    @i
    D=D+M
    @pointer
    M=D
    @fill
    D=M
    @pointer
    A=M
    M=D
    @i
    M=M-1
    D=M
    @FILL_SCREEN
    D;JGE
    @LOOP
    0;JMP