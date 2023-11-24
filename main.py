import json
import socket
import time
from threading import Thread
from time import sleep

import bot
import bot_base
from req import *
from resp import *
from config import config
from logger import logger
import sys


class Client(object):
    """Client obj that send/recv packet.
    """

    def __init__(self) -> None:
        self.config = config
        self.host = self.config.get("host")
        self.port = self.config.get("port")
        assert self.host and self.port, "host and port must be provided"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected = False

    def connect(self):
        if self.socket.connect_ex((self.host, self.port)) == 0:
            logger.info(f"connect to {self.host}:{self.port}")
            self._connected = True
        else:
            logger.error(f"can not connect to {self.host}:{self.port}")
            exit(-1)
        return

    def send(self, req: PacketReq):
        msg = json.dumps(req, cls=JsonEncoder).encode("utf-8")
        length = len(msg)
        self.socket.sendall(length.to_bytes(8, sys.byteorder) + msg)
        # uncomment this will show req packet
        # logger.info(f"send PacketReq, content: {msg}")
        return

    def recv(self):
        length = int.from_bytes(self.socket.recv(8), sys.byteorder)
        result = b""
        while resp := self.socket.recv(length):
            result += resp
            length -= len(resp)
            if length <= 0:
                break

        # uncomment this will show resp packet
        # logger.info(f"recv PacketResp, content: {result}")
        packet = PacketResp().from_json(result)
        return packet

    def __enter__(self):
        return self

    def close(self):
        logger.info("closing socket")
        self.socket.close()
        logger.info("socket closed successfully")
        self._connected = False

    @property
    def connected(self):
        return self._connected

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        if traceback:
            print(traceback)
            return False
        return True


def recvAndResp(cli: Client, player_id: int, round: int, map: list[list[dict]], players: list[dict], bombs: list[dict], items: list[list[dict]]):
    stime = time.time_ns()
    actions = bot.game_update(player_id, round, map, players, bombs, items)
    if actions:
        print(f"round {round}, actions: {actions}")
    etime = time.time_ns()

    if (etime - stime) < 1e6 * config.get("round_interval_value"):
        action_req = PacketReq(PacketType.ActionReq,
                               [ActionReq(player_id, action) for action in actions])
        cli.send(action_req)
    else:
        logger.error(f"round {round} timeout: {(etime - stime) / 1e6}ms")
        print(f"round {round} timeout: {(etime - stime) / 1e6}ms")


def botPlay():
    player_id = -1
    with Client() as cli:
        cli.connect()

        init_req = PacketReq(PacketType.InitReq, InitReq(config.get("player_name")))
        cli.send(init_req)

        packet_resp = cli.recv()
        if packet_resp.type == PacketType.ActionResp:
            player_id = packet_resp.data.player_id
            logger.info(f"player_id: {player_id}")
            print(f"player_id: {player_id}")
        else:
            logger.error("init failed")
            exit(-1)

        data = bot_base.packetDecode(packet_resp.data, player_id)
        round = data["round"]
        map = data["map"]
        players = data["players"]
        bombs = data["bombs"]
        items = data["items"]
        bot.game_init(player_id, round, map, players, bombs, items)

        while True:
            if packet_resp.type == PacketType.ActionResp:
                data = bot_base.packetDecode(packet_resp.data, player_id)
                round = data["round"]
                map = data["map"]
                players = data["players"]
                bombs = data["bombs"]
                items = data["items"]

                t = Thread(target=recvAndResp, args=(cli, player_id, round, map, players, bombs, items))
                t.start()
            elif packet_resp.type == PacketType.GameOver:
                logger.info("game over")
                break

            packet_resp = cli.recv()

        if player_id in packet_resp.data.winner_ids:
            logger.info("you win")
        else:
            logger.info("you lose")
        logger.info(packet_resp.data)
        print(packet_resp.data)


if __name__ == "__main__":
    botPlay()
