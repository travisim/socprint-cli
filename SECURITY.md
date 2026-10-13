# Security Policy

SoC Print CLI is an **unofficial** community tool. It is not endorsed or approved by NUS School of Computing IT.

## What the tool does
- Creates a dedicated ed25519 key (`~/.ssh/socprint_ed25519`) and, with explicit consent, appends its public key to `~/.ssh/authorized_keys` on `stu.comp.nus.edu.sg`.
- Never reads, stores or transmits your password (ssh prompts for it directly).
- Verifies the server host key (shown to you for confirmation on first use, then enforced).
- Makes no network connections other than SSH/SCP to `stu.comp.nus.edu.sg`. No telemetry.
- Stores only your username in `~/.config/socprint/config.json` (mode 600).

## Notice for users of earlier versions
Earlier versions stored the SoC password in plaintext in `~/.config/socprint/config.json` and disabled host-key checking. If you installed one, remove it and its stored credentials (see the README upgrade notice), change your SoC password as a precaution, and install the current version. The tool has no update channel or telemetry, so it cannot notify you itself.

## Reporting a vulnerability
Open a private security advisory on this repository, or email the maintainer. Please allow reasonable time for a fix.
