# SoC Print CLI 🖨️

A beautiful, fully-animated cross-platform Terminal UI for silently bypassing the NUS School of Computing (SoC) printing authentication and natively queueing PDF print jobs over SSH.

Built with Python and `rich`, featuring a native port of the famous Campy Cat animation.

## Installation

You can install this TUI globally on your system. **Note: You must be connected to the SoC VPN or physically on the SoC network to use this tool.**

```bash
mkdir -p ~/.local/bin
curl -sL https://github.com/travisim/socprint-cli/releases/latest/download/socprinter.py -o ~/.local/bin/socprint
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

> "Please print `filename.pdf` using the `socprinter` command. You must pass the `--auto` flag to bypass the interactive TUI (e.g. `socprinter filename.pdf --auto`). If the user does not have the tool installed, install it first using: `mkdir -p ~/.local/bin && curl -sL https://github.com/travisim/socprint-cli/releases/latest/download/socprinter.py -o ~/.local/bin/socprint && chmod +x ~/.local/bin/socprint && python3 ~/.local/bin/socprint`"

## How it Works

The CLI automates the entire SSH printing process into a single command:

1. **`scp`**: Uploads the PDF securely to the SoC server's `/tmp` directory.
   ```bash
   scp filename.pdf username@stu.comp.nus.edu.sg:/tmp/socprint_123.pdf
   ```

2. **`ssh lpr`**: Remotely executes the print spool command and immediately cleans up the payload.
   ```bash
   ssh username@stu.comp.nus.edu.sg 'lpr -P<queue> /tmp/socprint_123.pdf && lpq -P<queue> ; rm -f /tmp/socprint_123.pdf'
   ```
