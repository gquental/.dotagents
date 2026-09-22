# .dotagents

Personal skills and CLI tools for AI coding agents (Claude Code, Codex, etc.).

## Layout

- `skills/` — skill packages (one folder per skill, each with a `SKILL.md`).
- `bin/` — executable scripts.
- `pstacks/` — `pstack-claude`, `pstack-codex`, and `pstack-grok` as git submodules.
- `install.sh` — symlinks skills, scripts, and the pstack checkouts into the right places and ensures `~/.local/bin` is on `PATH`.

## Install

```bash
./install.sh
```

This will:

- symlink each `skills/<name>/` into `~/.claude/skills/<name>` and `~/.agents/skills/<name>`
- symlink each `bin/<name>` into `~/.local/bin/<name>`
- symlink the pstack submodules into the harness that loads them:
  - `pstacks/pstack-grok/plugins/pstack` to `~/.grok/plugins/pstack`
  - `pstacks/pstack-codex` as the Codex `pstack-codex` marketplace, and `plugins/pstack` over the installed cache directory
  - `pstacks/pstack-claude` to `~/.claude/plugins/marketplaces/pstack-claude`, and `plugins/pstack` over the installed cache directory
- append a `# >>> dotagents >>>` block to `~/.zshrc` and `~/.bashrc` so that `~/.local/bin` is on `PATH` (idempotent — only added if the marker is missing)

The first clone needs `git submodule update --init --recursive`. `pstack-claude`, `pstack-codex`, and `pstack-grok` are private. Existing files at any destination path are replaced without backup.

## License

MIT — see [`LICENSE`](LICENSE).
