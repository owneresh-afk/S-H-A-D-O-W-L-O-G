import threading
from flask import Flask, jsonify
import config

app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "bot": "CC Generator Bot", "version": "1.0.0"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200


def run_flask():
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=False, use_reloader=False)


def start_health_server():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    return t
