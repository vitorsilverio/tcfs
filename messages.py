import struct


class Handshake:

    def __init__(self, torrent_hash: bytes, peer_id: bytes):
        self.torrent_hash = torrent_hash
        self.peer_id = peer_id

    def __bytes__(self) -> bytes:
        handshake = b"\x13"
        handshake += b"BitTorrent protocol"
        handshake += struct.pack(">Q", 0)
        handshake += self.torrent_hash
        handshake += self.peer_id
        return handshake


class GenericMessage:

    def __init__(self, message_type: bytes, raw_payload: bytes):
        self.__message_type = message_type
        self._raw_payload = raw_payload

    def __len__(self):
        return len(self._raw_payload) + 1

    def __bytes__(self) -> bytes:
        message = struct.pack(">I", self.__len__())
        message += self.__message_type
        message += self._raw_payload
        return message

    @property
    def payload(self):
        return self._raw_payload

    def __repr__(self):
        return f"""
            Message: {self.__class__.__name__}
            Length: {self.__len__()}
            Payload: {self.payload}
        """


class ChokeMessage(GenericMessage):

    def __init__(self):
        super().__init__(message_type=b"\x00", raw_payload=b"")


class UnchokeMessage(GenericMessage):

    def __init__(self):
        super().__init__(message_type=b"\x01", raw_payload=b"")


class InterestedMessage(GenericMessage):

    def __init__(self):
        super().__init__(message_type=b"\x02", raw_payload=b"")


class NotInterestedMessage(GenericMessage):

    def __init__(self):
        super().__init__(message_type=b"\x03", raw_payload=b"")


class HaveMessage(GenericMessage):

    def __init__(self, *, payload: bytes | None = None, index: bytes | None = None):
        if not payload:
            payload = struct.pack(">i", index)
        super().__init__(message_type=b"\x04", raw_payload=payload)


class BitFieldMessage(GenericMessage):

    def __init__(self, *, payload: bytes | None = None):
        super().__init__(message_type=b"\x05", raw_payload=payload)

    @property
    def packages(self):
        packages = []
        for i in range(len(self._raw_payload)):
            for j in range(8):
                if (self._raw_payload[i] >> (7 - j)) & 1:
                    packages.append(8 * i + j)
        return packages

    def __repr__(self):
        return f"""
            {super().__repr__()}\tpackages: {self.packages}
        """


class RequestMessage(GenericMessage):

    def __init__(self, *, payload: bytes | None = None, index: int | None = None, begin: int | None = None,
                 length: int | None = None):
        if not payload:
            payload = bytearray()
            payload.extend(struct.pack(">i", index))
            payload.extend(struct.pack(">i", begin))
            payload.extend(struct.pack(">i", length))
            payload = bytes(payload)
        super().__init__(message_type=b"\x06", raw_payload=payload)


class PieceMessage(GenericMessage):

    def __init__(self, *, payload: bytes | None = None):
        super().__init__(message_type=b"\x07", raw_payload=payload)

    @property
    def content(self):
        return self._raw_payload[8:]


class CancelMessage(GenericMessage):

    def __init__(self, *, payload: bytes | None = None, index: int | None = None, begin: int | None = None,
                 length: int | None = None):
        if not payload:
            payload = bytearray()
            payload.extend(struct.pack(">i", index))
            payload.extend(struct.pack(">i", begin))
            payload.extend(struct.pack(">i", length))
            payload = bytes(payload)
        super().__init__(message_type=b"\x08", raw_payload=payload)


def build_message(data: bytes) -> GenericMessage:
    if not len(data):
        return None

    match data[0]:
        case 0:
            return ChokeMessage()
        case 1:
            return UnchokeMessage()
        case 2:
            return InterestedMessage()
        case 3:
            return NotInterestedMessage()
        case 4:
            return HaveMessage(payload=data[1:])
        case 5:
            return BitFieldMessage(payload=data[1:])
        case 6:
            return RequestMessage(payload=data[1:])
        case 7:
            return PieceMessage(payload=data[1:])
        case 8:
            return CancelMessage(payload=data[1:])

    if len(data) == 1:
        return GenericMessage(data[0], bytes())

    return GenericMessage(data[0], data[1:])
