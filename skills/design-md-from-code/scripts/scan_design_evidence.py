"""Index design-system evidence in a frontend repository.

The report is deliberately mechanical. It finds likely source files and exact
style values with file-and-line occurrences. An agent still decides which
values are canonical and what they mean.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".turbo",
    ".yarn",
    "build",
    "coverage",
    "dist",
    "log",
    "node_modules",
    "public/assets",
    "tmp",
    "vendor/bundle",
}

SOURCE_EXTENSIONS = {
    ".astro",
    ".cjs",
    ".css",
    ".erb",
    ".haml",
    ".html",
    ".js",
    ".jsx",
    ".less",
    ".liquid",
    ".mdx",
    ".mjs",
    ".njk",
    ".php",
    ".pug",
    ".rb",
    ".sass",
    ".scss",
    ".slim",
    ".svelte",
    ".ts",
    ".tsx",
    ".twig",
    ".vue",
}

STRUCTURED_EXTENSIONS = {".json", ".toml", ".yaml", ".yml"}
DESIGN_FILE_MARKERS = ("color", "design", "palette", "style", "theme", "token")

MANIFEST_NAMES = {
    "Gemfile",
    "angular.json",
    "astro.config.js",
    "astro.config.mjs",
    "astro.config.ts",
    "components.json",
    "next.config.cjs",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "nuxt.config.mjs",
    "nuxt.config.js",
    "nuxt.config.ts",
    "package.json",
    "postcss.config.cjs",
    "postcss.config.js",
    "postcss.config.mjs",
    "postcss.config.ts",
    "svelte.config.js",
    "svelte.config.ts",
    "tailwind.config.cjs",
    "tailwind.config.js",
    "tailwind.config.mjs",
    "tailwind.config.ts",
    "vite.config.cjs",
    "vite.config.js",
    "vite.config.mjs",
    "vite.config.ts",
}

PATTERNS = {
    "css_custom_properties": re.compile(r"(?m)(--[A-Za-z0-9_-]+)\s*:\s*([^;{}\n]+);"),
    "sass_variables": re.compile(r"(?m)^\s*(\$[A-Za-z0-9_-]+)\s*:\s*([^;\n]+);"),
    "colors": re.compile(
        r"(?i)(?<![\w-])(?:#[0-9a-f]{8}|#[0-9a-f]{6}|#[0-9a-f]{4}|#[0-9a-f]{3})\b"
        r"|(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^;{}\n]{1,160}\)"
    ),
    "font_families": re.compile(r"(?i)font-family\s*:\s*([^;{}\n]+)"),
    "radii": re.compile(r"(?i)border-radius\s*:\s*([^;{}\n]+)"),
    "shadows": re.compile(r"(?i)(?:box|text)-shadow\s*:\s*([^;{}\n]+)"),
    "transitions": re.compile(r"(?i)transition(?:-[a-z-]+)?\s*:\s*([^;{}\n]+)"),
    "breakpoints": re.compile(r"(?i)@media[^{}\n]*\((?:min|max)-width\s*:\s*([^)]+)\)"),
}

MAX_OCCURRENCES_PER_VALUE = 25


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Index frontend design evidence without evaluating project code."
    )
    parser.add_argument("--root", required=True, help="Repository root to scan")
    parser.add_argument(
        "--output", default="-", help="JSON output path, or - for stdout"
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=1_000_000,
        help="Skip individual files larger than this many bytes",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=10_000,
        help="Stop if more candidate files are found",
    )
    return parser.parse_args()


def is_ignored(relative_path: Path) -> bool:
    posix = relative_path.as_posix()
    parts = relative_path.parts
    if any(part in IGNORED_DIRECTORIES for part in parts):
        return True
    return any(
        posix == item or posix.startswith(f"{item}/") for item in IGNORED_DIRECTORIES
    )


def is_structured_design_file(relative_path: Path) -> bool:
    if relative_path.suffix.lower() not in STRUCTURED_EXTENSIONS:
        return False
    lowered = relative_path.as_posix().lower()
    return any(marker in lowered for marker in DESIGN_FILE_MARKERS)


def candidate_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if is_ignored(relative):
            continue
        if (
            path.suffix.lower() in SOURCE_EXTENSIONS
            or path.name in MANIFEST_NAMES
            or is_structured_design_file(relative)
        ):
            candidates.append(path)
    return sorted(candidates, key=lambda item: item.relative_to(root).as_posix())


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def normalize_value(value: str) -> str:
    return " ".join(value.strip().split())


def add_occurrence(
    values: dict[str, list[dict[str, object]]],
    key: str,
    relative_path: str,
    line: int,
    name: str | None = None,
) -> None:
    occurrence: dict[str, object] = {"file": relative_path, "line": line}
    if name is not None:
        occurrence["name"] = name
    if len(values[key]) < MAX_OCCURRENCES_PER_VALUE:
        values[key].append(occurrence)


def detect_stack(texts: dict[str, str]) -> list[str]:
    combined = "\n".join(
        text
        for path, text in texts.items()
        if path.endswith(("package.json", "Gemfile"))
    ).lower()
    signals = {
        "Angular": "@angular/core",
        "Astro": '"astro"',
        "Next.js": '"next"',
        "Rails": "rails",
        "React": '"react"',
        "Svelte": '"svelte"',
        "Tailwind CSS": "tailwindcss",
        "Vue": '"vue"',
    }
    detected = [name for name, needle in signals.items() if needle in combined]
    if any(path.endswith(".css") for path in texts) and not detected:
        detected.append("HTML/CSS")
    return detected


def sorted_value_records(
    counts: Counter[str], occurrences: dict[str, list[dict[str, object]]]
) -> list[dict[str, object]]:
    records = []
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        records.append(
            {
                "value": value,
                "count": count,
                "occurrences": occurrences[value],
            }
        )
    return records


def scan(root: Path, max_file_bytes: int, max_files: int) -> dict[str, object]:
    paths = candidate_files(root)
    if len(paths) > max_files:
        raise ValueError(
            f"Found {len(paths)} candidate files, above --max-files={max_files}. "
            "Narrow the root or raise the limit explicitly."
        )

    texts: dict[str, str] = {}
    skipped_large: list[str] = []
    skipped_unreadable: list[str] = []
    manifests: list[str] = []
    source_files: list[str] = []

    counts: dict[str, Counter[str]] = {category: Counter() for category in PATTERNS}
    occurrences: dict[str, dict[str, list[dict[str, object]]]] = {
        category: defaultdict(list) for category in PATTERNS
    }

    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            if path.stat().st_size > max_file_bytes:
                skipped_large.append(relative)
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            skipped_unreadable.append(relative)
            continue

        texts[relative] = text
        if path.name in MANIFEST_NAMES:
            manifests.append(relative)
        else:
            source_files.append(relative)

        for category, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                if category in {"css_custom_properties", "sass_variables"}:
                    name = normalize_value(match.group(1))
                    value = normalize_value(match.group(2))
                    key = f"{name}: {value}"
                    counts[category][key] += 1
                    add_occurrence(
                        occurrences[category],
                        key,
                        relative,
                        line_number(text, match.start()),
                        name=name,
                    )
                else:
                    value = normalize_value(
                        match.group(1) if match.lastindex else match.group(0)
                    )
                    counts[category][value] += 1
                    add_occurrence(
                        occurrences[category],
                        value,
                        relative,
                        line_number(text, match.start()),
                    )

    return {
        "root": str(root),
        "detected_stack": detect_stack(texts),
        "summary": {
            "candidate_files": len(paths),
            "scanned_files": len(texts),
            "manifest_files": len(manifests),
            "source_files": len(source_files),
            "skipped_large": len(skipped_large),
            "skipped_unreadable": len(skipped_unreadable),
        },
        "manifests": manifests,
        "source_files": source_files,
        "evidence": {
            category: sorted_value_records(counts[category], occurrences[category])
            for category in PATTERNS
        },
        "skipped": {
            "large": skipped_large,
            "unreadable": skipped_unreadable,
        },
    }


def write_report(report: dict[str, object], output: str) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output == "-":
        sys.stdout.write(rendered)
        return
    output_path = Path(output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root is not a directory: {root}", file=sys.stderr)
        return 2
    if args.max_file_bytes <= 0 or args.max_files <= 0:
        print("error: scan limits must be positive", file=sys.stderr)
        return 2

    try:
        report = scan(root, args.max_file_bytes, args.max_files)
        write_report(report, args.output)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
