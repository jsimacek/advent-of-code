
# https://adventofcode.com/2021/day/24
# brute force approach for solving part 1

import abc
import typing


class State:
    def __init__(self, ip: int, variables: tuple[int, ...]):
        self.ip = ip
        self.variables = variables

    def transform(self, variable_index: int, value: int) -> "State":
        """
        Create a new state obtained by changing the content of the selected variable within this state
        :param variable_index: selected variable index
        :param value: new value
        :return: modified state
        """
        return State(self.ip + 1, self.variables[0:variable_index] + (value,) + self.variables[variable_index + 1:])

    def __str__(self):
        return str((self.ip, self.variables))

    def __hash__(self):
        return hash((self.ip, self.variables))

    def __eq__(self, other: "State"):
        return (self.ip, self.variables) == (other.ip, other.variables)


VARIABLE_INDICES: dict[str, int] = {"w": 0, "x": 1, "y": 2, "z": 3}
VARIABLE_ACCESSOR: typing.Callable[[State, int], int] = lambda s, x: s.variables[x]
CONSTANT_ACCESSOR: typing.Callable[[State, int], int] = lambda s, x: x


class Instruction(abc.ABC):
    @abc.abstractmethod
    def execute(self, state: State, sid: str) -> list[tuple[State, str]]:
        """
        Produces a list of successor states arising from application of this instruction on the provided state. The
        states are traversed using LIFO strategy hence the last returned state is processed first, etc.
        :param state: machine state
        :param sid: string representing the input that has been read so far
        :return: list of (state, input string) pairs
        """


class Inp(Instruction):
    def __init__(self, args: list[str]):
        self._dst_index = VARIABLE_INDICES[args[1]]

    def execute(self, state: State, sid: str) -> list[tuple[State, str]]:
        # create one successor state for each individual single digit input
        return [(state.transform(self._dst_index, x), sid + str(x)) for x in range(1, 10)]


class BinOp(Instruction, abc.ABC):
    def __init__(self, args: list[str]):
        self._dst_index = VARIABLE_INDICES[args[1]]
        if args[2] in VARIABLE_INDICES:
            self._src = VARIABLE_INDICES[args[2]]
            self._accessor = VARIABLE_ACCESSOR
        else:
            self._src = int(args[2])
            self._accessor = CONSTANT_ACCESSOR

    def execute(self, state: State, sid: str) -> list[tuple[State, str]]:
        return [
            (
                state.transform(
                    self._dst_index,
                    self._get_result(state.variables[self._dst_index], self._accessor(state, self._src))
                ),
                sid
            )
        ]

    @abc.abstractmethod
    def _get_result(self, lhs: int, rhs: int) -> int:
        pass


class Add(BinOp):
    def _get_result(self, lhs: int, rhs: int) -> int:
        return lhs + rhs


class Div(BinOp):
    def _get_result(self, lhs: int, rhs: int) -> int:
        return lhs // rhs


class Mod(BinOp):
    def _get_result(self, lhs: int, rhs: int) -> int:
        return lhs % rhs


class Mul(BinOp):
    def _get_result(self, lhs: int, rhs: int) -> int:
        return lhs * rhs


class Eql(BinOp):
    def _get_result(self, lhs: int, rhs: int) -> int:
        return 1 if lhs == rhs else 0


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

    states: set[State] = set()
    stack = [(State(0, (0, 0, 0, 0)), "")]
    while len(stack) > 0:
        state, sid = stack.pop()
        if state in states:
            continue
        states.add(state)
        if state.ip >= len(code):
            if state.variables[3] == 0:
                print(sid)
                return
        else:
            stack.extend(code[state.ip].execute(state, sid))


if __name__ == "__main__":
    main()
