
# https://adventofcode.com/2021/day/25
# solves part 1

import array
import hashlib


class SeaFloor:
    def __init__(self, data: list[str]):
        self._width = len(data[0])
        self._height = len(data)
        self._data = array.array("u", "".join(data))
        self._buffer = array.array("u", self._data)

    @staticmethod
    def _move_transpose(data_in: array, data_out: array, width: int, height: int, symbol: str):
        # stores the result transposed so that the next direction can be processed using the same code
        for line_index in range(height):
            element = data_in[(line_index + 1) * width - 1]
            next_element = data_in[line_index * width]
            for element_index in range(width):
                prev_element = element
                element = next_element
                next_element = data_in[line_index * width + (element_index + 1) % width]
                if element == symbol and next_element == ".":
                    data_out[element_index * height + line_index] = "."
                elif element == "." and prev_element == symbol:
                    data_out[element_index * height + line_index] = symbol
                else:
                    data_out[element_index * height + line_index] = element

    def _move(self):
        SeaFloor._move_transpose(self._data, self._buffer, self._width, self._height, ">")
        SeaFloor._move_transpose(self._buffer, self._data, self._height, self._width, "v")

    def _sha256(self):
        o = hashlib.sha256()
        o.update(self._data)
        return o.digest()

    def simulate(self) -> int:
        result = 0
        last_sha = self._sha256()
        keys = set()
        keys.add(last_sha)
        while True:
            self._move()
            result += 1
            sha = self._sha256()
            if sha in keys:
                if sha == last_sha:
                    return result
                else:
                    raise ValueError("infinite loop detected at iteration %d" % result)
            keys.add(sha)
            last_sha = sha

    def __repr__(self):
        result: list[str] = []
        for line_index in range(self._height):
            for element_index in range(self._width):
                result.append(self._data[line_index * self._width + element_index])
            result.append("\n")

        return "".join(result)


def main():
    """Expects input on stdin"""

    lines = None
    try:
        lines = [input()]
        width = len(lines[0])
        while True:
            line = input()
            if len(line) != width:
                raise ValueError("inconsistent input dimensions")
            lines.append(line)
    except EOFError:
        pass
    sea_floor = SeaFloor(lines)
    print(sea_floor.simulate())


if __name__ == "__main__":
    main()
