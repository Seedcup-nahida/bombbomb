import json
import socket
from threading import Thread
from time import sleep

import bot_base
from req import *
from resp import *
from config import config
from logger import logger
import sys

gContext = {
    "playerID": -1,
    "gameOverFlag": False,
    "gameBeginFlag": False,
    "recvData": ActionResp(),
}


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
        logger.info(f"recv PacketResp, content: {result}")
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


def botPlay():
    """This is just for bot play, not for human play."""
    with Client() as cli:
        cli.connect()

        init_packet = PacketReq(PacketType.InitReq, InitReq(config.get("player_name")))
        cli.send(init_packet)
        print("Waiting for the other player to connect...")
        logger.info("Waiting for the other player to connect...")

        resp = cli.recv()

        if resp.type == PacketType.ActionResp:
            gContext["gameBeginFlag"] = True
            gContext["playerID"] = resp.data.player_id
            print(f"Game begin! You are player {gContext['playerID']}")
            logger.info(f"Game begin! You are player {gContext['playerID']}")

        # TODO
        while resp.type != PacketType.GameOver:
            gContext["recvData"] = resp.data
            actions = bot.step(bot.packetDecode(resp.data, gContext["playerID"]))
            action_packet = PacketReq(PacketType.ActionReq,
                                      [ActionReq(gContext["playerID"], action) for action in actions])
            cli.send(action_packet)
            resp = cli.recv()
            # print("recv packet")

        gContext["gameOverFlag"] = True
        print(f"Final scores {resp.data.scores}")
        logger.info(f"Final scores {resp.data.scores}")

        if gContext["playerID"] in resp.data.winner_ids:
            print("win!")
            logger.info("win!")
        else:
            print(f"lost! The winner is {resp.data.winner_ids}")
            logger.info(f"lost! The winner is {resp.data.winner_ids}")


if __name__ == "__main__":
    botPlay()
