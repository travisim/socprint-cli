# SoC Print CLI 🖨️ (Unofficial)

> **Unofficial, community-made tool. It is not endorsed, approved or supported by NUS School of Computing IT.** Use at your own discretion and follow SoC IT's acceptable-use policies.

A beautiful, fully-animated cross-platform Terminal UI that sends your PDFs to the SoC print queues using your own SoC account over SSH (the same `scp` + `lpr` you could type by hand).

Built with Python and `rich`, featuring a native port of the famous Campy Cat animation.

## ⚠️ Upgrading from an earlier version (security notice)

Earlier versions of this tool **stored your SoC password in plaintext** in `~/.config/socprint/config.json`, and did not verify the server's SSH host key. If you ever installed an earlier version, please:

1. **Remove the old version and its stored credentials.** If you still have the old script, run `socprinter uninstall`. Otherwise delete manually:
   ```bash
   rm -rf ~/.config/socprint
   rm -f ~/.ssh/socprint_ed25519 ~/.ssh/socprint_ed25519.pub
   rm -f ~/.local/bin/socprint
   ```
   and remove the `socprinter` alias from your shell config (`~/.zshrc` / `~/.bashrc`). Also remove any old `socprint_ed25519` public key line from `~/.ssh/authorized_keys` on the SoC server.
2. **Change your SoC password as a precaution**, since the old version kept it on disk.
3. **Install the current version** below. On first run it scrubs any leftover password field automatically, but it cannot notify you by itself (the tool has no telemetry or update channel), so please do the steps above.

## Installation

You can install this TUI globally on your system. **Note: You must be connected to the SoC VPN or physically on the SoC network to use this tool.**

```bash
mkdir -p ~/.local/bin
curl -sL https://github.com/travisim/socprint-cli/releases/latest/download/socprinter.py -o ~/.local/bin/socprint
chmod +x ~/.local/bin/socprint
```

Run it once to set up. It creates a dedicated SSH key, asks you to verify the server's host-key fingerprint with SoC IT, and installs the key with your confirmation:
```bash
python3 ~/.local/bin/socprint
```

Now you can print from any directory:
```bash
socprinter
```

## Security & Privacy

- **No password is stored.** Your password is typed once into `ssh` itself to install a key; this tool never reads or saves it. Only your username is kept in `~/.config/socprint/config.json`. Older versions saved the password there; the file is scrubbed automatically on next run.
- **Host key is verified.** On first setup the server fingerprint is shown and you must confirm it with SoC IT (official SoC documentation or SoC IT support); this tool cannot verify it for you and does not ship a trusted fingerprint. It is saved to `~/.config/socprint/known_hosts` and enforced (`StrictHostKeyChecking=yes`) afterwards.
- **Dedicated key.** Uses `~/.ssh/socprint_ed25519` only; your existing SSH keys are never touched. Setup asks for consent before adding the public key to `~/.ssh/authorized_keys` on the SoC server.
- **No telemetry.** The tool and this repo send nothing to any website or analytics service. The only network connections are SSH/SCP to `stu.comp.nus.edu.sg`.
- **Remove everything:** run `socprinter uninstall` to delete the local key/settings and revoke the key on the server.

See [SECURITY.md](SECURITY.md) to report issues.

## AI Agent Integration (optional)

Agents can print non-interactively with `socprinter filename.pdf --auto` once you have completed setup yourself. Review the script before letting any agent install or run it for you.

## How it Works

The CLI automates the entire SSH printing process into a single command:

1. **`scp`**: Uploads the PDF securely to the SoC server's `/tmp` directory.
   ```bash
   scp -i ~/.ssh/socprint_ed25519 filename.pdf username@stu.comp.nus.edu.sg:/tmp/socprint_123.pdf
   ```

2. **`ssh lpr`**: Remotely executes the print spool command and immediately cleans up the payload.
   ```bash
   ssh username@stu.comp.nus.edu.sg 'lpr -P<queue> /tmp/socprint_123.pdf && lpq -P<queue> ; rm -f /tmp/socprint_123.pdf'
   ```
