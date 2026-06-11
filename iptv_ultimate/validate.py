from __future__ import annotations

import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

from .playlist import Channel


def validate_channel(channel: Channel, timeout: int = 10) -> Channel:
    start = time.perf_counter()
    channel.valid = False
    channel.error = ""
    headers = {"User-Agent": "IPTV-Ultimate/0.1"}

    try:
        request = urllib.request.Request(channel.url, method="HEAD", headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            channel.status_code = response.getcode()
            channel.content_type = response.headers.get("Content-Type", "")
            if response.getcode() < 400:
                channel.valid = True
    except urllib.error.HTTPError as exc:
        channel.status_code = exc.code
        channel.content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        if exc.code < 500:
            try:
                request = urllib.request.Request(channel.url, headers=headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    response.read(8192)
                    channel.status_code = response.getcode()
                    channel.content_type = response.headers.get("Content-Type", "")
                    channel.valid = response.getcode() < 400
            except Exception as inner:  # noqa: BLE001 - validation should report all failures.
                channel.error = str(inner)
        else:
            channel.error = str(exc)
    except Exception as exc:  # noqa: BLE001 - validation should report all failures.
        channel.error = str(exc)

    channel.latency_ms = int((time.perf_counter() - start) * 1000)
    return channel


def validate_channels(channels: Iterable[Channel], timeout: int = 10, workers: int = 8) -> list[Channel]:
    channels = list(channels)
    if not channels:
        return []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(validate_channel, channel, timeout): channel for channel in channels}
        for future in as_completed(future_map):
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001 - keep batch validation alive.
                future_map[future].error = str(exc)
    return channels
