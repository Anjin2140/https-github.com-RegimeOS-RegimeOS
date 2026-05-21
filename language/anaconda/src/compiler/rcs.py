# rcs.py
# Project ANACONDA Regime Canonical Serialization v1.0
# Classification: BLACK PROJECT // SOVEREIGN

import struct
import hashlib
from typing import Any
from src.kernel.regime_math import Ternary, RegimeDecimal

TAG_INT = 0x01
TAG_STR = 0x02
TAG_BYTES = 0x03
TAG_LIST = 0x04
TAG_DICT = 0x05
TAG_TERNARY = 0x06
TAG_REGIME = 0x07

def _serialize_value(val: Any) -> tuple[int, bytes]:
    """
    Serializes a value without the outer Type/Length tags.
    Returns (tag, data_bytes).
    """
    if isinstance(val, bool):
        # Transpile bools to Ternary first to maintain type rules
        val = Ternary(1 if val else -1)

    if isinstance(val, int):
        # 8-byte big-endian signed integer
        return TAG_INT, struct.pack(">q", val)

    elif isinstance(val, str):
        data = val.encode('utf-8')
        return TAG_STR, data

    elif isinstance(val, bytes):
        return TAG_BYTES, val

    elif isinstance(val, list) or isinstance(val, tuple):
        # [4 bytes length][elements...]
        elements_bytes = bytearray()
        for item in val:
            elements_bytes.extend(serialize(item))
        return TAG_LIST, struct.pack(">I", len(val)) + bytes(elements_bytes)

    elif isinstance(val, dict):
        # Dict serialization MUST sort keys alphabetically for determinism.
        sorted_keys = sorted(val.keys())
        pairs_bytes = bytearray()
        for k in sorted_keys:
            pairs_bytes.extend(serialize(k))
            pairs_bytes.extend(serialize(val[k]))
        return TAG_DICT, struct.pack(">I", len(val)) + bytes(pairs_bytes)

    elif isinstance(val, Ternary):
        # 1-byte data: 0->0, 1->1, -1->2
        state_byte = 0
        if val.value == 1:
            state_byte = 1
        elif val.value == -1:
            state_byte = 2
        return TAG_TERNARY, bytes([state_byte])

    elif isinstance(val, RegimeDecimal):
        # Sign (1 byte: 0->0, 1->1, -1->2)
        # Exponent (4 bytes signed big-endian)
        # Length of chunks (2 bytes big-endian)
        # Chunks (N * 2 bytes big-endian uint16)
        sign_byte = 0
        if val.sign == 1:
            sign_byte = 1
        elif val.sign == -1:
            sign_byte = 2

        header = struct.pack(">BiH", sign_byte, val.exponent, len(val.chunks))
        chunks_bytes = bytearray()
        for chunk in val.chunks:
            chunks_bytes.extend(struct.pack(">H", chunk))
        return TAG_REGIME, header + bytes(chunks_bytes)

    else:
        raise TypeError(f"RCS: Unsupported type for serialization: {type(val)}")

def serialize(val: Any) -> bytes:
    """
    Serializes value to RCS format: [Type_Tag (1B)][Length (4B)][Data][SHA-384 Hash (48B)]
    """
    tag, data = _serialize_value(val)
    length = len(data)
    header = struct.pack(">BI", tag, length)
    payload = header + data
    h = hashlib.sha384(payload).digest()
    return payload + h

def deserialize(b: bytes) -> tuple[Any, int]:
    """
    Deserializes from RCS format bytes.
    Returns (deserialized_value, total_bytes_read).
    """
    if len(b) < 53: # 1B tag + 4B length + 48B hash
        raise ValueError("RCS: Payload too short")

    tag, length = struct.unpack(">BI", b[0:5])
    total_len = 5 + length + 48
    if len(b) < total_len:
        raise ValueError(f"RCS: Incomplete payload, expected {total_len} bytes")

    payload = b[0 : 5 + length]
    expected_hash = b[5 + length : total_len]
    actual_hash = hashlib.sha384(payload).digest()

    if expected_hash != actual_hash:
        raise ValueError("RCS: Integrity violation! SHA-384 hash mismatch.")

    data = b[5 : 5 + length]

    if tag == TAG_INT:
        return struct.unpack(">q", data)[0], total_len

    elif tag == TAG_STR:
        return data.decode('utf-8'), total_len

    elif tag == TAG_BYTES:
        return data, total_len

    elif tag == TAG_LIST:
        elem_count = struct.unpack(">I", data[0:4])[0]
        offset = 4
        elements = []
        for _ in range(elem_count):
            item, read_len = deserialize(data[offset:])
            elements.append(item)
            offset += read_len
        return elements, total_len

    elif tag == TAG_DICT:
        pair_count = struct.unpack(">I", data[0:4])[0]
        offset = 4
        d = {}
        for _ in range(pair_count):
            key, read_len = deserialize(data[offset:])
            offset += read_len
            val, read_len = deserialize(data[offset:])
            offset += read_len
            d[key] = val
        return d, total_len

    elif tag == TAG_TERNARY:
        state_byte = data[0]
        if state_byte == 1:
            return Ternary(1), total_len
        elif state_byte == 2:
            return Ternary(-1), total_len
        return Ternary(0), total_len

    elif tag == TAG_REGIME:
        sign_byte, exponent, chunk_count = struct.unpack(">BiH", data[0:7])
        sign = 0
        if sign_byte == 1:
            sign = 1
        elif sign_byte == 2:
            sign = -1

        chunks = []
        offset = 7
        for _ in range(chunk_count):
            chunk = struct.unpack(">H", data[offset : offset + 2])[0]
            chunks.append(chunk)
            offset += 2
        return RegimeDecimal(sign, exponent, chunks), total_len

    else:
        raise ValueError(f"RCS: Unknown type tag {tag}")
