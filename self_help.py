from bot_base import *

direction_list = [[0, -1], [0, 1], [1, 0], [-1, 0]]


def scan_danger(player_id: int, round: int, map: list[list[dict]], players: list[dict], bombs: list[dict], map_danger: list[list[dict]]):
    actions = []
    # map_danger = scan_map_danger(map, bombs, players, player_id)
    player = get_current_player(players, player_id)
    x = player["x"]
    y = player["y"]
    if map_danger[x][y] != 0 and player["invincible_time"] == 0:
        actions = run(player, map, map_danger)
    return actions


def scan_map_danger(map, bombs, players, player_id) -> list[list]:
    danger = [[-(map[x][y] & BlockType.BLOCK.value) for y in range(len(map[x]))] for x in range(len(map))]
    # 0 is empty, -1 is block, >0 is bomb and bomb range

    for i in range(len(bombs)):
        x = bombs[i]["x"]
        y = bombs[i]["y"]
        danger[x][y] = -(i + 2)
    for bomb in bombs:
        flag_bomb(danger, bombs, bomb, max(1, 5 - bomb["round"]))
    for enemy in get_enemy_players(players, player_id):
        if enemy["invincible_time"] != 0:
            flag_enemy(enemy, map, danger)
    return danger


def flag_enemy(enemy, map, danger):
    depth_max = min(2, enemy["invincible_time"])
    queue = [{"x": enemy["x"], "y": enemy["y"], "depth": 0}]

    while queue:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            if status["x"] < 0 or status["x"] >= len(map) or status["y"] < 0 or status["y"] >= len(map[0]):
                continue
            elif status["depth"] > depth_max:
                continue
            elif not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                queue.append(status)
                danger[status["x"]][status["y"]] = 1
        del queue[0]


def flag_bomb(danger, bombs, bomb, danger_value):
    """danger_value is the value of the bomb, which is the round of the bomb
    the smaller the value, the more dangerous the bomb is"""
    if 0 < danger[bomb["x"]][bomb["y"]] < danger_value:
        return  # when the bomb is already flagged, do nothing
    danger[bomb["x"]][bomb["y"]] = danger_value

    for direction in direction_list:
        x = bomb["x"]
        y = bomb["y"]
        for _ in range(bomb["bomb_range"]):
            x += direction[0]
            y += direction[1]
            if x < 0 or x >= len(danger) or y < 0 or y >= len(danger[0]):
                break
            elif danger[x][y] == -1:
                break
            elif danger[x][y] == 0:
                danger[x][y] = danger_value
            elif danger[x][y] > 0:
                danger[x][y] = min(danger[x][y], danger_value)
            else:
                index = -danger[x][y] - 2
                fork_bomb = bombs[index]
                if fork_bomb["round"] < bomb["round"]:
                    flag_bomb(danger, bombs, fork_bomb, danger_value)
                    break


def run(player, map, map_danger):
    queue = [{"x": player["x"], "y": player["y"], "depth": 0, "path": []}]
    safe_path = None
    dire_actions = []

    while True:
        for direction in direction_list:
            status = dict(queue[0])
            status["x"] += direction[0]
            status["y"] += direction[1]
            status["depth"] += 1
            status["path"] = status["path"][::]
            status["path"].append(direction)
            if status["x"] < 0 or status["x"] >= len(map) or status["y"] < 0 or status["y"] >= len(map[0]):
                continue
            if not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                if map_danger[status["x"]][status["y"]] == 0:
                    safe_path = status["path"]
                    break
                elif map_danger[status["x"]][status["y"]] > status["depth"]:
                    queue.append(status)
        del queue[0]
        if safe_path or not queue:
            break

    if safe_path:
        if len(safe_path) == 1:
            dire_actions.append(safe_path[0])
        else:
            dire_actions.append(safe_path[0])
            dire_actions.append(safe_path[1])
    else:
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
