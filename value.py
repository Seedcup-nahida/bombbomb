from random import *
from bot_base import *
from collections import deque

from resp import ItemType

judge_value_gap = 150
init_value_rate = 50
distance_decay = 0.7
distance_warning = 4


def scan_value(step, player_id, map, players, items, map_danger, level):
    map_value = [[0 for _ in range(15)] for _ in range(15)]
    actions = []
    player = get_current_player(players, player_id)
    enemies = get_enemy_players(players, player_id)

    for x in range(len(map)):
        for y in range(len(map[0])):
            mark_value(x, y, map, items, map_value, level, player, enemies)

    if player["bomb_now_num"] > 0:
        bomb_action = put_bomb(player, map, items, enemies, map_value, level)
        if bomb_action:
            actions.append(bomb_action)
            step -= 1
    if step <= 0:
        return actions

    move_action = move(step, player, map, map_value, map_danger, enemies, level)
    actions.extend(move_action)

    return actions


def mark_value(x, y, map, items, map_value, level, player, enemies):
    if BlockType.BOX.match(map[x][y]):
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if not (0 <= i < 15 and 0 <= j < 15):
                    continue
                elif not BlockType.BLOCK.match(map[i][j]):
                    map_value[i][j] += 10
        return
    if items[x][y] == ItemType.NO_POTION:
        return

    queue = deque([(x, y, 0, init_value_rate
                    * init_value(items[x][y], level, player, enemies, map, x, y))])  # x, y, depth, value
    depth_max = 6

    while queue:
        x, y, depth, value = queue.popleft()
        depth += 1
        value *= distance_decay
        for direction in direction_list:
            nx, ny = x + direction[0], y + direction[1]
            if depth > depth_max or not (0 <= nx < 15 and 0 <= ny < 15):
                continue
            elif not BlockType.BLOCK.match(map[nx][ny]):
                queue.append((nx, ny, depth, value))
                map_value[nx][ny] = max(map_value[nx][ny], value)


def put_bomb(player, map, items, enemies, map_value, level):
    boxes = []

    for direction in direction_list:
        x = player["x"]
        y = player["y"]
        for i in player["bomb_range"]:
            x += direction[0]
            y += direction[1]
            if 0 <= x < len(map) and 0 <= y < len(map[0]):
                if BlockType.BLOCK.match(map[x][y]):
                    if BlockType.BOX.match(map[x][y]):
                        boxes.append((x, y))
                    break
                elif items[x][y]:
                    return None
                else:
                    for enemy in enemies:
                        if x == enemy["x"] and y == enemy["y"]:
                            return ActionType.PLACED
    if level == 1 and len(boxes) >= 2:
        return ActionType.PLACED
    elif len(boxes) == 0:
        return None

    x = player["x"]
    y = player["y"]
    before_put_value = map_value[x][y]
    after_map = clone_map(map)
    after_map_value = clone_map(map_value)
    for box_x, box_y in boxes:
        after_map[box_x][box_y] = BlockType.EMPTY
    for i in range(len(map)):
        for j in range(len(map[0])):
            mark_value(i, j, after_map, items, after_map_value, level, player, enemies)
    after_put_value = after_map_value[x][y]

    for dx, dy in direction_list:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(map) and 0 <= ny < len(map[0]):
            before_put_value += map_value[nx][ny]
            after_put_value += after_map_value[nx][ny]
    if (after_put_value - before_put_value) >= judge_value_gap:
        return ActionType.PLACED


def move(step, player, map, map_value, map_danger, enemies, level):
    actions = []
    before_x, before_y = player["x"], player["y"]

    for _ in range(step):
        value_max = -1
        toward_direction = (0, 0)
        for direction in direction_list:
            nx, ny = before_x + direction[0], before_y + direction[1]
            if 0 <= nx < len(map) and 0 <= ny < len(map[0]):
                if map_danger[nx][ny] > 0:
                    continue
                elif map_value[nx][ny] > value_max:
                    value_max = map_value[nx][ny]
                    toward_direction = direction
                elif map_value[nx][ny] == value_max:
                    distance_change = 0
                    for enemy in enemies:
                        distance_change += abs(nx - enemy["x"]) + abs(ny - enemy["y"])
                        distance_change -= abs(before_x + toward_direction[0] - enemy["x"]) + abs(before_y + toward_direction[1] - enemy["y"])
                    if (level == 1 and distance_change > 0) or (level == 2 and distance_change < 0):
                        toward_direction = direction
                    elif distance_change == 0:
                        if random() % 2:
                            toward_direction = direction
        if not toward_direction and toward_direction != (0, 0):
            break
        actions.append(convert_direction(toward_direction))
        before_x += toward_direction[0]
        before_y += toward_direction[1]

    return actions


def init_value(item_type, level, player, enemies, map, x, y):
    if not (level == 1 or level == 2):
        raise Exception("level error")

    if item_type == ItemType.NO_POTION:
        return 0
    elif item_type == ItemType.BOMB_RANGE:
        return 2 + level
    elif item_type == ItemType.BOMB_NUM:
        return 4 - level
    elif item_type == ItemType.INVINCIBLE:
        return 3 + level
    elif item_type == ItemType.SHIELD:
        if player["hp"] == 3:
            return 2
        return 3

        # 可能需要参数判断对战是否执行
    elif item_type == ItemType.HP:
        if player["hp"] < 3:
            return 5 - player["hp"]
        # elif player["hp"] == 3:
        for enemy in enemies:
            distance = get_distance(map, (enemy["x"], enemy["y"]), (x, y))
            if distance > 0:
                if 2 < distance <= distance_warning and enemy["hp"] < 3:
                    # 有敌人在附近，且敌人血量不满
                    return 3
        return 0


def get_distance(map, pos1, pos2):
    """calculate the distance between two points
    the pos should not be a block.
    the format of pos1 and pos2 is (x, y)

    return the distance between two points, if the two points are not connected, return -1"""
    if pos1 == pos2:
        return 0
    if BlockType.BLOCK.match(map[pos1[0]][pos1[1]]) or BlockType.BLOCK.match(map[pos2[0]][pos2[1]]):
        return -1

    queue = deque(((pos1[0], pos1[1], 0),))  # x, y, step
    visited = set()

    while queue:
        x, y, step = queue.popleft()
        pos = (x, y)
        if pos == pos2:
            return step

        visited.add(pos)
        step += 1

        for dx, dy in direction_list:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 15 and 0 <= ny < 15 and (nx, ny) not in visited and not BlockType.BLOCK.match(map[nx][ny]):
                queue.append((nx, ny, step))

    return -1
