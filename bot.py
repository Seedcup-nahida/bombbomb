from bot_base import *
from resp import ItemType
from self_help import *
# from value import *

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
    step = 2
    actions = []  # ATTENTION: len(actions) <= player.speed, equal to player.speed is recommended
    actions_signal = []
    actions_signal.append(scan_danger(data))
    for i in range(len(actions_signal)):
        for action in actions_signal[i]:
            if action == 0:
                actions.append(ActionType.PLACED)
            elif action == 1:
                actions.append(ActionType.MOVE_LEFT)
            elif action == 2:
                actions.append(ActionType.MOVE_RIGHT)
            elif action == 3:
                actions.append(ActionType.MOVE_DOWN)
            elif action == 4:
                actions.append(ActionType.MOVE_UP)
    print(actions)
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
