from base import JsonIntEnum
from req import ActionType
from config import config
from resp import ObjType, ActionResp


class BlockType(JsonIntEnum):
    EMPTY = 0
    BLOCK = 1  # 任何挡路的东西
    BOX = 2  # 可破坏的墙
    BOMB = 4
    ITEM = 8
    PLAYER = 16


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


def packetDecode(recv_data: ActionResp, player_id) -> dict:
    data = {"player_id": recv_data.player_id, "round": recv_data.round,
            "map": [[0 for _ in range(config.get("map_size"))] for _ in range(config.get("map_size"))],
            "player": [],
            "bomb": [],
            "item": [[0 for _ in range(config.get("map_size"))] for _ in range(config.get("map_size"))],
            }

    for block in recv_data.map:
        block_type = 0
        if len(block.objs) != 0:
            for obj in block.objs:
                obj_property = obj.property.to_json()
                if obj.type == ObjType.Block:
                    block_type |= BlockType.BLOCK  # 墙肯定是挡路的
                    if obj_property.removable:
                        block_type |= BlockType.BOX
                elif obj.type == ObjType.Player:
                    block_type |= BlockType.PLAYER
                    obj_property["x"] = block.x
                    obj_property["y"] = block.y
                    data["player"].append(obj_property)
                elif obj.type == ObjType.Bomb:
                    block_type |= BlockType.BOMB
                    block_type |= BlockType.BLOCK  # 炸弹也是挡路的
                    data["bomb"].append(bombDecode(data["round"], block, obj_property))
                elif obj.type == ObjType.Item:
                    block_type |= BlockType.ITEM
                    data["item"][block.x][block.y] = obj_property.item_type
                else:
                    raise Exception("unknown obj type")

        data["map"][block.x][block.y] = block_type
    return data


def clone_map(map: list[list[int]]):
    """in case of modifying the map"""
    return [[map[x][y] for y in range(len(map[x]))] for x in range(len(map))]


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
    actions = []

    pass
    return actions
