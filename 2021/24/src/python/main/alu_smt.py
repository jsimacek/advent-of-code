
# https://adventofcode.com/2021/day/24
# smt approach for solving part 1 & 2
# requires z3 package

import abc
import typing
import z3

ZERO, ONE = z3.BitVecVal(0, 64), z3.BitVecVal(1, 64)


class State:
    def __init__(self, ip: int, variables: tuple[any, ...]):
        self.ip = ip
        self.variables = variables

    def transform(self, variable_index: int, value: any) -> "State":
        """
        Create a new state obtained by changing the content of the selected variable within this state
        :param variable_index: selected variable index
        :param value: new value
        :return: modified state
        """
        return State(self.ip + 1, self.variables[0:variable_index] + (value,) + self.variables[variable_index + 1:])

    def __repr__(self):
        return str((self.ip, self.variables))

    def __hash__(self):
        return hash((self.ip, self.variables))

    def __eq__(self, other: "State"):
        return (self.ip, self.variables) == (other.ip, other.variables)


VARIABLE_INDICES: dict[str, int] = {"w": 0, "x": 1, "y": 2, "z": 3}
VARIABLE_ACCESSOR: typing.Callable[[State, int], any] = lambda s, x: s.variables[x]
CONSTANT_ACCESSOR: typing.Callable[[State, int], any] = lambda s, x: z3.BitVecVal(x, 64)


class Instruction(abc.ABC):
    @abc.abstractmethod
    def execute(self, state: State) -> State:
        pass


class Inp(Instruction):
    INDEX: int = 0
    DIGITS: list[any] = []

    def __init__(self, args: list[str]):
        self._dst_index = VARIABLE_INDICES[args[1]]

    def execute(self, state: State) -> State:
        digit = z3.BitVec(f"i{Inp.INDEX}", 64)
        Inp.DIGITS.append(digit)
        Inp.INDEX += 1
        return state.transform(self._dst_index, digit)


class BinOp(Instruction, abc.ABC):
    def __init__(self, args: list[str]):
        self._dst_index = VARIABLE_INDICES[args[1]]
        if args[2] in VARIABLE_INDICES:
            self._src = VARIABLE_INDICES[args[2]]
            self._accessor = VARIABLE_ACCESSOR
        else:
            self._src = int(args[2])
            self._accessor = CONSTANT_ACCESSOR

    def execute(self, state: State) -> State:
        return state.transform(
            self._dst_index, self._get_result(state.variables[self._dst_index], self._accessor(state, self._src))
        )

    @abc.abstractmethod
    def _get_result(self, lhs: any, rhs: any) -> any:
        pass


class Add(BinOp):
    def _get_result(self, lhs: any, rhs: any) -> any:
        return lhs + rhs


class Div(BinOp):
    def _get_result(self, lhs: any, rhs: any) -> any:
        return lhs / rhs


class Mod(BinOp):
    def _get_result(self, lhs: any, rhs: any) -> any:
        return lhs % rhs


class Mul(BinOp):
    def _get_result(self, lhs: any, rhs: any) -> any:
        return lhs * rhs


class Eql(BinOp):
    def _get_result(self, lhs: any, rhs: any) -> any:
        return z3.If(lhs == rhs, ONE, ZERO)


INSTRUCTIONS: dict[str, typing.Callable[[list[str]], Instruction]] = {
    "add": Add, "div": Div, "eql": Eql, "inp": Inp, "mod": Mod, "mul": Mul
}


def main():
    """Expects input on stdin"""

    code: list[Instruction] = []
    try:
        while True:
            args = input().split(" ")
            code.append(INSTRUCTIONS[args[0]](args))
    except EOFError:
        pass

    state = State(0, (ZERO, ZERO, ZERO, ZERO))
    for instr in code:
        state = instr.execute(state)

    solver = z3.Optimize()
    for d in Inp.DIGITS:
        solver.add(z3.And(1 <= d, d <= 9))
    # the base 10 result to be optimized
    digits_base_10 = z3.BitVec(f"digits_base_10", 64)
    solver.add(digits_base_10 == sum((10 ** i) * d for i, d in enumerate(Inp.DIGITS[::-1])))
    solver.add(state.variables[3] == 0)
    for f in (solver.minimize, solver.maximize):
        solver.push()
        f(digits_base_10)
        if solver.check() != z3.sat:
            raise ValueError("solution not found")
        print(solver.model().eval(digits_base_10))
        solver.pop()


if __name__ == "__main__":
    main()
