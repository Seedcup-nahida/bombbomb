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

def step(data: dict) -> list[ActionType]:
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