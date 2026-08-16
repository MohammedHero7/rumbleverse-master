from flask import Flask, request, jsonify
import time
import uuid
import threading

app = Flask(__name__)

servers = {}
lock = threading.Lock()

SERVER_TIMEOUT = 30  # seconds


def cleanup_servers():
    """Remove servers that stopped sending heartbeats."""
    while True:
        now = time.time()
        with lock:
            expired = [
                server_id
                for server_id, server in servers.items()
                if now - server["last_heartbeat"] > SERVER_TIMEOUT
            ]
            for server_id in expired:
                print(f"Removing expired server {server_id}")
                del servers[server_id]

        time.sleep(5)


cleanup_thread = threading.Thread(target=cleanup_servers, daemon=True)
cleanup_thread.start()


@app.route("/")
def index():
    return jsonify({
        "name": "Rumbleverse Master Server",
        "status": "online",
        "server_count": len(servers)
    })


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)

    required = ["name", "ip", "port"]

    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}"
            }), 400

    server_id = str(uuid.uuid4())

    server = {
        "id": server_id,
        "name": data["name"],
        "ip": data["ip"],
        "port": int(data["port"]),
        "players": int(data.get("players", 0)),
        "max_players": int(data.get("max_players", 45)),
        "game_mode": int(data.get("game_mode", 1)),
        "map": data.get("map", "Playground"),
        "last_heartbeat": time.time()
    }

    with lock:
        servers[server_id] = server

    print(f"Registered server {server['name']} ({server_id})")

    return jsonify({
        "success": True,
        "server_id": server_id
    })


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json(force=True)

    server_id = data.get("server_id")

    if not server_id:
        return jsonify({
            "success": False,
            "error": "Missing server_id"
        }), 400

    with lock:
        server = servers.get(server_id)

        if not server:
            return jsonify({
                "success": False,
                "error": "Unknown server"
            }), 404

        server["last_heartbeat"] = time.time()

        if "players" in data:
            server["players"] = int(data["players"])

    return jsonify({
        "success": True
    })


@app.route("/servers", methods=["GET"])
def get_servers():
    now = time.time()

    with lock:
        result = []

        for server in servers.values():
            if now - server["last_heartbeat"] <= SERVER_TIMEOUT:
                result.append({
                    "id": server["id"],
                    "name": server["name"],
                    "ip": server["ip"],
                    "port": server["port"],
                    "players": server["players"],
                    "max_players": server["max_players"],
                    "game_mode": server["game_mode"],
                    "map": server["map"]
                })

    return jsonify(result)


@app.route("/unregister", methods=["POST"])
def unregister():
    data = request.get_json(force=True)

    server_id = data.get("server_id")

    if not server_id:
        return jsonify({
            "success": False,
            "error": "Missing server_id"
        }), 400

    with lock:
        if server_id in servers:
            del servers[server_id]
            print(f"Unregistered server {server_id}")

    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)