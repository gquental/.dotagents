#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
BIN_SRC="$REPO_DIR/bin"

CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
LOCAL_BIN_DIR="$HOME/.local/bin"

mkdir -p "$CLAUDE_SKILLS_DIR" "$AGENTS_SKILLS_DIR" "$LOCAL_BIN_DIR"

link() {
    local src="$1" dest="$2"
    rm -rf "$dest"
    ln -s "$src" "$dest"
    echo "linked $dest -> $src"
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
