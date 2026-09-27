# SoC Print CLI 🖨️

A beautiful, fully-animated cross-platform Terminal UI for silently bypassing the NUS School of Computing (SoC) printing authentication and natively queueing PDF print jobs over SSH.

Built with Python and `rich`, featuring a native port of the famous Campy Cat animation.

## Installation

You can install this TUI globally on your system.

```bash
mkdir -p ~/.local/bin
curl -sL https://raw.githubusercontent.com/travisim/socprint-cli/main/socprinter.py -o ~/.local/bin/socprint
chmod +x ~/.local/bin/socprint
```

Run it once to install the alias and SSH keys:
```bash
python3 ~/.local/bin/socprint
```

Now you can print from any directory:
```bash
socprinter
```

## AI Agent Integration (Claude / Codex)

This CLI was designed to empower autonomous coding agents to print physical documents without getting stuck in TUI navigation prompts.

If you are using Claude Code, Codex, or Cursor, you can provide them with the following prompt:

> "Please print `filename.pdf` using the `socprinter` command. You must pass the `--auto` flag to bypass the interactive TUI (e.g. `socprinter filename.pdf --auto`)."

## How it Works

The CLI automates the entire SSH printing process into a single command:
1. `scp` - Uploads the PDF securely to the SoC server's `/tmp` directory.
2. `ssh` - Remotely executes `lpr -P<queue> /tmp/...` to push the document directly into the printing queue.
3. Automatically deletes the temporary remote PDF footprint once spooled.
