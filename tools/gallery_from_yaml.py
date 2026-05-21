#!/usr/bin/env python3
"""Generate a Jekyll gallery collection from a YAML source file.

The YAML file is the editable source of truth. This script writes the gallery
Markdown file and creates any missing image assets under `media_subpath`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional, Union


MAX_BYTES_DEFAULT = 150 * 1024
MAX_EDGE_DEFAULT = 1800
MIN_EDGE_DEFAULT = 900
QUALITY_DEFAULT = 85
MIN_QUALITY_DEFAULT = 55

REPO_ROOT = Path(__file__).resolve().parents[1]


class GalleryError(RuntimeError):
    """Expected user-facing error."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a gallery collection markdown file from YAML."
    )
    parser.add_argument("yaml_file", type=Path, help="Gallery YAML source file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output markdown path. Defaults to _galleries/<media folder>.md.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing markdown or image assets.",
    )
    parser.add_argument(
        "--force-assets",
        action="store_true",
        help="Regenerate image assets even when target files already exist.",
    )
    parser.add_argument(
        "--no-assets",
        action="store_true",
        help="Only write markdown; do not create or convert image assets.",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Only create or convert image assets; do not write markdown.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=MAX_BYTES_DEFAULT,
        help="Maximum generated image size in bytes. Default: 153600 (150 KiB).",
    )
    parser.add_argument(
        "--max-edge",
        type=int,
        default=MAX_EDGE_DEFAULT,
        help="Initial maximum width/height for generated images. Default: 1800.",
    )
    parser.add_argument(
        "--min-edge",
        type=int,
        default=MIN_EDGE_DEFAULT,
        help="Smallest maximum width/height to try. Default: 900.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=QUALITY_DEFAULT,
        help="Initial image quality for generated images. Default: 85.",
    )
    parser.add_argument(
        "--min-quality",
        type=int,
        default=MIN_QUALITY_DEFAULT,
        help="Lowest image quality to try. Default: 55.",
    )
    parser.add_argument(
        "--magick",
        type=Path,
        help="Path to ImageMagick's `magick` executable.",
    )
    return parser.parse_args()


def import_yaml_module() -> Optional[Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        return None
    return yaml


def load_yaml(path: Path) -> dict[str, Any]:
    yaml = import_yaml_module()
    if yaml:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    else:
        data = load_yaml_with_ruby(path)

    if not isinstance(data, dict):
        raise GalleryError("The YAML root must be a mapping.")
    return data


def load_yaml_with_ruby(path: Path) -> Any:
    ruby = shutil.which("ruby")
    if not ruby:
        raise GalleryError(
            "YAML parsing needs either PyYAML or Ruby. Install PyYAML with "
            "`python3 -m pip install PyYAML`."
        )

    code = (
        "require 'yaml'; require 'json'; require 'date'; "
        "data = YAML.safe_load("
        "File.read(ARGV[0]), "
        "permitted_classes: [Date, Time, Symbol], "
        "aliases: true"
        "); "
        "puts JSON.generate(data)"
    )

    try:
        result = subprocess.run(
            [ruby, "-e", code, str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise GalleryError(f"Ruby failed to parse YAML: {exc.stderr.strip()}") from exc

    return json.loads(result.stdout)


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()

    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}([ T].*)?", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def yaml_key(key: Any) -> str:
    text = str(key)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def yaml_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{yaml_key(key)}:")
                lines.extend(yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}{yaml_key(key)}: {yaml_scalar(item)}")
        return lines

    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{prefix}- {{}}")
                    continue

                first = True
                for key, nested in item.items():
                    marker = "-" if first else " "
                    first = False
                    if isinstance(nested, (dict, list)):
                        lines.append(f"{prefix}{marker} {yaml_key(key)}:")
                        lines.extend(yaml_lines(nested, indent + 4))
                    else:
                        lines.append(
                            f"{prefix}{marker} {yaml_key(key)}: {yaml_scalar(nested)}"
                        )
            elif isinstance(item, list):
                lines.append(f"{prefix}-")
                lines.extend(yaml_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines

    return [f"{prefix}{yaml_scalar(value)}"]


def dump_yaml(data: dict[str, Any]) -> str:
    return "\n".join(yaml_lines(data))


def expand_path(value: Union[str, Path]) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(value))))


def find_magick(explicit: Optional[Path]) -> str:
    candidates: list[str] = []
    if explicit:
        candidates.append(str(expand_path(explicit)))

    for name in ("magick", "convert"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    candidates.extend(
        [
            "/opt/homebrew/bin/magick",
            "/usr/local/bin/magick",
            "/opt/homebrew/bin/convert",
            "/usr/local/bin/convert",
        ]
    )

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    raise GalleryError(
        "ImageMagick was not found. Install it or pass `--magick /path/to/magick`."
    )


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "gallery"


def media_dir_from_subpath(media_subpath: str) -> Path:
    if not media_subpath:
        raise GalleryError("`media_subpath` is required.")
    if "://" in media_subpath:
        raise GalleryError("`media_subpath` must be a local site path, not a URL.")
    return (REPO_ROOT / media_subpath.lstrip("/")).resolve()


def default_output_path(data: dict[str, Any]) -> Path:
    media_subpath = str(data.get("media_subpath") or "").strip()
    if media_subpath:
        stem = Path(media_subpath).name
    else:
        title = str(data.get("title") or "gallery")
        date = str(data.get("date") or "").strip()
        stem = slugify(f"{date}-{title}" if date else title)
    return REPO_ROOT / "_galleries" / f"{stem}.md"


def ensure_within(parent: Path, child: Path, label: str) -> None:
    try:
        child.relative_to(parent)
    except ValueError as exc:
        raise GalleryError(f"{label} escapes {parent}: {child}") from exc


def resolve_target(asset_dir: Path, name: str) -> Path:
    if not name:
        raise GalleryError("Every photo needs a `name` field.")
    name_path = Path(name)
    if name_path.is_absolute():
        raise GalleryError(f"Photo `name` must be relative to media_subpath: {name}")
    target = (asset_dir / name_path).resolve()
    ensure_within(asset_dir, target, "Photo target")
    return target


def resolve_source(
    photo: dict[str, Any],
    yaml_dir: Path,
    source_common: Optional[str],
) -> Optional[Path]:
    raw_source = photo.get("source")
    if not raw_source:
        return None

    source = expand_path(str(raw_source))
    if source.is_absolute():
        return source

    if source_common:
        return (expand_path(source_common) / source).resolve()

    return (yaml_dir / source).resolve()


def quality_steps(start: int, floor: int) -> list[int]:
    start = max(1, min(100, start))
    floor = max(1, min(start, floor))
    steps = list(range(start, floor - 1, -5))
    if steps[-1] != floor:
        steps.append(floor)
    return steps


def edge_steps(start: int, floor: int) -> list[int]:
    start = max(1, start)
    floor = max(1, min(start, floor))
    steps: list[int] = []
    edge = start
    while edge >= floor:
        steps.append(edge)
        edge -= 200
    if steps[-1] != floor:
        steps.append(floor)
    return steps


def convert_image(
    magick: str,
    source: Path,
    target: Path,
    max_bytes: int,
    max_edge: int,
    min_edge: int,
    quality: int,
    min_quality: int,
    dry_run: bool,
) -> None:
    if not source.exists():
        raise GalleryError(f"Source image not found: {source}")

    if dry_run:
        print(f"convert {source} -> {target}")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    best_size: Optional[int] = None

    for edge in edge_steps(max_edge, min_edge):
        for q_value in quality_steps(quality, min_quality):
            fd, tmp_name = tempfile.mkstemp(
                prefix=f".{target.stem}.",
                suffix=target.suffix or ".jpg",
                dir=str(target.parent),
            )
            os.close(fd)
            tmp_path = Path(tmp_name)

            cmd = [
                magick,
                str(source),
                "-auto-orient",
                "-resize",
                f"{edge}x{edge}>",
                "-strip",
                "-quality",
                str(q_value),
                str(tmp_path),
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                size = tmp_path.stat().st_size
                best_size = size if best_size is None else min(best_size, size)
                if size <= max_bytes:
                    tmp_path.replace(target)
                    print(f"wrote {target} ({size / 1024:.0f} KiB)")
                    return
            except subprocess.CalledProcessError as exc:
                raise GalleryError(
                    f"ImageMagick failed for {source}: {exc.stderr.strip()}"
                ) from exc
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    size_text = "unknown" if best_size is None else f"{best_size / 1024:.0f} KiB"
    raise GalleryError(
        f"Could not get {target.name} below {max_bytes / 1024:.0f} KiB "
        f"(smallest attempt: {size_text})."
    )


def collection_photo(photo: dict[str, Any]) -> dict[str, Any]:
    name = photo.get("name") or photo.get("src")
    if not name:
        raise GalleryError("Every photo needs a `name` field.")

    result: dict[str, Any] = {"src": str(name)}
    for key in ("thumbnail", "thumb", "alt", "caption", "ratio"):
        value = photo.get(key)
        if value not in (None, ""):
            result[key] = value

    map_url = photo.get("map")
    if map_url not in (None, ""):
        result["map"] = map_url
    else:
        gmap = photo.get("gmap")
        if gmap not in (None, ""):
            result["map"] = f"https://maps.app.goo.gl/{gmap}"

    return result


def collection_front_matter(data: dict[str, Any]) -> dict[str, Any]:
    required = ("title", "date", "location", "media_subpath")
    front_matter: dict[str, Any] = {}
    for key in required:
        value = data.get(key)
        if value in (None, ""):
            raise GalleryError(f"`{key}` is required.")
        front_matter[key] = value

    cover = data.get("cover")
    if cover not in (None, ""):
        front_matter["cover"] = cover

    photos = data.get("photos") or []
    if not isinstance(photos, list):
        raise GalleryError("`photos` must be a list.")
    front_matter["photos"] = [collection_photo(photo) for photo in photos]
    return front_matter


def render_markdown(data: dict[str, Any]) -> str:
    front_matter = collection_front_matter(data)
    body = data.get("body") or ""
    if not isinstance(body, str):
        raise GalleryError("`body` must be a string when provided.")

    markdown = f"---\n{dump_yaml(front_matter)}\n---\n"
    if body.strip():
        markdown += f"\n{body.rstrip()}\n"
    return markdown


def process_assets(data: dict[str, Any], yaml_dir: Path, args: argparse.Namespace) -> None:
    media_subpath = str(data.get("media_subpath") or "")
    asset_dir = media_dir_from_subpath(media_subpath)
    source_common = data.get("source_common")
    if source_common not in (None, ""):
        source_common = str(source_common)
    else:
        source_common = None

    photos = data.get("photos") or []
    if not isinstance(photos, list):
        raise GalleryError("`photos` must be a list.")

    conversion_needed = False
    for photo in photos:
        if not isinstance(photo, dict):
            raise GalleryError("Each photo entry must be a mapping.")
        target = resolve_target(asset_dir, str(photo.get("name") or photo.get("src") or ""))
        if args.force_assets or not target.exists():
            conversion_needed = True

    magick = find_magick(args.magick) if conversion_needed else ""

    if not args.dry_run:
        asset_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"ensure directory {asset_dir}")

    for photo in photos:
        target = resolve_target(asset_dir, str(photo.get("name") or photo.get("src") or ""))
        if target.exists() and not args.force_assets:
            print(f"keep existing {target}")
            continue

        source = resolve_source(photo, yaml_dir, source_common)
        if not source:
            raise GalleryError(
                f"{target.name} is missing and its photo entry has no `source`."
            )

        convert_image(
            magick=magick,
            source=source,
            target=target,
            max_bytes=args.max_bytes,
            max_edge=args.max_edge,
            min_edge=args.min_edge,
            quality=args.quality,
            min_quality=args.min_quality,
            dry_run=args.dry_run,
        )


def write_markdown(markdown: str, output: Path, dry_run: bool) -> None:
    output = output if output.is_absolute() else REPO_ROOT / output
    if dry_run:
        print(f"write markdown {output}")
        print(markdown)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    print(f"wrote {output}")


def main() -> int:
    args = parse_args()

    try:
        yaml_file = expand_path(args.yaml_file).resolve()
        data = load_yaml(yaml_file)
        output = args.output or default_output_path(data)

        if not args.no_assets:
            process_assets(data, yaml_file.parent, args)

        if not args.no_markdown:
            write_markdown(render_markdown(data), output, args.dry_run)

    except GalleryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
