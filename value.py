from random import *
from bot_base import *

direction_list = [[0, -1], [0, 1], [1, 0], [-1, 0]]
judge_value_gap = 150
distance_decay = 0.7

def scan_value(step, player_id, map, players, items, map_danger, level):
    map_value = [[0 for _ in range(15)] for _ in range(15)]
    actions = []
    player = get_current_player(players, player_id)
    enemies = get_enemy_players(players, player_id)

    for x in range(15):
        for y in range(15):
            mark_value(x, y, map, items, map_value, level, player, enemies)

    if player["bomb_now_num"] > 0:
        actions.append(put_bomb(player, map, items, enemies, map_value, level))
    if len(actions):
        step -= 1
    if step == 0:
        return actions

    move_action = move(step, player, map, map_value, map_danger, enemies, level)
    for action in move_action:
        actions.append(action)

    return actions


def mark_value(x, y, map, items, map_value, level, player, enemies):
    if not items[x][y]:
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i < 0 or i >= len(map) or j < 0 or j >= len(map[0]):
                    continue
                elif not BlockType.BLOCK.match(map[i][j]):
                    map_value += 10
        return

    queue=[{"x": x, "y": y, "depth": 0, "value": init_value(items[x][y], level, player, enemies)}]
    depth_max = 6

    while queue:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            status["value"] *= distance_decay
            if status["x"] < 0 or status["x"] >= len(map) or status["y"] < 0 or status["y"] >= len(map[0]):
                continue
            elif status["depth"] > depth_max:
                continue
            elif not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                queue.append(status)
                map_value[status["x"]][status["y"]] = max(map_value[status["x"]][status["y"]], status["value"])
        del queue[0]


def put_bomb(player, map, items, enemies, map_value, level):
    box = []

    for direction in direction_list:
        x = player["x"]
        y = player["y"]
        for i in player["bomb_range"]:
            x += direction[0]
            y += direction[1]
            if x >= 0 and x < len(map) and y >= 0 and y < len(map[0]):
                if BlockType.BLOCK.match(map[x][y]):
                    if map[x][y] & 2:
                        box.append([x, y])
                    break
                elif items[x][y] > 0:
                    return
                else:
                    for enemy in enemies:
                        if x == enemy["x"] and y == enemy["y"]:
                            return 5
    if level == 1 and len(box) >= 2:
        return 5
    elif len(box) == 0:
        return

    x = player["x"]
    y = player["y"]
    before_put_value = map_value[x][y]
    after_map = map
    after_map_value = [[0 for _ in range(15)] for _ in range(15)]
    for single_box in box:
        after_map[single_box[0]][single_box[1]] = 0
    for i in range(15):
        for j in range(15):
            map_value(i, j, after_map, items, after_map_value)
    after_put_value = after_map_value[x][y]
    for direction in direction_list:
        x += direction[0]
        y += direction[1]
        if x >= 0 and x < len(map) and y >= 0 and y < len(map[0]):
            before_put_value += map_value[x][y]
            after_put_value += after_map_value[x][y]
    if (after_put_value - before_put_value) >= judge_value_gap:
        return 5


def move(step, player, map, map_value, map_danger, enemies, level):
    actions = []
    before_x = player["x"]
    before_y = player["y"]

    for i in range(step):
        value_max = -1
        path = []
        for direction in direction_list:
            x = before_x + direction[0]
            y = before_y + direction[1]
            if x >= 0 and x < len(map) and y >= 0 and y < len(map[0]):
                if map_danger[x][y] > 0:
                    continue
                elif map_value[x][y] > value_max:
                    value_max = map_value[x][y]
                    path = direction
                elif map_value[x][y] == value_max:
                    distance_change = 0
                    for enemy in enemies:
                        distance_change += abs(x - enemy["x"]) + abs(y - enemy["y"])
                        distance_change -= abs(before_x + path[0] - enemy["x"]) + abs(before_y + path[1] - enemy["y"])
                    if level == 1 and distance_change > 0 or level == 2 and distance_change < 0:
                        path = direction
                    elif distance_change == 0:
                        if random() % 2:
                            path = direction
        if not len(path):
            break
        actions.append(convert_list_to_direction(path))
        before_x += path[0]
        before_y += path[1]

    return actions


def init_value(item_type, level, player, enemies):
    pass
    return 1