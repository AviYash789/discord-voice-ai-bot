import os
from flask import Flask, jsonify
from flask_cors import CORS
import stats
from key_rotator import KeyRotator

app = Flask(__name__)
CORS(app)

_rotator: KeyRotator = None


def set_rotator(r: KeyRotator):
    global _rotator
    _rotator = r


@app.route("/api/bot/stats")
def bot_stats():
    data = stats.get_stats()
    data["current_key_masked"] = _rotator.current_masked() if _rotator else "N/A"
    data["total_keys"] = _rotator.total() if _rotator else 0
    return jsonify(data)


def run_dashboard(port: int = None):
    if port is None:
        port = int(os.environ.get("DASHBOARD_PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
