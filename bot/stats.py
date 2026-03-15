import threading

_lock = threading.Lock()

_stats = {
    "total_requests": 0,
    "active_channel": None,
    "bot_status": "offline",
}


def set_status(status: str):
    with _lock:
        _stats["bot_status"] = status


def set_channel(channel_name):
    with _lock:
        _stats["active_channel"] = channel_name


def increment_requests():
    with _lock:
        _stats["total_requests"] += 1


def get_stats():
    with _lock:
        return dict(_stats)
