
# https://adventofcode.com/2021/day/23
# solves part 1

import abc
import copy
import queue


class State:
    """
    A compact representation of a system state
    """
    def __init__(self, data: list[int], active_locations: set["Location"]):
        self.data = data
        self.active_locations = active_locations

    def clone(self) -> "State":
        return State(copy.copy(self.data), copy.copy(self.active_locations))

    def __lt__(self, other: "State"):
        return self.data < other.data


class Location(abc.ABC):
    """
    A stateless representation of location. Many methods take external data parameter for obtaining the system state.
    """
    def __init__(self, index):
        self._index = index
        self._links: list[tuple[Location, int]] = []

    def __hash__(self):
        return hash(self._index)

    def __eq__(self, other: "Location"):
        return self._index == other._index

    def index(self):
        return self._index

    def add_link(self, place: "Location", weight: int):
        self._links.append((place, weight))

    @staticmethod
    def connect(p1: "Location", p2: "Location", weight: int):
        p1.add_link(p2, weight)
        p2.add_link(p1, weight)

    def links(self) -> list[tuple["Location", int]]:
        return self._links

    def candidate_moves(self, data: list[int]) -> list[tuple["Location", int]]:
        result: list[tuple[Location, int]] = []
        a = self.get(data)
        if a == 0:
            return result
        for link in self._links:
            if link[0].accepts(data, a):
                result.append(link)
        return result

    @abc.abstractmethod
    def is_active(self, data: list[int]) -> bool:
        """
        :param data: the system state
        :return: True if there is an amphipod eligible for moving out of this location
        """

    @abc.abstractmethod
    def get(self, data: list[int]) -> int:
        """
        :param data: the system state
        :return: the amphipod type that can move out of this location
        """

    @abc.abstractmethod
    def accepts(self, data: list[int], amphipod: int) -> bool:
        """
        :param data: the system state
        :param amphipod: amphipod type
        :return: True if the givne amphipod type can move to this  location
        """

    @abc.abstractmethod
    def put(self, data: list[int], amphipod: int) -> int:
        """
        Moves given amphipod in (1-4) or out (0) of this location
        :param data: the system state
        :param amphipod: amphipod type
        :return: a number of additional steps required to move the amphipod in/out of this location
        """


class Regular(Location):
    """
    Regular location contains at most one amphipod.
    """
    def is_active(self, data: list[int]) -> bool:
        return data[self._index] > 0

    def get(self, data: list[int]) -> int:
        return data[self._index]

    def accepts(self, data: list[int], amphipod: int) -> bool:
        return data[self._index] == 0

    def put(self, data: list[int], amphipod: int) -> int:
        data[self._index] = amphipod
        return 0


class Home(Location):
    """
    Home location can contain up to two amphipods.
    """
    def __init__(self, index: int, amphipod: int):
        super().__init__(index)
        self._amphipod = amphipod

    def is_active(self, data: list[int]) -> bool:
        return (data[self._index] > 0 and data[self._index] != self._amphipod and
                data[self._index] != (5 * self._amphipod) + self._amphipod)

    def get(self, data: list[int]) -> int:
        aa = data[self._index]
        a = aa // 5
        if a > 0:
            return a
        a = aa % 5
        return a

    def accepts(self, data: list[int], amphipod: int) -> bool:
        aa = data[self._index]
        a = aa // 5
        if a > 0:
            return False
        return self._amphipod == amphipod

    def put(self, data: list[int], amphipod: int) -> int:
        aa = data[self._index]
        if amphipod == 0:
            # moving out
            a = aa // 5
            if a == 0:
                data[self._index] = 0
                return 1
            else:
                data[self._index] = aa % 5
                return 0
        else:
            # moving in
            a = aa % 5
            if a == 0:
                data[self._index] = amphipod
                return 1
            else:
                data[self._index] = (amphipod * 5) + a
                return 0


AMPHIPODS = {".": 0, "A": 1, "B": 2, "C": 3, "D": 4}
REV_AMPHIPODS = (".", "A", "B", "C", "D")

# lower bound on energy required to move an amphipod of a particular type from a given location to its final destination
DISTANCES = (
    (0, 3, 50, 700, 9000),  # location 0
    (0, 2, 40, 600, 8000),  # location 1
    (0, 1, 30, 500, 7000),  # ...
    (0, 2, 20, 400, 6000),
    (0, 3, 10, 300, 5000),
    (0, 4, 20, 200, 4000),
    (0, 5, 30, 100, 3000),
    (0, 6, 40, 200, 2000),
    (0, 7, 50, 300, 1000),
    (0, 8, 60, 400, 2000),
    (0, 9, 70, 500, 3000),
    (0, 0, 40, 600, 8000),
    (0, 4, 00, 400, 6000),
    (0, 6, 40, 000, 4000),
    (0, 8, 60, 400, 0000),
    (0, 0, 50, 700, 9000),
    (0, 5, 00, 500, 7000),
    (0, 7, 50, 000, 5000),
    (0, 9, 70, 500, 0000)
)


def get_estimation(data: list[int]) -> int:
    result = 0
    for i in range(11):
        result += DISTANCES[i][data[i]]
    for i in range(4):
        result += DISTANCES[i + 11][data[i + 11] // 5]
        result += DISTANCES[i + 15][data[i + 11] % 5]

    return result


def print_state(data: list[int]):
    l = "".join([REV_AMPHIPODS[d] for d in data[0:11]])
    h1 = [REV_AMPHIPODS[d // 5] for d in data[11:15]]
    h2 = [REV_AMPHIPODS[d % 5] for d in data[11:15]]

    print(
        f"#############\n"
        f"#{l}#\n"
        f"###{h1[0]}#{h1[1]}#{h1[2]}#{h1[3]}###\n"
        f"  #{h2[0]}#{h2[1]}#{h2[2]}#{h2[3]}#\n"
        f"  #########"
    )


def main():
    """Expects input on stdin"""

    lines = [input(), input(), input(), input(), input()]

    # build and connect locations
    locations: list[Location] = []
    for i in range(11):
        locations.append(Regular(i))
    for i in range(4):
        locations.append(Home(i + 11, i + 1))

    Location.connect(locations[0], locations[1], 1)
    Location.connect(locations[1], locations[3], 2)
    Location.connect(locations[1], locations[11], 2)
    Location.connect(locations[11], locations[3], 2)
    Location.connect(locations[3], locations[5], 2)
    Location.connect(locations[3], locations[12], 2)
    Location.connect(locations[12], locations[5], 2)
    Location.connect(locations[5], locations[7], 2)
    Location.connect(locations[5], locations[13], 2)
    Location.connect(locations[13], locations[7], 2)
    Location.connect(locations[7], locations[9], 2)
    Location.connect(locations[7], locations[14], 2)
    Location.connect(locations[14], locations[9], 2)
    Location.connect(locations[9], locations[10], 1)

    # "parse" initial state
    data = 15 * [0]
    for i in range(1, 12):
        data[i] = AMPHIPODS[lines[1][i]]
    data[11] = 5 * AMPHIPODS[lines[2][3]] + AMPHIPODS[lines[3][3]]
    data[12] = 5 * AMPHIPODS[lines[2][5]] + AMPHIPODS[lines[3][5]]
    data[13] = 5 * AMPHIPODS[lines[2][7]] + AMPHIPODS[lines[3][7]]
    data[14] = 5 * AMPHIPODS[lines[2][9]] + AMPHIPODS[lines[3][9]]

    # best result at the start ~> infinity
    result = 2**63
    states: dict[tuple[int, ...], int] = {}
    todo: queue.PriorityQueue[tuple[int, int, State]] = queue.PriorityQueue()
    todo.put((get_estimation(data), 0, State(data, {p for p in locations if p.is_active(data)})))
    while not todo.empty():
        estimate, energy, state = todo.get()
        if result <= estimate:
            continue
        tdata = tuple(state.data)
        prev_energy = states.get(tdata)
        if prev_energy is not None and prev_energy <= energy:
            continue
        states[tdata] = energy
        if len(state.active_locations) == 0 and energy < result:
            # no amphipod wants to move => we have reached the goal
            result = energy
        for source in state.active_locations:
            for target, weight in source.candidate_moves(state.data):
                new_s = state.clone()
                a = source.get(new_s.data)
                new_e = energy + 10 ** (a - 1) * (weight + source.put(new_s.data, 0) + target.put(new_s.data, a))
                if not source.is_active(new_s.data):
                    new_s.active_locations.remove(source)
                if target.is_active(new_s.data):
                    new_s.active_locations.add(target)
                todo.put((get_estimation(new_s.data) + new_e, new_e, new_s))

    print(result)


if __name__ == "__main__":
    main()
