from bencode import Bencode
from hashlib import sha1


class File:

    def __init__(self, file_dict: dict):
        self.length = file_dict["length"]
        self.path = file_dict["path"]

    def __repr__(self):
        return f"""
                   Length: {self.length}
                   Path: {self.path}
               """


class Info:

    def __init__(self, info_dict: dict):
        self.name = info_dict["name"]
        self.piece_length = info_dict["piece length"]
        self.__pieces = info_dict["pieces"]
        self.hash = sha1(Bencode.encode(info_dict))
        if "length" in info_dict:
            self.length = info_dict["length"]
            self.files = None
        else:
            self.files = [File(f) for f in info_dict["files"]]
            self.length = None

    @property
    def pieces(self):
        pieces = self.__pieces.hex()
        return [
            pieces[n:n + 40] for n in range(0, len(pieces), 40)
        ]

    def __repr__(self):
        return f"""
            Length: {self.length}
            Name: {self.name}
            Piece Length: {self.piece_length}
            Pieces: {self.pieces}
            Hash: {self.hash.hexdigest()}
            Files: {self.files}
        """


class Torrent:

    def __init__(self, torrent_dict: dict):
        self.announce = torrent_dict["announce"]
        self.info = Info(torrent_dict["info"])

    def __repr__(self):
        return f"""
               Announce: {self.announce}
               Info: {self.info}
           """


def load_torrent(path) -> Torrent:
    with open(path, "rb") as f:
        return Torrent(Bencode.decode(f.read()))
