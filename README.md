# .dotagents

Personal skills and CLI tools for AI coding agents (Claude Code, Codex, etc.).

## Layout

- `skills/` — skill packages (one folder per skill, each with a `SKILL.md`).
- `bin/` — executable scripts.
- `install.sh` — symlinks skills and scripts into the right places and ensures `~/.local/bin` is on `PATH`.

## Install

```bash
./install.sh
```

This will:

- symlink each `skills/<name>/` into `~/.claude/skills/<name>` and `~/.agents/skills/<name>`
- symlink each `bin/<name>` into `~/.local/bin/<name>`
- append a `# >>> dotagents >>>` block to `~/.zshrc` and `~/.bashrc` so that `~/.local/bin` is on `PATH` (idempotent — only added if the marker is missing)

Existing files at any destination path are replaced without backup.

## License

MIT — see [`LICENSE`](LICENSE).
