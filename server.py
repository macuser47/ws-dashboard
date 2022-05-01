"""
Implement a service that provies a JSON-RPC API to localhost applications that allows them to 
publish key-value pairs to be viewed in a web dashboard served by this service.
"""
import flask
from flask_sock import Sock
import jsonrpcserver
import socket
import json
import threading
import struct
import argparse
from contextlib import suppress

app = flask.Flask(__name__)
sock = Sock(app)

kv_store = {}
update_sem = threading.BoundedSemaphore(1)
update_sem.acquire()


@app.route("/")
def index():
    return flask.render_template("index.html")


@sock.route("/")
def ws_handle(ws):
    """Send key-value pairs to the client."""
    ws.send(json.dumps(kv_store))
    while True:
        update_sem.acquire()
        ws.send(json.dumps(kv_store))


@jsonrpcserver.method
def publish(key, value):
    kv_store[key] = value
    with suppress(ValueError):
        update_sem.release()
    return jsonrpcserver.Success()


def rpc_main(rpc_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", rpc_port))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        threading.Thread(target=rpc_handle, args=(conn,), daemon=True).start()


def rpc_handle(conn):
    while True:
        size = struct.unpack("!I", conn.recv(4))[0]
        if response := jsonrpcserver.dispatch(conn.recv(size)):
            conn.send(response.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ws-dashboard server")
    parser.add_argument(
        "--web-port", type=int, default=5000, help="Port to run the webserver on"
    )
    parser.add_argument(
        "--rpc-port", type=int, default=5001, help="Port to run the JSON-RPC server on"
    )
    args = parser.parse_args()

    threading.Thread(target=rpc_main, args=(args.rpc_port,), daemon=True).start()
    app.run(host="0.0.0.0", port=args.web_port)
