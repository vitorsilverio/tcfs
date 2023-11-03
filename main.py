import requests

from bencode import Bencode
from client import PeerConnection
from messages import Handshake, BitFieldMessage, InterestedMessage, RequestMessage
from torrent import load_torrent
from tracker import TrackerResponse
from hashlib import sha1

TORRENT_CLIENT_PEER_ID = b"tcfs 1.0            "

if __name__ == '__main__':
    torrent = load_torrent(r"E:\FONTES_APP_DOCS\codecrafters\codecrafters-bittorrent-python\sample.torrent")
    print(torrent)

    response = requests.get(torrent.announce, params={
        "info_hash": torrent.info.hash.digest(),
        "peer_id": TORRENT_CLIENT_PEER_ID.decode(),
        "port": 6882,
        "uploaded": 0,
        "downloaded": 0,
        "left": torrent.info.length,
        "compact": 1
    })
    tracker_response = TrackerResponse(Bencode.decode(response.content))
    print(f"{tracker_response=}")

    with open(torrent.info.name, "wb") as f:

        with PeerConnection(tracker_response.peers[1].ip, tracker_response.peers[1].port) as connection:
            response = connection.handshake(Handshake(torrent.info.hash.digest(), TORRENT_CLIENT_PEER_ID))
            print(response)

            message = connection.read_message()
            print(message)

            assert isinstance(message, BitFieldMessage)  # Must be the first message

            interested = InterestedMessage()
            print(interested)
            connection.send_message(interested)
            message = connection.read_message()
            print(message)
            block_len = 2 ** 14
            length = block_len
            for piece in range(len(torrent.info.pieces)):
                piece_data = bytearray()
                for block in range(torrent.info.piece_length // block_len):
                    downloaded = (torrent.info.piece_length * piece) + (block * block_len)
                    if torrent.info.length - downloaded < block_len:
                        length = torrent.info.length - downloaded
                    request = RequestMessage(index=piece, begin=block * block_len, length=length)
                    print(request)
                    connection.send_message(request)
                    message = connection.read_message()
                    print(message)
                    if message:
                        piece_data.extend(message.content)
                piece_hash = sha1(piece_data).hexdigest()
                assert piece_hash == torrent.info.pieces[piece]
                f.write(piece_data)


