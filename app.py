from flask import Flask, jsonify
from contextlib import closing
from socket import *
from time import time
from concurrent.futures import ThreadPoolExecutor
import atexit

app = Flask(__name__)

def find_free_port():
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        return s.getsockname()[1]

def accept_socket(s):
    s.settimeout(3)
    try:
        _, addr = s.accept()
        return addr[0]
    except:
        return ""

threads = {}
executor = ThreadPoolExecutor(10)
atexit.register(lambda: executor.shutdown())

@app.route("/set/<key>")
def listen(key):
    port = find_free_port()

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    
    threads[key] = { "start": int(time()), "future": executor.submit(accept_socket, s) }
    return jsonify({ "port": port })

@app.route("/get/<key>")
def get_result(key):
    if key not in threads:
        return jsonify({ "code": -1, "result": "key not exists" })

    future = threads[key]["future"]
    if future.done():
        result = future.result()
        return jsonify({ "code": 0, "result": result })
    elif future.cancelled():
        return jsonify({ "code": -1, "result": "future timout" })

    return jsonify({ "code": -1, "result": "still running..." })

app.run(host="0.0.0.0", port=9712)
