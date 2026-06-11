# IPTV Ultimate

Legal-by-default IPTV playlist builder, validator, deduper, and static player.

This repo is **not** a copy-paste dump of other IPTV repositories. It is an original toolkit for people who already own or are legally allowed to use IPTV streams and want a cleaner workflow than the usual scattered M3U repos.

## What it beats the old repos at

- **Legal-by-default posture:** no paid/pirated subscriptions, no hidden scraping, no copied channel dumps.
- **Reusable pipeline:** ingest M3U/M3U8 URLs, parse metadata, validate streams, dedupe, and generate clean playlists.
- **Working-only playlists:** optional stream health checks with timeout and concurrency controls.
- **Static player:** built-in web UI using HLS.js for generated playlists.
- **CI-ready:** GitHub Actions can validate and build playlists on every push.
- **Source registry:** keep your legal sources in JSON instead of hand-editing giant M3U files.

## Quick start

```bash
cd iptv-ultimate
python -m pip install -e .
python -m iptv_ultimate.cli validate --sources data/sources.local.json --output output/validate.json
python -m iptv_ultimate.cli build --sources data/sources.local.json --output output/channels.m3u --json-output output/channels.json --validate --working-only
```

Open `public/index.html` in a browser and load `output/channels.json` if your browser permits local file access, or serve it with:

```bash
python -m http.server 8000 --directory .
```

Then visit `http://localhost:8000/public/index.html`.

## Add your own legal sources

Edit `data/sources.local.json`:

```json
[
  {
    "name": "My legal IPTV provider",
    "url": "https://example.com/customer/playlist.m3u",
    "group-title": "My Legal IPTV",
    "country": "US",
    "language": "en",
    "enabled": true,
    "headers": {}
  }
]
```

Only add streams you are allowed to access and redistribute.

## CLI

```bash
python -m iptv_ultimate.cli build \
  --sources data/sources.local.json \
  --output output/channels.m3u \
  --json-output output/channels.json \
  --validate \
  --working-only \
  --timeout 10 \
  --workers 8
```

Commands:

- `validate`: fetch sources, parse playlists, validate stream URLs, write `validate.json`.
- `build`: parse sources, optionally validate, dedupe, write `.m3u` and `.json`.

## Output format

`output/channels.json` contains a flat channel list:

```json
{
  "generated_at": "2026-06-11T00:00:00Z",
  "source": "data/sources.local.json",
  "channels": [
    {
      "name": "Big Buck Bunny public test stream",
      "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
      "group-title": "Legal test streams",
      "country": "INT",
      "language": "en",
      "valid": true
    }
  ]
}
```

## Static player

The player reads `output/channels.json` and lets you:

- search by channel name
- filter by group/country/language
- copy stream URLs
- play HLS streams in the browser

## Competitive notes

Common IPTV repos focus on one thing: giant playlists. This project focuses on the workflow around playlists: source management, validation, dedupe, generation, and playback.

Relevant public IPTV repos for market research:

- https://github.com/iptv-org/iptv
- https://github.com/iptv-org/awesome-iptv
- https://github.com/iptv-org/database
- https://github.com/iptv-org/epg
- https://github.com/Free-TV/IPTV
- https://github.com/4gray/iptvnator
- https://github.com/Fredolx/open-tv
- https://github.com/linuxmint/hypnotix
- https://github.com/tvheadend/tvheadend
- https://github.com/chrisbenincasa/tunarr
- https://github.com/zhimin-dev/iptv-checker
- https://github.com/Guovin/iptv-api
- https://github.com/imDazui/Tvlist-awesome-m3u-m3u8
- https://github.com/HerbertHe/iptv-sources
- https://github.com/Meroser/IPTV
- https://github.com/yuanzl77/IPTV
- https://github.com/mytv-android/mytv-android
- https://github.com/GhostenEditor/Ghosten-Player
- https://github.com/gstory0404/Cinetry
- https://github.com/Davidona/StreamVault-IPTV
- https://github.com/clubanderson/clubTivi
- https://github.com/jvdillon/netv
- https://github.com/bsogulcan/another-iptv-player
- https://github.com/EvilCult/iptv-m3u-maker
- https://github.com/qwerttvv/Beijing-IPTV
- https://github.com/hujingguang/ChinaIPTV

## Ethics

Do not use this project to redistribute paid, stolen, or unauthorized streams. Use it for:

- your own IPTV subscription
- public/free streams that explicitly allow redistribution
- test/demo streams
- private home-lab TV stacks

## License

MIT.
