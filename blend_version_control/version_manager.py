"""Lógica central para crear, listar y restaurar versiones de archivos .blend."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


VERSION_SUFFIX_PATTERN = re.compile(r"_v(\d{3,})$")
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


@dataclass(frozen=True)
class VersionEntry:
    path: Path
    label: str
    number: int | None
    modified: float
    size_bytes: int

    @property
    def modified_str(self) -> str:
        return datetime.fromtimestamp(self.modified).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def size_str(self) -> str:
        size = self.size_bytes
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
            size /= 1024
        return f"{size:.1f} GB"


def get_versions_dir(blend_path: str, custom_dir: str = "") -> Path | None:
    """Devuelve la carpeta donde se guardan las versiones."""
    if not blend_path:
        return None

    blend_file = Path(bpy_path(blend_path))
    if custom_dir.strip():
        base = Path(bpy_path(custom_dir)).expanduser()
        if not base.is_absolute():
            base = blend_file.parent / base
        return base / f".{blend_file.stem}_versions"

    return blend_file.parent / f".{blend_file.stem}_versions"


def bpy_path(path: str) -> str:
    """Normaliza rutas de Blender (// relative paths)."""
    import bpy

    return bpy.path.abspath(path)


def parse_version_number(filename_stem: str) -> int | None:
    match = VERSION_SUFFIX_PATTERN.search(filename_stem)
    if match:
        return int(match.group(1))
    return None


def next_version_number(versions_dir: Path, base_stem: str) -> int:
    highest = 0
    if versions_dir.is_dir():
        for item in versions_dir.glob(f"{base_stem}_v*.blend"):
            number = parse_version_number(item.stem)
            if number is not None:
                highest = max(highest, number)
    return highest + 1


def build_version_filename(base_stem: str, version_number: int) -> str:
    return f"{base_stem}_v{version_number:03d}.blend"


def build_timestamp_filename(base_stem: str) -> str:
    stamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return f"{base_stem}_{stamp}.blend"


def create_version(
    blend_path: str,
    *,
    custom_dir: str = "",
    use_timestamp: bool = False,
    note: str = "",
) -> Path:
    """Copia el .blend actual a la carpeta de versiones."""
    source = Path(bpy_path(blend_path))
    if not source.is_file():
        raise FileNotFoundError("Guarda el archivo antes de crear una versión.")

    versions_dir = get_versions_dir(blend_path, custom_dir)
    if versions_dir is None:
        raise ValueError("No hay un archivo .blend activo.")

    versions_dir.mkdir(parents=True, exist_ok=True)
    base_stem = source.stem

    if use_timestamp:
        target_name = build_timestamp_filename(base_stem)
    else:
        number = next_version_number(versions_dir, base_stem)
        target_name = build_version_filename(base_stem, number)

    target = versions_dir / target_name
    shutil.copy2(source, target)

    if note.strip():
        note_path = target.with_suffix(".txt")
        note_path.write_text(note.strip(), encoding="utf-8")

    return target


def list_versions(blend_path: str, custom_dir: str = "") -> list[VersionEntry]:
    """Lista versiones ordenadas de más reciente a más antigua."""
    versions_dir = get_versions_dir(blend_path, custom_dir)
    if versions_dir is None or not versions_dir.is_dir():
        return []

    source = Path(bpy_path(blend_path))
    base_stem = source.stem
    entries: list[VersionEntry] = []

    for item in sorted(versions_dir.glob("*.blend"), key=lambda p: p.stat().st_mtime, reverse=True):
        if not item.name.startswith(base_stem):
            continue

        stat = item.stat()
        number = parse_version_number(item.stem)
        label = item.name
        if number is not None:
            label = f"v{number:03d}"

        entries.append(
            VersionEntry(
                path=item,
                label=label,
                number=number,
                modified=stat.st_mtime,
                size_bytes=stat.st_size,
            )
        )

    return entries


def get_version_note(version_path: Path) -> str:
    note_path = version_path.with_suffix(".txt")
    if note_path.is_file():
        return note_path.read_text(encoding="utf-8").strip()
    return ""


def restore_version(version_path: Path) -> None:
    """Abre una versión anterior en una nueva ventana de Blender."""
    import bpy

    bpy.ops.wm.open_mainfile(filepath=str(version_path))


def prune_old_versions(
    blend_path: str,
    *,
    custom_dir: str = "",
    keep_count: int = 20,
) -> int:
    """Elimina versiones antiguas conservando las N más recientes."""
    if keep_count <= 0:
        return 0

    entries = list_versions(blend_path, custom_dir)
    removed = 0

    for entry in entries[keep_count:]:
        entry.path.unlink(missing_ok=True)
        note_path = entry.path.with_suffix(".txt")
        note_path.unlink(missing_ok=True)
        removed += 1

    return removed
