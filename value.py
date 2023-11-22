from bot_base import *
from value import *

direction_list = [[0, -1], [0, 1], [1, 0], [-1, 0]]

def scan_value(step, player_id, round, map, players, bombs, items, map_danger):
    map_value = [[0 for _ in range(15)] for _ in range(15)]
    for x in range(15):
        for y in range(15):
            mark_value(x, y, map, items, map_value)


def mark_value(x, y, map, items, map_value):
    if not items[x][y]:
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i < 0 or i >= len(map) or j < 0 or j >= len(map[0]):
                    continue
                elif not BlockType.BLOCK.match(map[i][j]):
                    map_value += 10
        return

    queue=[{"x": x, "y": y, "depth": 0, "value": init_value(items[x][y])}]
    depth_max = 6

    while queue:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            status["value"] *= 0.75
            if status["x"] < 0 or status["x"] >= len(map) or status["y"] < 0 or status["y"] >= len(map[0]):
                continue
            elif status["depth"] > depth_max:
                continue
            elif not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                queue.append(status)
                map_value[status["x"]][status["y"]] += status["value"]
        del queue[0]


def init_value(ItemType):
    pass
    return 1