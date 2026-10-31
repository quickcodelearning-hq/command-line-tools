# At the Books command-line tools

Small Zsh tools for episode production on Ken’s Mac.

## Commands

- `atb`: go to `~/Documents/At The Books`.
- `atb 34`: find the top-level chapter 34 folder; enter its `Export` subfolder when present. This function must be sourced into the current shell.
- `atb-review [video]`: use FFmpeg to create a separate H.264/AAC review MP4, at most 1280 pixels wide. Automatic selection recognizes lowercase extensions; pass uppercase `.MP4` files explicitly.
- `atb-backup`: copy the Completed folder to both configured ATB external drives using rsync, then verify names and file sizes. This is not a content-checksum verification and does not delete local files.

## Installation on this Mac

`~/.zshrc` sources `atb.zsh`. Links in `~/bin` point to `atb-review` and `atb-backup`; `~/bin` is on PATH. Keep this directory at its current location or update those links and the source line.

Requires Zsh, FFmpeg for review conversion, and macOS rsync/stat for backups. The scripts currently contain Mac-specific folder and drive paths.

Keep episode media, API keys, and the full shell configuration outside this repository.
