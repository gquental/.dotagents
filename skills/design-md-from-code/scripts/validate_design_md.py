"""Validate the structural and evidence invariants of an extracted DESIGN.md."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REQUIRED_SCALARS = ("name", "version", "status", "source_mode", "last_verified")
ALLOWED_SOURCE_MODES = {"source-only", "code-and-screenshots", "runtime-verified"}
REQUIRED_SECTIONS = (
    "System character",
    "Foundations",
    "Layout and responsive behavior",
    "Components and states",
    "Composition patterns",
    "Accessibility",
    "Rules",
    "Evidence and confidence",
    "Known gaps and drift",
)
TOKEN_GROUPS = (
    "colors",
    "typography",
    "spacing",
    "radii",
    "elevation",
    "motion",
    "breakpoints",
    "themes",
)
PLACEHOLDERS = (
    "TODO",
    "TBD",
    "Lorem ipsum",
    "[Project name]",
    "<project>",
    "PLACEHOLDER",
)
EVIDENCE_PATH = re.compile(
    r"`[^`\n]+\.(?:astro|cjs|css|erb|haml|html|js|json|jsx|less|liquid|mdx|mjs|njk|php|pug|rb|sass|scss|slim|svelte|toml|ts|tsx|twig|vue|yaml|yml)(?::\d+(?:-\d+)?)?`",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to DESIGN.md")
    return parser.parse_args()


def split_frontmatter(text: str) -> tuple[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return None
    return "\n".join(lines[1:closing]), "\n".join(lines[closing + 1 :])


def scalar(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    split = split_frontmatter(text)
    if split is None:
        return ["missing or unclosed YAML frontmatter"], warnings
    frontmatter, body = split

    for key in REQUIRED_SCALARS:
        if scalar(frontmatter, key) is None:
            errors.append(f"missing top-level frontmatter key: {key}")

    if scalar(frontmatter, "version") not in {None, "1"}:
        errors.append("frontmatter version must be 1")
    if scalar(frontmatter, "status") not in {None, "extracted"}:
        errors.append('frontmatter status must be "extracted"')

    source_mode = scalar(frontmatter, "source_mode")
    if source_mode is not None and source_mode not in ALLOWED_SOURCE_MODES:
        errors.append(
            "source_mode must be one of: " + ", ".join(sorted(ALLOWED_SOURCE_MODES))
        )

    last_verified = scalar(frontmatter, "last_verified")
    if last_verified is not None:
        try:
            date.fromisoformat(last_verified)
        except ValueError:
            errors.append("last_verified must use YYYY-MM-DD")

    present_token_groups = [
        key
        for key in TOKEN_GROUPS
        if re.search(rf"(?m)^{re.escape(key)}:\s*$", frontmatter)
    ]
    if not present_token_groups:
        warnings.append("frontmatter has no structured token groups")

    h1_headings = re.findall(r"(?m)^# (.+)$", body)
    if len(h1_headings) != 1:
        errors.append(f"expected exactly one H1 heading, found {len(h1_headings)}")

    actual_sections = re.findall(r"(?m)^## (.+?)\s*$", body)
    if actual_sections != list(REQUIRED_SECTIONS):
        errors.append(
            "H2 sections must match the required names and order; found: "
            + (", ".join(actual_sections) if actual_sections else "none")
        )

    for placeholder in PLACEHOLDERS:
        if placeholder.lower() in text.lower():
            errors.append(f"unresolved placeholder: {placeholder}")

    for candidate in re.findall(r"#[0-9A-Za-z]+", text):
        if re.fullmatch(r"#[0-9A-Fa-f]+", candidate) and len(candidate) not in {
            4,
            5,
            7,
            9,
        }:
            errors.append(f"invalid hex color length: {candidate}")

    evidence_match = re.search(
        r"(?ms)^## Evidence and confidence\s*$\n(.*?)(?=^## |\Z)", body
    )
    if evidence_match is None:
        errors.append("missing Evidence and confidence content")
    else:
        evidence = evidence_match.group(1)
        if "| Evidence |" not in evidence or "| Confidence |" not in evidence:
            errors.append(
                "evidence section must contain Evidence and Confidence table columns"
            )
        if not EVIDENCE_PATH.search(evidence):
            errors.append(
                "evidence section must cite at least one repository source file in backticks"
            )
        if not re.search(r"(?i)\b(high|medium|low)\b", evidence):
            errors.append("evidence section must state confidence levels")

    return errors, warnings


def main() -> int:
    args = parse_args()
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"error: file does not exist: {path}", file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"error: cannot read {path}: {error}", file=sys.stderr)
        return 2

    errors, warnings = validate(text)
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        print(
            f"DESIGN.md validation failed with {len(errors)} error(s).", file=sys.stderr
        )
        return 1
    print(f"DESIGN.md validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
