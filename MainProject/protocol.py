import struct
import json
from config import *


def package(send_dict: dict) -> bytes:
    body = json.dumps(send_dict)
    header = len(body)
    header_pack = struct.pack('1I', header)
    if DEBUG:
        print(header)
    return header_pack + body.encode(encoding='utf-8')
