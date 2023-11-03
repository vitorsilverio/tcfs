from socket import socket, AF_INET, SOCK_STREAM
import struct
from typing import Self

from messages import Handshake, build_message, GenericMessage


class PeerConnection:

    def __init__(self, ip: str, port: int):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__ip = ip
        self.__port = port

    def __enter__(self) -> Self:
        self.__socket.connect((self.__ip, self.__port))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__socket.close()

    def handshake(self, handshake: Handshake) -> bytes:
        self.__socket.send(bytes(handshake))
        return self.__read_buffer(68)

    def __read_buffer(self, buffer_size):
        buffer = bytearray()
        while remaining := buffer_size - len(buffer):
            buffer.extend(self.__socket.recv(remaining))
        return buffer

    def read_message(self) -> GenericMessage:
        buffer = self.__read_buffer(4)
        message_length = int(struct.unpack(">I", buffer)[0])
        data = self.__read_buffer(message_length)
        return build_message(data)

    def send_message(self, message: GenericMessage) -> None:
        self.__socket.send(bytes(message))
