from bot_base import *

direction = [[0, -1], [0, 1], [1, 0], [-1, 0]]


def scan_danger(data):
    map = data["map"]
    bomb = data["bombs"]
    player = get_current_player(data["players"], data["player_id"])
    enemies = get_enemy_players(data["players"], data["player_id"])
    map_danger = [[0 for _ in range(15)] for _ in range(15)]
    actions = []
    for i in range(len(bomb)):
        scan_danger_single(map, map_danger, bomb[i])
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
    status = {"x": enemy["x"], "y": enemy["y"], "depth": 0}
    queue = [status]
    while len(queue):
        for dir in direction:
            status = queue[0]
            status["x"] += dir[0]
            status["y"] += dir[1]
            status["depth"] += 1
            if status["x"] < 0 or status["x"] > 14 or status["y"] < 0 or status["y"] > 14:
                pass
            elif status["depth"] > depth_max:
                pass
            elif not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                queue.append(status)
                map_danger[status["x"]][status["y"]] = 1
        del queue[0]


def scan_danger_single(map, map_danger, bomb):  # 和scan_danger不一样，此处bomb为字典而非列表
    x = bomb["x"]
    y = bomb["y"]
    time = 5 - bomb["round"]
    len = bomb["bomb_range"]
    flag_bomb(x, y, time, map_danger)
    for i in range(4):
        x = bomb["x"]
        y = bomb["y"]
        for j in range(len):
            x += direction[i][0]
            y += direction[i][1]
            if 15 > x >= 0 and 15 > y >= 0:
                if BlockType.BLOCK.match(map[x][y]):
                    break
                flag_bomb(x, y, time, map_danger)


def run(player, map, map_danger):
    status = {"x": player["x"], "y": player["y"], "depth": 0, "path": 0}
    queue = [status]
    safe_path = []
    path = []
    actions = []
    while 1:
        for i in range(4):
            status = dict(queue[0])
            status["x"] += direction[i][0]
            status["y"] += direction[i][1]
            status["depth"] += 1
            status["path"] = status["path"] * 10 + i + 1
            if status["x"] < 0 or status["x"] > 14 or status["y"] < 0 or status["y"] > 14:
                continue
            elif BlockType.BLOCK.match(map[status["x"]][status["y"]]) == 0:
                if map_danger[status["x"]][status["y"]] == 0:
                    safe_path = status
                    break
                elif map_danger[status["x"]][status["y"]] - status["depth"] > 0:
                    queue.append(status)
        del queue[0]
        if len(safe_path) != 0 or len(queue) == 0:
            break
    if len(safe_path):
        if safe_path["path"] < 10:
            actions.append(safe_path["path"])
        else:
            while safe_path["path"]:
                path.append(safe_path["path"] % 10)
                safe_path["path"] = (safe_path["path"] - safe_path["path"] % 10) / 10
            actions.append(path[-1])
            actions.append(path[-2])
    else:
        actions = [1, 1]
        time_left = [0, 0]
        x = player["x"]
        y = player["y"]
        for i in range(2):
            for j in range(4):
                if not BlockType.BLOCK.match(map[status["x"]][status["y"]]):
                    pass
                elif map_danger[x + direction[j][0]][y + direction[j][1]] > time_left[i]:
                    time_left = map_danger[x + direction[j][0]][y + direction[j][1]]
                    actions[i] = j + 1
            x += direction[actions[i] - 1][0]
            y += direction[actions[i] - 1][1]
    return actions