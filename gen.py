from enum import Enum
import json
import os
from typing import List, Type


if not os.path.exists("out"):
    os.mkdir("out")


class OpType(Enum):
    # load/store
    MOVEMENT = (0,)
    # add / sub / shift / etc
    ARITHMATIC = (1,)
    # compare logical stuff
    LOGICAL = (2,)
    # stack ops
    STACK = (3,)
    # jump/branch
    BRANCH = (5,)
    # set/clear flags
    FLAG = (6,)


class Flag(Enum):
    CARRY = (0,)
    ZERO = (1,)
    INTERRUPT_DISABLE = (2,)
    DECIMAL_MODE = (3,)
    OVERFLOW = (6,)
    NEGATIVE = 7


class AddressingMode(Enum):
    IMPLIED = (0,)
    IMMEDIATE = (1,)
    ZERO_PAGE = (2,)
    ZERO_PAGE_X = (3,)
    ZERO_PAGE_Y = (4,)
    RELATIVE = (5,)
    ABSOLUTE = (6,)
    ABSOLUTE_X = (7,)
    ABSOLUTE_Y = (8,)
    INDIRECT = (9,)
    INDIRECT_X = (10,)
    INDIRECT_Y = (11,)


class OpCode:
    def __init__(
        self,
        opcode: int,
        cycles: int,
        length: int,
        addr_mode: Type[AddressingMode],
        page_cross_incr=0,
    ):
        self.opcode = opcode
        self.cycles = cycles
        self.page_cross_incr = page_cross_incr
        self.length = length
        self.addr_mode = addr_mode

    def get_dict(self):
        ret_dict = self.__dict__.copy()
        ret_dict["addr_mode"] = self.addr_mode.name
        return ret_dict


class Op:
    def __init__(
        self,
        name: str,
        long_name: str,
        op_type,
        flags: List[Flag],
        operands: List[OpCode] = None,
    ):
        self.name = name
        self.long_name = long_name
        self.type = op_type
        self.flags = flags
        self.operands = operands if operands is not None else []

    def add_operand(self, operand: OpCode):
        self.operands.append(operand)

    def get_dict(self):
        basedict = self.__dict__.copy()
        basedict.pop("operands")
        basedict["operands"] = [o.get_dict() for o in self.operands]
        basedict["type"] = self.type.name.lower()
        basedict["flags"] = [f.name.lower() for f in self.flags]
        return basedict


with open("out/6502.json", "w", encoding="utf-8") as f:
    ops = []
    op = Op(
        "ADC",
        "ADd with Carry",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.OVERFLOW, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0x69, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0x65, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x75, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x6D, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x7D, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0x79, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0x61, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0x71, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    op = Op(
        "AND",
        "bitwise AND with accumulator",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.ZERO],
    )
    op.add_operand(OpCode(0x29, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0x25, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x35, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x2D, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x3D, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0x39, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0x21, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0x31, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    op = Op(
        "ASL",
        "Arithmatic Shift Left",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0x0A, 2, 1, AddressingMode.IMPLIED))
    op.add_operand(OpCode(0x06, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x16, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x0E, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x1E, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    op = Op(
        "BIT", "test BITs", OpType.LOGICAL, [Flag.NEGATIVE, Flag.OVERFLOW, Flag.ZERO]
    )
    op.add_operand(OpCode(0x24, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x2C, 4, 3, AddressingMode.ABSOLUTE))
    ops.append(op)

    ops.append(
        Op(
            "BPL",
            "Branch on PLus",
            OpType.BRANCH,
            [],
            [OpCode(0x10, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BMI",
            "Branch on MInus",
            OpType.BRANCH,
            [],
            [OpCode(0x30, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BVC",
            "Branch on oVerflow Clear",
            OpType.BRANCH,
            [],
            [OpCode(0x50, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BVS",
            "Branch on oVerflow Set",
            OpType.BRANCH,
            [],
            [OpCode(0x70, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BCC",
            "Branch on Carry Clear",
            OpType.BRANCH,
            [],
            [OpCode(0x90, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BCS",
            "Branch on Carry Set",
            OpType.BRANCH,
            [],
            [OpCode(0xB0, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BNE",
            "Branch on Not Equal",
            OpType.BRANCH,
            [],
            [OpCode(0xD0, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )
    ops.append(
        Op(
            "BEQ",
            "Branch on EQual",
            OpType.BRANCH,
            [],
            [OpCode(0xF0, 2, 2, AddressingMode.IMPLIED, 1)],
        )
    )

    ops.append(
        Op(
            "BRK",
            "BReaK",
            OpType.BRANCH,
            [Flag.INTERRUPT_DISABLE],
            [OpCode(0x00, 7, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op(
        "CMP",
        "CoMPare accumulator",
        OpType.LOGICAL,
        [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0xC9, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xC5, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xD5, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xCD, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xDD, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0xD9, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0xC1, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0xD1, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    op = Op(
        "CPX",
        "ComPare X register",
        OpType.LOGICAL,
        [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0xE0, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xE4, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xEC, 4, 3, AddressingMode.ABSOLUTE))
    ops.append(op)

    op = Op(
        "CPY",
        "ComPare Y register",
        OpType.LOGICAL,
        [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0xC0, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xC4, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xCC, 4, 3, AddressingMode.ABSOLUTE))
    ops.append(op)

    op = Op("DEC", "DECrement memory", OpType.ARITHMATIC, [Flag.NEGATIVE, Flag.ZERO])
    op.add_operand(OpCode(0xC6, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xD6, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xCE, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xDE, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    op = Op(
        "EOR", "bitwise Exclusive OR", OpType.ARITHMATIC, [Flag.NEGATIVE, Flag.ZERO]
    )
    op.add_operand(OpCode(0x49, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0x45, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x55, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x4D, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x5D, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0x59, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0x41, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0x51, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    ops.append(
        Op(
            "CLC",
            "CLear Carry",
            OpType.FLAG,
            [Flag.CARRY],
            [OpCode(0x18, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "SEC",
            "SEt Carry",
            OpType.FLAG,
            [Flag.CARRY],
            [OpCode(0x38, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "CLI",
            "CLear Interrupt",
            OpType.FLAG,
            [Flag.INTERRUPT_DISABLE],
            [OpCode(0x58, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "SEI",
            "SEt Interrupt",
            OpType.FLAG,
            [Flag.INTERRUPT_DISABLE],
            [OpCode(0x78, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "CLV",
            "CLear oVerflow",
            OpType.FLAG,
            [Flag.OVERFLOW],
            [OpCode(0xB8, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "CLD",
            "CLear Decimal",
            OpType.FLAG,
            [Flag.DECIMAL_MODE],
            [OpCode(0xD8, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "SED",
            "SEt Decimal",
            OpType.FLAG,
            [Flag.DECIMAL_MODE],
            [OpCode(0xF8, 2, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op("INC", "INCrement memory", OpType.ARITHMATIC, [Flag.NEGATIVE, Flag.ZERO])
    op.add_operand(OpCode(0xE6, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xF6, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xEE, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xFE, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    ops.append(
        Op(
            "JMP",
            "JuMP",
            OpType.BRANCH,
            [],
            [
                OpCode(0x4C, 3, 3, AddressingMode.ABSOLUTE),
                OpCode(0x6C, 5, 3, AddressingMode.INDIRECT),
            ],
        )
    )
    ops.append(
        Op(
            "JSR",
            "Jump to SubRoutine",
            OpType.BRANCH,
            [],
            [OpCode(0x20, 6, 3, AddressingMode.ABSOLUTE)],
        )
    )

    op = Op("LDA", "LoaD Accumulator", OpType.MOVEMENT, [Flag.NEGATIVE, Flag.ZERO])
    op.add_operand(OpCode(0xA9, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xA5, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xB5, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xAD, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xBD, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0xB9, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0xA1, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0xB1, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    op = Op("LDX", "LoaD X register", OpType.MOVEMENT, [Flag.NEGATIVE, Flag.ZERO])
    op.add_operand(OpCode(0xA2, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xA6, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xB6, 4, 2, AddressingMode.ZERO_PAGE_Y))
    op.add_operand(OpCode(0xAE, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xBE, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    ops.append(op)

    op = Op("LDY", "LoaD Y register", OpType.MOVEMENT, [Flag.NEGATIVE, Flag.ZERO])
    op.add_operand(OpCode(0xA0, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xA4, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xB4, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xAC, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xBC, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    ops.append(op)

    op = Op(
        "LSR",
        "Logical Shift Right",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0x4A, 2, 1, AddressingMode.IMPLIED))
    op.add_operand(OpCode(0x46, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x56, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x4E, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x5E, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    ops.append(
        Op(
            "NOP",
            "No OPeration",
            OpType.MOVEMENT,
            [],
            [OpCode(0xEA, 2, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op(
        "ORA",
        "bitwise OR with Accumulator",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.ZERO],
    )
    op.add_operand(OpCode(0x09, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0x05, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x15, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x0D, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x1D, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0x19, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0x01, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0x11, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    ops.append(
        Op(
            "TAX",
            "Transfer Accumulator to X",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xAA, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "TXA",
            "Transfer X to Accumulator",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0x8A, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "DEX",
            "DEcrement X",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xCA, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "INX",
            "INcrement X",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xE8, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "TAY",
            "Transfer Accumulator to Y",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xA8, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "TYA",
            "Transfer Y to Accumulator",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0x98, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "DEY",
            "DEcrement Y",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0x88, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "INY",
            "INcrement Y",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xC8, 2, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op(
        "ROL", "ROtate Left", OpType.ARITHMATIC, [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY]
    )
    op.add_operand(OpCode(0x2A, 2, 1, AddressingMode.IMPLIED))
    op.add_operand(OpCode(0x26, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x36, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x2E, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x3E, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    op = Op(
        "ROR", "ROtate Right", OpType.ARITHMATIC, [Flag.NEGATIVE, Flag.ZERO, Flag.CARRY]
    )
    op.add_operand(OpCode(0x6A, 2, 1, AddressingMode.IMPLIED))
    op.add_operand(OpCode(0x66, 5, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x76, 6, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x6E, 6, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x7E, 7, 3, AddressingMode.ABSOLUTE_X))
    ops.append(op)

    ops.append(
        Op(
            "RTI",
            "ReTurn from Interrupt",
            OpType.BRANCH,
            [Flag.INTERRUPT_DISABLE],
            [OpCode(0x40, 6, 1, AddressingMode.IMPLIED)],
        )
    )

    ops.append(
        Op(
            "RTS",
            "ReTurn from Subroutine",
            OpType.BRANCH,
            [],
            [OpCode(0x60, 6, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op(
        "SBC",
        "SuBtract with Carry",
        OpType.ARITHMATIC,
        [Flag.NEGATIVE, Flag.OVERFLOW, Flag.ZERO, Flag.CARRY],
    )
    op.add_operand(OpCode(0xE9, 2, 2, AddressingMode.IMMEDIATE))
    op.add_operand(OpCode(0xE5, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0xF5, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0xED, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0xFD, 4, 3, AddressingMode.ABSOLUTE_X, 1))
    op.add_operand(OpCode(0xF9, 4, 3, AddressingMode.ABSOLUTE_Y, 1))
    op.add_operand(OpCode(0xE1, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0xF1, 5, 2, AddressingMode.INDIRECT_Y, 1))
    ops.append(op)

    op = Op("STA", "STore Accumulator", OpType.MOVEMENT, [])
    op.add_operand(OpCode(0x85, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x95, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x8D, 4, 3, AddressingMode.ABSOLUTE))
    op.add_operand(OpCode(0x9D, 5, 3, AddressingMode.ABSOLUTE_X))
    op.add_operand(OpCode(0x99, 5, 3, AddressingMode.ABSOLUTE_Y))
    op.add_operand(OpCode(0x81, 6, 2, AddressingMode.INDIRECT_X))
    op.add_operand(OpCode(0x91, 6, 2, AddressingMode.INDIRECT_Y))
    ops.append(op)

    ops.append(
        Op(
            "TXS",
            "Transfer X to Stack ptr",
            OpType.MOVEMENT,
            [],
            [OpCode(0x9A, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "TSX",
            "Transfer Stack ptr to X",
            OpType.MOVEMENT,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0xBA, 2, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "PHA",
            "PusH Accumulator",
            OpType.STACK,
            [],
            [OpCode(0x48, 3, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "PLA",
            "PuLl Accumulator",
            OpType.STACK,
            [Flag.NEGATIVE, Flag.ZERO],
            [OpCode(0x68, 4, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "PHP",
            "PusH Processor status",
            OpType.STACK,
            [],
            [OpCode(0x08, 3, 1, AddressingMode.IMPLIED)],
        )
    )
    ops.append(
        Op(
            "PLP",
            "PuLl Processor status",
            OpType.STACK,
            [
                Flag.NEGATIVE,
                Flag.ZERO,
                Flag.INTERRUPT_DISABLE,
                Flag.DECIMAL_MODE,
                Flag.OVERFLOW,
                Flag.CARRY,
            ],
            [OpCode(0x28, 4, 1, AddressingMode.IMPLIED)],
        )
    )

    op = Op("STX", "STore X register", OpType.MOVEMENT, [])
    op.add_operand(OpCode(0x86, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x96, 4, 2, AddressingMode.ZERO_PAGE_Y))
    op.add_operand(OpCode(0x8E, 4, 3, AddressingMode.ABSOLUTE))
    ops.append(op)

    op = Op("STY", "STore Y register", OpType.MOVEMENT, [])
    op.add_operand(OpCode(0x84, 3, 2, AddressingMode.ZERO_PAGE))
    op.add_operand(OpCode(0x94, 4, 2, AddressingMode.ZERO_PAGE_X))
    op.add_operand(OpCode(0x8C, 4, 3, AddressingMode.ABSOLUTE))
    ops.append(op)

    dicts = [o.get_dict() for o in ops]
    print(dicts)

    js = json.dumps([o.get_dict() for o in ops], indent=4)
    f.write(js)
