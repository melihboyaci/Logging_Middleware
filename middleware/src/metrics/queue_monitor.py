from __future__ import annotations

import base64
import json
from urllib.error import URLError
from urllib.request import Request, urlopen


def fetch_queue_depth(
    queue_name: str,
    *,
    mgmt_url: str = "http://127.0.0.1:15672",
    vhost: str = "%2F",
    username: str = "guest",
    password: str = "guest",
    timeout: float = 5.0,
) -> int:
    url = f"{mgmt_url.rstrip('/')}/api/queues/{vhost}/{queue_name}"
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request = Request(url, headers={"Authorization": f"Basic {token}"})

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch queue stats from {url}: {exc}") from exc

    messages = payload.get("messages")
    if isinstance(messages, int):
        return messages
    return int(payload.get("messages_ready", 0) or 0)
