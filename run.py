import sys
import heapq
from itertools import count

ENERGY = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
TARGET_ROOM = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
ROOM_POS = [2, 4, 6, 8]
VALID_HALL_STOPS = [0, 1, 3, 5, 7, 9, 10]


def parse_input(lines: list[str]):

    hallway = [None] * 11
    rooms = [[] for _ in range(4)]

    depth = len(lines) - 3
    
    for i in range(len(lines) - 2, 1, -1):
        line = lines[i]
        for room_idx in range(4):
            pos = 3 + room_idx * 2
            if pos < len(line) and line[pos] in "ABCD":
                rooms[room_idx].append(line[pos])

    return hallway, rooms, depth


def state_to_tuple(hallway, rooms):
    return (tuple(hallway), tuple(tuple(r) for r in rooms))


def is_goal_state(rooms, depth):
    for i, t in enumerate("ABCD"):
        if len(rooms[i]) != depth:
            return False
        if not all(x == t for x in rooms[i]):
            return False
    return True


def can_enter_room(room, obj):
    return all(x == obj for x in room)


def corridor_clear(hallway, start, end):
    if start < end:
        for i in range(start + 1, end + 1):
            if hallway[i] is not None:
                return False
    else:
        for i in range(end, start):
            if hallway[i] is not None:
                return False
    return True


def get_moves(hallway, rooms, depth):
    moves = []

    # Коридор - комната
    for hpos, obj in enumerate(hallway):
        if obj is None:
            continue
        target = TARGET_ROOM[obj]
        target_pos = ROOM_POS[target]
        room = rooms[target]
        if not can_enter_room(room, obj):
            continue
        if not corridor_clear(hallway, hpos, target_pos):
            continue

        steps = abs(hpos - target_pos) + (depth - len(room))
        cost = steps * ENERGY[obj]
        new_hall = hallway[:]
        new_hall[hpos] = None
        new_rooms = [r[:] for r in rooms]
        new_rooms[target].append(obj)
        moves.append((cost, new_hall, new_rooms))

    # Комната - коридор
    for ri in range(4):
        room = rooms[ri]
        if not room:
            continue
        target_type = "ABCD"[ri]
        if all(x == target_type for x in room):
            continue

        obj = room[-1]
        door_pos = ROOM_POS[ri]
        for hpos in VALID_HALL_STOPS:
            if not corridor_clear(hallway, door_pos, hpos):
                continue
            if hallway[hpos] is not None:
                continue

            steps = (depth - len(room) + 1) + abs(hpos - door_pos)
            cost = steps * ENERGY[obj]
            new_hall = hallway[:]
            new_hall[hpos] = obj
            new_rooms = [r[:] for r in rooms]
            new_rooms[ri] = room[:-1]
            moves.append((cost, new_hall, new_rooms))

    return moves


def heuristic(hallway, rooms):
    total = 0
    for pos, obj in enumerate(hallway):
        if obj is not None:
            target = TARGET_ROOM[obj]
            target_pos = ROOM_POS[target]
            total += abs(pos - target_pos) * ENERGY[obj]

    for ri, room in enumerate(rooms):
        target_type = "ABCD"[ri]
        for i, obj in enumerate(room):
            if obj != target_type:
                target = TARGET_ROOM[obj]
                total += (len(room) - i + abs(ROOM_POS[ri] - ROOM_POS[target])) * ENERGY[obj]
    return total


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    hallway, rooms, depth = parse_input(lines)
    counter = count()
    start = state_to_tuple(hallway, rooms)
    pq = [(heuristic(hallway, rooms), next(counter), 0, hallway, rooms)]
    visited = {start: 0}

    while pq:
        _, _, cost, hallway, rooms = heapq.heappop(pq)

        if is_goal_state(rooms, depth):
            return cost

        state = state_to_tuple(hallway, rooms)
        if cost > visited.get(state, float('inf')):
            continue

        for move_cost, new_hall, new_rooms in get_moves(hallway, rooms, depth):
            new_cost = cost + move_cost
            new_state = state_to_tuple(new_hall, new_rooms)
            if new_cost < visited.get(new_state, float('inf')):
                visited[new_state] = new_cost
                heapq.heappush(
                    pq,
                    (new_cost + heuristic(new_hall, new_rooms), next(counter), new_cost, new_hall, new_rooms)
                )

    return -1


def main():
    lines = [line.rstrip('\n') for line in sys.stdin if line.strip()]
    print(solve(lines))


if __name__ == "__main__":
    main()
    