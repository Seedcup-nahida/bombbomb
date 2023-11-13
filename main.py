import json
import socket
from threading import Thread
from time import sleep

import bot
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


def recvAndRefresh(cli: Client):
    global gContext
    resp = cli.recv()

    if resp.type == PacketType.ActionResp:
        gContext["gameBeginFlag"] = True
        gContext["playerID"] = resp.data.player_id

    while resp.type != PacketType.GameOver:
        gContext["recvData"] = resp.data
        resp = cli.recv()
        # print("recv packet")

    gContext["gameOverFlag"] = True
    print(f"Final scores \33[1m{resp.data.scores}\33[0m")
    logger.info(f"Final scores {resp.data.scores}")

    if gContext["playerID"] in resp.data.winner_ids:
        print("win!")
        logger.info("win!")
    else:
        print(f"lost! The winner is {resp.data.winner_ids}")
        logger.info(f"lost! The winner is {resp.data.winner_ids}")


def botPlay():
    """This is just for bot play, not for human play."""
    with Client as cli:
        cli.connect()

        init_packet = PacketReq(PacketType.InitReq, InitReq(config.get("player_name")))
        cli.send(init_packet)

        t = Thread(target=recvAndRefresh, args=(cli,))
        t.start()

        print("Waiting for the other player to connect...")
        logger.info("Waiting for the other player to connect...")
        while not gContext["gameBeginFlag"]:
            sleep(0.1)

        print("Game begin!")
        logger.info("Game begin!")

        has_updated = False
        step = 0
        while not gContext["gameOverFlag"]:
            # TODO: bot play
            recv_data = gContext["recvData"]
            if has_updated:
                step = 0
            if step >= config.get("player_speed"):
                sleep(0.01)
                if recv_data != gContext["recvData"]:
                    has_updated = True
                continue

            action = bot.step(bot.packetDecode(recv_data, gContext["playerID"]), has_updated)
            step += 1

            if gContext["gameOverFlag"]:
                break
            action_packet = PacketReq(PacketType.ActionReq, ActionReq(gContext["playerID"], action))
            cli.send(action_packet)
            has_updated = recv_data == gContext["recvData"]

        print("Game Over!")
        logger.info("Game Over!")


if __name__ == "__main__":
    botPlay()
