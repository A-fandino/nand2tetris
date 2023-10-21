# Symbols
COMMENT_SYMBOL = "//"

# Instruction commands
PUSH = "push"
POP = "pop"

GOTO = "goto"
IF_GOTO = "if-goto"
FUNCTION = "function"
CALL = "call"
RETURN = "return"
LABEL = "label"

FLOW_CONTROL_COMMANDS = [GOTO, IF_GOTO, FUNCTION, CALL, RETURN, LABEL]

# Arithmetic/Logic commands
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"
ARITHMETIC_COMMANDS = [ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT]

# Memory segments
SP = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4

TEMP_START = 5
TEMP_LENGTH = 7

STATIC_START = 16
STATIC_LENGTH = 255 - STATIC_START

LCL_LENGTH, ARG_LENGTH, THIS_LENGTH, THAT_LENGTH = 1000, 1000, 1000, 1000
