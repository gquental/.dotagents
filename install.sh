#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
BIN_SRC="$REPO_DIR/bin"
PSTACKS_SRC="$REPO_DIR/pstacks"

CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR" "$LOCAL_BIN_DIR"

link() {
    local src="$1" dest="$2"
    mkdir -p "$(dirname "$dest")"
    rm -rf "$dest"
    ln -s "$src" "$dest"
    echo "linked $dest -> $src"
}

require_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "missing $dir" >&2
        echo "run: git submodule update --init --recursive" >&2
        exit 1
    fi
}

json_version() {
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$1"
}

link_pstacks() {
    local claude_repo="$PSTACKS_SRC/pstack-claude"
    local codex_repo="$PSTACKS_SRC/pstack-codex"
    local grok_repo="$PSTACKS_SRC/pstack-grok"
    local claude_plugin="$claude_repo/plugins/pstack"
    local codex_plugin="$codex_repo/plugins/pstack"
    local grok_plugin="$grok_repo/plugins/pstack"

    require_dir "$claude_plugin"
    require_dir "$codex_plugin"
    require_dir "$grok_plugin"

    link "$grok_plugin" "$HOME/.grok/plugins/pstack"
    python3 - "$HOME/.grok/installed-plugins/registry.json" "$grok_plugin" <<'PY'
import json, pathlib, sys
registry, target = sys.argv[1:]
path = pathlib.Path(registry)
if not path.exists():
    print(f"no {registry}; skipped Grok registry")
    raise SystemExit(0)
data = json.loads(path.read_text())
changed = False
for repo in data.get("repos", {}).values():
    kind = repo.get("kind") or {}
    source = kind.get("source_path")
    if kind.get("type") == "Local" and isinstance(source, str) and source.rstrip("/").endswith("/pstack-grok/plugins/pstack"):
        if source != target:
            kind["source_path"] = target
            changed = True
if changed:
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated Grok registry source to {target}")
else:
    print("Grok registry already points at the pstack-grok submodule")
PY

    python3 - "$HOME/.codex/config.toml" "$codex_repo" <<'PY'
import pathlib, sys
config, source = sys.argv[1:]
path = pathlib.Path(config)
if not path.exists():
    print(f"no {config}; skipped Codex marketplace")
    raise SystemExit(0)
lines = path.read_text().splitlines()
section = None
replaced = False
found = False
for index, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        section = stripped
        if section == "[marketplaces.pstack-codex]":
            found = True
        continue
    if section == "[marketplaces.pstack-codex]" and "=" in line:
        key, _value = line.split("=", 1)
        if key.strip() == "source":
            new = f'{key.rstrip()} = "{source}"'
            if lines[index] != new:
                lines[index] = new
                replaced = True
if not found:
    if lines and lines[-1] != "":
        lines.append("")
    lines.extend([
        "[marketplaces.pstack-codex]",
        'source_type = "local"',
        f'source = "{source}"',
    ])
    replaced = True
if replaced:
    path.write_text("\n".join(lines) + "\n")
    print(f"updated Codex marketplace source to {source}")
else:
    print("Codex marketplace already points at the pstack-codex submodule")
PY

    local codex_version
    codex_version="$(json_version "$codex_plugin/.codex-plugin/plugin.json")"
    link "$codex_plugin" "$HOME/.codex/plugins/cache/pstack-codex/pstack/$codex_version"

    link "$claude_repo" "$HOME/.claude/plugins/marketplaces/pstack-claude"
    local claude_installs
    claude_installs="$(python3 - "$HOME/.claude/plugins/installed_plugins.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
if not path.exists():
    raise SystemExit(0)
data = json.loads(path.read_text())
for entry in data.get("plugins", {}).get("pstack@pstack-claude", []):
    install = entry.get("installPath")
    if install:
        print(install)
PY
)"
    if [ -n "$claude_installs" ]; then
        local install_path
        while IFS= read -r install_path; do
            [ -n "$install_path" ] || continue
            link "$claude_plugin" "$install_path"
        done <<< "$claude_installs"
    else
        local claude_version
        claude_version="$(json_version "$claude_plugin/.claude-plugin/plugin.json")"
        link "$claude_plugin" "$HOME/.claude/plugins/cache/pstack-claude/pstack/$claude_version"
    fi

    python3 - "$HOME/.claude/settings.json" "$HOME/.claude/plugins/known_marketplaces.json" <<'PY'
import pathlib, sys
old = "michael-denyer/pstack-claude"
new = "gquental/pstack-claude"
for raw in sys.argv[1:]:
    path = pathlib.Path(raw)
    if not path.exists():
        print(f"no {path}; skipped Claude marketplace record")
        continue
    text = path.read_text()
    if new in text and old not in text:
        print(f"Claude marketplace record in {path.name} already uses {new}")
        continue
    if old not in text:
        print(f"left {path.name} unchanged; it does not name {old}")
        continue
    path.write_text(text.replace(old, new))
    print(f"updated Claude marketplace record in {path.name} to {new}")
PY
}

for skill_dir in "$SKILLS_SRC"/*/; do
    skill_dir="${skill_dir%/}"
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    link "$skill_dir" "$CLAUDE_SKILLS_DIR/$skill_name"
    link "$skill_dir" "$AGENTS_SKILLS_DIR/$skill_name"
done

for script in "$BIN_SRC"/*; do
    [ -f "$script" ] || continue
    chmod +x "$script"
    link "$script" "$LOCAL_BIN_DIR/$(basename "$script")"
done

link_pstacks

BLOCK_START="# >>> dotagents >>>"
BLOCK_END="# <<< dotagents <<<"
BLOCK_BODY='export PATH="$HOME/.local/bin:$PATH"'

ensure_path_block() {
    local rc="$1"
    [ -e "$rc" ] || touch "$rc"
    if grep -qF "$BLOCK_START" "$rc"; then
        echo "PATH block already present in $rc"
        return
    fi
    {
        printf '\n%s\n' "$BLOCK_START"
        printf '%s\n' "$BLOCK_BODY"
        printf '%s\n' "$BLOCK_END"
    } >> "$rc"
    echo "added PATH block to $rc"
}

ensure_path_block "$HOME/.zshrc"
ensure_path_block "$HOME/.bashrc"

echo "done."
