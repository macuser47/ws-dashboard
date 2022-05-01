import jsonrpcclient
import socket
import time
import math
import struct
import json

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 5001))
    start_time = time.time()
    while True:
        t = time.time() - start_time
        msg = json.dumps(
            jsonrpcclient.request(
                "publish", params=["test", math.sin(2 * 3.14 * 0.2 * t)]
            )
        )
        print(msg)
        s.send(struct.pack("!I", len(msg)))
        s.send(msg.encode())
        print(json.loads(s.recv(1024)))
