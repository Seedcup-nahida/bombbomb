from bot_base import *
from resp import ItemType

"""
enum ActionType:// 动作类型
  SILENT = 0, // 静止不动
  MOVE_LEFT = 1,
  MOVE_RIGHT = 2,
  MOVE_UP = 3,
  MOVE_DOWN = 4,
  PLACED = 5, // 放置炸弹或者道具
"""


box_count = 0


def game_update(data: dict, player_id: int) -> list[ActionType]:
    """make a decision based on the data received from the server.

    recvData is the data received from the server,
    hasUpdated is a flag indicating whether the data has been updated.

    return a list of values of ActionType in req.py and length less than {player.speed}
    """
    # TODO
    actions = []  # ATTENTION: len(actions) <= player.speed, equal to player.speed is recommended

    # test code below, only set bombs
    actions.append(ActionType.PLACED)
    return actions


def game_init(data: dict, player_id: int):
    """"param data is the same of step function,
    will be called when game start
    """
    for block_row in data["map"]:
        for b in block_row:
            if BlockType.BOX.match(b):
                global box_count
                box_count += 1
