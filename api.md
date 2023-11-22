接口文档

## 函数定义
```python
def step(data: dict) -> list[ActionType]:
```
**说明**：当 client 收到一个数据包，将其解码后立即并发调用 step 函数确定行动。

## 参数说明

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| player_id | int | 玩家id |
| round | int | 当前回合 |
| map | list[list[int]]（二维数组[x][y]） | 地图，只包含方格的类型 |
| players | list[dict] | 场上所有玩家 |
| bombs | list[dict] | 场上所有~~蹦蹦~~炸弹 |
| items | list[list[int]] | 场上所有道具（坐标同`map`）|

---
### `map`
```python
class BlockType(Enum):
    EMPTY = 0
    BLOCK = 1  # 任何挡路的东西
    BOX = 2  # 可破坏的墙
    BOMB = 4
    ITEM = 8
    PLAYER = 16
```
竖向为x，横向为y
**相关函数**
`BlockType.{EMPTY|BLOCK|BOX|BOMB|ITEM|PLAYER}.match(block_type: int)`

BlockType.BLOCK 指任何阻挡玩家移动的物体，同时也是阻挡炸弹的物体（包括炸弹本身）
那么，当该方格为 炸弹/可破坏墙 时，`BlockType.BLOCK.match(block_type) == True`
特别的，当且仅当`block_type == 0` 时 `BlockType.EMPTY.match(block_type) == True`

---
### `players[index]`
| 名称 | 类型 | 说明 |
| --- | --- | --- |
| x | int | 坐标x |
| y | int | 坐标y |
| player_id | int | 玩家id |
| alive | bool | 是否存活 |
| hp | int | 血量(上限为3) |
| shield_time | int | 护盾剩余回合数 |
| invincible_time | int | 无敌回合数 |
| score | int | 当前分数 |
| bomb_range | int | 炸弹爆炸范围 |
| bomb_max_num | int | 炸弹数量上限 |
| bomb_now_num | int | 当前剩余炸弹 |
| speed | int | 玩家的移动速度(每回合行动数) |

---
### `bombs[index]`
| 名称 | 类型 | 说明 |
| --- | --- | --- |
| x | int | 坐标x |
| y | int | 坐标y |
| round | int | 存续时间 |
| bomb_id | int | 炸弹 id |
| bomb_range | int | 炸弹范围 |
| player_id | int | 炸弹放置者 |

---
### `items[x][y]`
```py
class ItemType(JsonIntEnum):
    NO_POTION = 0  # 无药水
    BOMB_RANGE = 1  # 炸弹范围增大
    BOMB_NUM = 2  # 炸弹数量增加
    HP = 3  # 血量增加
    INVINCIBLE = 4  # 无敌
    SHIELD = 5  # 护盾

## 提示
### 如何调用 dict 内的数据？
dict （字典）组成为
```python
	{
		"key1" : value1,
		"key2" : value2,
		...
	}
```
这样的`key-value`组合称为“**键值对**”。
可以通过`value = a_dict["key"/vars]` （其中vars == "key"）调用

同时， python 也有非常好用的`for...in`语句遍历 dict ：
```python
for key in a_dict:
	value = a_dict[key]
	...
# or
for key, value in a_dict.items():
	...
```

### 如何判断某方格的类型
`BlockType.{TYPE}.match(map[x][y])` 返回 bool 值