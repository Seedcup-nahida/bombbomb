from bot_base import *

direction_list = [[0, -1], [0, 1], [1, 0], [-1, 0]]


def scan_danger(player_id: int, round: int, map: list[list[dict]], players: list[dict], bombs: list[dict], items: list[list[dict]]):
    player = get_current_player(players, player_id)
    enemies = get_enemy_players(players, player_id)
    map_danger = [[0 for _ in range(15)] for _ in range(15)]
    actions = []

    for bomb in bombs:
        scan_danger_single(map, map_danger, bomb)
    for enemy in enemies:
        if enemy["invincible_time"] != 0:
            flag_enemy(enemy, map, map_danger)
    x = player["x"]
    y = player["y"]
    if map_danger[x][y] != 0 and player["invincible_time"] == 0:
        actions = run(player, map, map_danger)
    return actions


def flag_bomb(x, y, time, map_danger):
    if map_danger[x][y] == 0:
        map_danger[x][y] = max(1, time)
    else:
        map_danger[x][y] = min(map_danger[x][y], max(1, time))


def flag_enemy(enemy, map, map_danger):
    depth_max = min(2, enemy["invincible_time"])
    queue = [{"x": enemy["x"], "y": enemy["y"], "depth": 0}]

    while queue:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            if status["x"] < 0 or status["x"] > 14 or status["y"] < 0 or status["y"] > 14:
                continue
            elif status["depth"] > depth_max:
                continue
            elif not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                queue.append(status)
                map_danger[status["x"]][status["y"]] = 1
        del queue[0]


def scan_danger_single(map, map_danger, bomb: dict):
    x = bomb["x"]
    y = bomb["y"]
    time = 5 - bomb["round"]
    flag_bomb(x, y, time, map_danger)

    for direction in direction_list:
        x = bomb["x"]
        y = bomb["y"]
        for _ in range(bomb["bomb_range"]):
            x += direction[0]
            y += direction[1]
            if 0 <= x < 15 and 0 <= y < 15:
                if BlockType.BLOCK.match(map[x][y]):
                    break
                flag_bomb(x, y, time, map_danger)


def run(player, map, map_danger):
    queue = [{"x": player["x"], "y": player["y"], "depth": 0, "path": []}]
    safe_path = None
    path = []
    dire_actions = []

    while True:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            status["path"] = status["path"][::]
            status["path"].append(direction)
            if status["x"] < 0 or status["x"] > 14 or status["y"] < 0 or status["y"] > 14:
                continue
            if not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                if map_danger[status["x"]][status["y"]] == 0:
                    safe_path = status["path"]
                    break
                elif map_danger[status["x"]][status["y"]] - status["depth"] > 0:
                    queue.append(status)
        del queue[0]
        if safe_path or not queue:
            break

    if safe_path:
        if len(safe_path) == 1:
            dire_actions.append(safe_path)
        else:
            dire_actions.append(safe_path[0])
            dire_actions.append(safe_path[1])
    else:
        # TODO
        dire_actions = [direction_list[0], direction_list[0]]
        time_left = [0, 0]
        x = player["x"]
        y = player["y"]
        for i in range(2):
            # TODO
            for direction in direction_list:
                tmp_x = x + direction[0]
                tmp_y = y + direction[1]
                if BlockType.BLOCK.match(map[tmp_x][tmp_y]):
                    continue
                elif map_danger[tmp_x][tmp_y] > time_left[i]:
                    time_left = map_danger[tmp_x][tmp_y]
                    dire_actions[i] = direction
                elif map_danger[tmp_x][tmp_y] == time_left[i]:
                    pass
            x += dire_actions[i][0]
            y += dire_actions[i][1]

    return [convert_list_to_direction(direction) for direction in dire_actions]
