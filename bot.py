from enum import Enum

from req import ActionType
from config import config
from resp import ObjType, ActionResp


"""
enum ActionType:// 动作类型
  SILENT = 0, // 静止不动
  MOVE_LEFT = 1,
  MOVE_RIGHT = 2,
  MOVE_UP = 3,
  MOVE_DOWN = 4,
  PLACED = 5, // 放置炸弹或者道具
"""


def step(data) -> list[ActionType]:
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


class BlockType(Enum):
    EMPTY = 0
    BLOCK = 1  # 任何挡路的东西
    BOX = 2  # 可破坏的墙
    BOMB = 4
    ITEM = 8
    PLAYER = 16

    def __bool__(self):
        return self != BlockType.EMPTY

    def __int__(self):
        return self.value

    def match(self, value: int) -> bool:
        return self.value & value != 0


bombs_counter = []


def bombDecode(round, block, prop) -> dict:
    bomb = prop
    if bomb["round"] == round:
        bombs_counter.append(bomb["bomb_id"])
    bomb["round"] = 0
    for b in bombs_counter:
        if b["bomb_id"] == bomb["bomb_id"]:
            bomb["round"] = round - b["round"]
    bomb["x"] = block.x
    bomb["y"] = block.y
    bomb["bombed"] = False
    return bomb


def bombs_counter_clear(bomb_data):
    bomb_ids = [bomb["bomb_id"] for bomb in bomb_data]
    for bomb in bombs_counter:
        if bomb["bomb_id"] not in bomb_ids:
            bombs_counter.remove(bomb)


def packetDecode(recv_data: ActionResp, player_id) -> dict:
    data = {"player_id": recv_data.player_id,
            "round": recv_data.round,
            "map": [[0 for _ in range(config.get("map_size"))] for _ in range(config.get("map_size"))],
            "players": [],
            "bombs": [],
            "items": [[0 for _ in range(config.get("map_size"))] for _ in range(config.get("map_size"))],
            }

    for block in recv_data.map:
        block_type = 0
        if len(block.objs) != 0:
            for obj in block.objs:
                obj_property: dict = obj.property.to_json()
                if obj.type == ObjType.Block:
                    block_type |= BlockType.BLOCK.value  # 墙肯定是挡路的
                    if obj_property["removable"]:
                        block_type |= BlockType.BOX.value
                elif obj.type == ObjType.Player:
                    block_type |= BlockType.PLAYER.value
                    obj_property["x"] = block.x
                    obj_property["y"] = block.y
                    data["players"].append(obj_property)
                elif obj.type == ObjType.Bomb:
                    block_type |= BlockType.BOMB.value
                    block_type |= BlockType.BLOCK.value  # 炸弹也是挡路的
                    data["bombs"].append(bombDecode(data["round"], block, obj_property))
                elif obj.type == ObjType.Item:
                    block_type |= BlockType.ITEM.value
                    data["items"][block.x][block.y] = obj_property["item_type"]
                else:
                    raise Exception("unknown obj type")

        data["map"][block.x][block.y] = block_type

    bombs_counter_clear(data["bombs"])
    return data


def clone_map(map: list[list[int]]):
    """in case of modifying the map"""
    return [[map[x][y] for y in range(len(map[x]))] for x in range(len(map))]
