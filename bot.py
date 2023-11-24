from bot_base import *
from resp import ItemType
from self_help import *
from value import *

"""
enum ActionType:// 动作类型
  SILENT, // 静止不动
  MOVE_LEFT,
  MOVE_RIGHT,
  MOVE_UP,
  MOVE_DOWN,
  PLACED // 放置炸弹或者道具
"""


box_count = 0
judge_level2 = 0.1


def game_update(player_id: int, round: int, map: list[list[dict]], players: list[dict], bombs: list[dict], items: list[list[dict]]) -> list[ActionType]:
    """make a decision based on the data received from the server.

    return a list of values of ActionType in req.py and length less than {player.speed}
    """
    # TODO
    box = 0
    level = 1
    for block_row in map:
        for b in block_row:
            if BlockType.BOX.match(b):
                box += 1
    if box <= box_count * judge_level2:
        level = 2

    step = 2
    actions = []  # ATTENTION: len(actions) <= player.speed, equal to player.speed is recommended
    map_danger = scan_map_danger(map, bombs, players, player_id)

    actions_danger = scan_danger(player_id, round, map, players, bombs, map_danger)
    actions.extend(actions_danger)
    step -= len(actions_danger)

    if step > 0:
        actions_value = scan_value(step, player_id, map, players, items, map_danger, level)
        actions.extend(actions_value)
    return actions


def game_init(player_id, round, map, players, bombs, items):
    """"param data is the same of step function,
    will be called when game start
    """
    global box_count
    for block_row in map:
        for b in block_row:
            if BlockType.BOX.match(b):
                box_count += 1
