from typing import assert_never
from collections import OrderedDict


class Bencode:
    """
        Bencode encoder/decoder
        Docs https://en.wikipedia.org/wiki/Bencode
    """

    @classmethod
    def decode(cls, bencoded_value: any):
        if not isinstance(bencoded_value, bytearray):
            bencoded_value = bytearray(bencoded_value)

        match chr(bencoded_value[0]):
            case d if d.isdigit():
                return cls.__decode_string(bencoded_value)
            case "i":
                return cls.__decode_int(bencoded_value)
            case "l":
                return cls.__decode_list(bencoded_value)
            case "d":
                return cls.__decode_dict(bencoded_value)

        assert_never()

    @classmethod
    def encode(self, data: any) -> bytes:
        match data:
            case int():
                return f"i{data}e".encode()
            case str():
                return f"{len(data)}:{data}".encode()
            case bytes():
                return f"{len(data)}:".encode() + data
            case list():
                return b"l" + b"".join(self.encode(val) for val in data) + b"e"
            case dict():
                return (
                        b"d"
                        + b"".join(
                    self.encode(key) + self.encode(val) for key, val in data.items()
                )
                        + b"e"
                )

        assert_never()

    @classmethod
    def __decode_string(cls, bencoded_value: bytearray):
        length, value = bencoded_value.split(b":", maxsplit=1)
        value = bytes(value[:int(length)])
        for _ in range(len(value) + len(length) + 1):
            bencoded_value.pop(0)
        try:
            return value.decode()
        except UnicodeDecodeError:
            return value

    @classmethod
    def __decode_int(cls, bencoded_value: bytearray):
        value = bytearray()
        bencoded_value.pop(0)
        while (b := bencoded_value.pop(0)) and chr(b) != "e":
            value.append(b)
        return int(value)

    @classmethod
    def __decode_list(cls, bencoded_value: bytearray):
        value = OrderedDict()
        bencoded_value.pop(0)
        while chr(bencoded_value[0]) != "e":
            value.append(cls.decode(bencoded_value))
        bencoded_value.pop(0)  # remove trailing e
        return value

    @classmethod
    def __decode_dict(cls, bencoded_value: bytearray):
        value = {}
        bencoded_value.pop(0)
        while chr(bencoded_value[0]) != "e":
            k = cls.decode(bencoded_value)
            v = cls.decode(bencoded_value)

            value[k] = v
        bencoded_value.pop(0)  # remove trailing e
        return value


def do_tests():
    assert Bencode.decode(b"i42e") == 42
    assert Bencode.decode(b"i-42e") == -42
    assert Bencode.decode(b"13:Hello, world!") == "Hello, world!"
    assert Bencode.decode(b"li1ei2ei3ee") == [1, 2, 3]
    assert Bencode.decode(b"l1:a1:b1:c1:de") == ["a", "b", "c", "d"]
    assert Bencode.decode(b"lli1ei2ei3eel1:a1:b1:c1:dee") == [[1, 2, 3], ["a", "b", "c", "d"]]
    assert Bencode.decode(b"d3:bar4:spam3:fooi42ee") == {"bar": "spam", "foo": 42}

    assert Bencode.encode(42) == b"i42e"
    assert Bencode.encode(-42) == b"i-42e"
    assert Bencode.encode("Hello, world!") == b"13:Hello, world!"
    assert Bencode.encode([1, 2, 3]) == b"li1ei2ei3ee"
    assert Bencode.encode(["a", "b", "c", "d"]) == b"l1:a1:b1:c1:de"
    assert Bencode.encode([[1, 2, 3], ["a", "b", "c", "d"]]) == b"lli1ei2ei3eel1:a1:b1:c1:dee"
    assert Bencode.encode({"bar": "spam", "foo": 42}) == b"d3:bar4:spam3:fooi42ee"


if __name__ == "__main__":
    do_tests()
