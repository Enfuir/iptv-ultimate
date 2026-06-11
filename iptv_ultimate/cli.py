from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from .playlist import build_m3u, channels_to_payload, dedupe_channels, load_sources, parse_m3u, write_json
from .validate import validate_channels

try:
    import urllib.request
except Exception:  # pragma: no cover
    urllib = None


def fetch_source(source):
    if urllib is None:
        raise RuntimeError("urllib is unavailable")

    parsed = urlparse(source.url)
    if parsed.scheme == "file":
        return Path(parsed.path).read_text(encoding="utf-8", errors="replace")
    if parsed.scheme == "" and Path(source.url).exists():
        return Path(source.url).read_text(encoding="utf-8", errors="replace")

    headers = {"User-Agent": "IPTV-Ultimate/0.1"}
    if source.headers:
        headers.update(source.headers)
    request = urllib.request.Request(source.url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def collect_channels(source_path: str | Path) -> list:
    sources = load_sources(source_path)
    channels = []
    for source in sources:
        text = fetch_source(source)
        channels.extend(parse_m3u(text, source.name, source))
    return dedupe_channels(channels)


def cmd_build(args: argparse.Namespace) -> int:
    channels = collect_channels(args.sources)
    if args.validate:
        channels = validate_channels(channels, timeout=args.timeout, workers=args.workers)
        if args.working_only:
            channels = [channel for channel in channels if channel.valid]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(build_m3u(channels), encoding="utf-8")

    if args.json_output:
        write_json(args.json_output, channels_to_payload(channels, args.sources))

    print(f"Built {len(channels)} channel(s) -> {args.output}")
    if args.json_output:
        print(f"Wrote JSON -> {args.json_output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    channels = collect_channels(args.sources)
    channels = validate_channels(channels, timeout=args.timeout, workers=args.workers)
    payload = channels_to_payload(channels, args.sources)
    write_json(args.output, payload)
    valid = sum(1 for channel in channels if channel.valid)
    print(f"Validated {len(channels)} channel(s); {valid} passed -> {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="iptv-ultimate")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build clean M3U and JSON playlists from source registry")
    build.add_argument("--sources", required=True)
    build.add_argument("--output", default="output/channels.m3u")
    build.add_argument("--json-output", default="output/channels.json")
    build.add_argument("--validate", action="store_true")
    build.add_argument("--working-only", action="store_true")
    build.add_argument("--timeout", type=int, default=10)
    build.add_argument("--workers", type=int, default=8)
    build.set_defaults(func=cmd_build)

    validate = sub.add_parser("validate", help="Validate parsed stream URLs and write results JSON")
    validate.add_argument("--sources", required=True)
    validate.add_argument("--output", default="output/validate.json")
    validate.add_argument("--timeout", type=int, default=10)
    validate.add_argument("--workers", type=int, default=8)
    validate.set_defaults(func=cmd_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
