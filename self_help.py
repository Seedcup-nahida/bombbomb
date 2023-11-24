from collections import deque

from bot_base import *


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
    queue = deque([(enemy["x"], enemy["y"], 0)])  # x, y, depth

    while queue:
        x, y, depth = queue.popleft()
        depth += 1
        for dx, dy in direction_list:
            nx, ny = x + dx, y + dy
            if depth > depth_max or not (0 <= nx < len(map) and 0 <= ny < len(map[0])):
                continue
            elif not BlockType.BLOCK.match(map[nx][ny]):
                queue.append((nx, ny, depth))
                danger[nx][ny] = 1


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
            if not (0 <= x < len(danger) and 0 <= y < len(danger)):
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
    queue = deque([(player["x"], player["y"], 0, [])])  # x, y, depth, path
    safe_path = None
    dire_actions = []

    while queue:
        x, y, depth, path = queue.popleft()
        depth += 1
        for direction in direction_list:
            nx, ny = x + direction[0], y + direction[1]
            new_path = path.copy()
            new_path.append(direction)
            if not (0 <= nx < len(map) and 0 <= ny < len(map[0])):
                continue
            if not BlockType.BLOCK.match(map[nx][ny]):
                if map_danger[nx][ny] == 0:
                    safe_path = new_path
                    break
                elif map_danger[nx][ny] < depth:
                    queue.append((nx, ny, depth, new_path))
        if safe_path:
            break

    if safe_path:
        dire_actions.append(safe_path[0])
        if len(safe_path) > 1:
            dire_actions.append(safe_path[1])
    else:
        dire_actions = [direction_list[0] for _ in range(2)]
        time_left = [0 for _ in range(len(dire_actions))]
        x = player["x"]
        y = player["y"]
        for i in range(len(dire_actions)):
            # TODO
            for direction in direction_list:
                nx, ny = x + direction[0], y + direction[1]
                if BlockType.BLOCK.match(map[nx][ny]):
                    continue
                elif map_danger[nx][ny] > time_left[i]:
                    time_left = map_danger[nx][ny]
                    dire_actions[i] = direction
                elif map_danger[nx][ny] == time_left[i]:
                    pass
            x += dire_actions[i][0]
            y += dire_actions[i][1]

    return [convert_direction(direction) for direction in dire_actions]
