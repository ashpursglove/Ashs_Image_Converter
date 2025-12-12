"""
modules/image_ops.py

All image processing lives here (Pillow).
Keeps GUI code clean and makes it easy to unit test later.

Features:
- Read image with optional EXIF auto-rotate
- Optional metadata stripping
- Resize modes: contain, cover, stretch
- Transparency flattening when converting to non-alpha formats
- Save formats with quality/optimize options
- Multi-size ICO builder
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from PIL import Image, ImageOps


# ---------- Types & Settings ----------

SUPPORTED_INPUT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
SUPPORTED_OUTPUT = {"PNG", "JPEG", "WEBP", "BMP", "TIFF"}  # PIL format names


class ResizeMode:
    CONTAIN = "Fit inside (contain)"
    COVER = "Fill and crop (cover)"
    STRETCH = "Stretch (no aspect lock)"


@dataclass(frozen=True)
class ConvertSettings:
    output_format: str  # PIL format name, e.g. "PNG", "JPEG"
    output_dir: Path
    name_mode: str  # "keep" | "prefix" | "suffix"
    name_text: str  # prefix/suffix text
    auto_number_collisions: bool

    resize_enabled: bool
    width: int
    height: int
    keep_aspect: bool
    resize_mode: str  # from ResizeMode
    do_not_upscale: bool

    quality: int  # 1..100 for JPEG/WEBP
    optimize: bool  # png/webp optimization-ish

    strip_metadata: bool
    autorotate_exif: bool

    flatten_bg_rgb: Tuple[int, int, int]  # used when transparency -> non-alpha


@dataclass(frozen=True)
class ConvertResult:
    src: Path
    dst: Optional[Path]
    ok: bool
    message: str


# ---------- Helpers ----------

def is_supported_input(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_INPUT


def _safe_open_image(path: Path, autorotate_exif: bool) -> Image.Image:
    """
    Opens an image robustly.
    GIFs: will load first frame only (practical for conversion/thumbnailing).
    """
    img = Image.open(str(path))
    if autorotate_exif:
        # exif_transpose handles orientation tags if present
        img = ImageOps.exif_transpose(img)
    # Ensure we have pixels loaded (especially for lazy formats)
    img.load()
    return img


def _strip_metadata(img: Image.Image) -> Image.Image:
    """
    Removes metadata by rebuilding the image pixel data.
    This drops EXIF and most ancillary info.
    """
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    return clean


def _has_alpha(img: Image.Image) -> bool:
    if img.mode in ("RGBA", "LA"):
        return True
    if img.mode == "P" and "transparency" in img.info:
        return True
    return False


def _flatten_transparency(img: Image.Image, bg_rgb: Tuple[int, int, int]) -> Image.Image:
    """
    Flattens alpha onto a solid background.
    """
    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, bg_rgb + (255,))
    out = Image.alpha_composite(bg, img.convert("RGBA"))
    return out.convert("RGB")


def _resize(img: Image.Image, width: int, height: int, keep_aspect: bool, mode: str, do_not_upscale: bool) -> Image.Image:
    """
    Applies resize behavior per settings.
    """
    if width <= 0 or height <= 0:
        return img

    src_w, src_h = img.size
    if do_not_upscale and src_w <= width and src_h <= height:
        return img

    if not keep_aspect or mode == ResizeMode.STRETCH:
        return img.resize((width, height), resample=Image.LANCZOS)

    if mode == ResizeMode.CONTAIN:
        # Fit inside target
        return ImageOps.contain(img, (width, height), method=Image.LANCZOS)

    if mode == ResizeMode.COVER:
        # Fill and crop to exact
        return ImageOps.fit(img, (width, height), method=Image.LANCZOS, centering=(0.5, 0.5))

    # Fallback to contain
    return ImageOps.contain(img, (width, height), method=Image.LANCZOS)


def _resolve_output_name(src: Path, settings: ConvertSettings) -> str:
    stem = src.stem
    if settings.name_mode == "prefix" and settings.name_text:
        return f"{settings.name_text}{stem}"
    if settings.name_mode == "suffix" and settings.name_text:
        return f"{stem}{settings.name_text}"
    return stem


def _unique_path(path: Path) -> Path:
    """
    If path exists, append _001 style numbering.
    """
    if not path.exists():
        return path
    base = path.with_suffix("")
    ext = path.suffix
    i = 1
    while True:
        candidate = Path(f"{base}_{i:03d}{ext}")
        if not candidate.exists():
            return candidate
        i += 1


def estimate_output_path(src: Path, settings: ConvertSettings) -> Path:
    ext_map = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WEBP": ".webp",
        "BMP": ".bmp",
        "TIFF": ".tiff",
    }
    out_stem = _resolve_output_name(src, settings)
    dst = settings.output_dir / f"{out_stem}{ext_map[settings.output_format]}"
    if settings.auto_number_collisions:
        dst = _unique_path(dst)
    return dst


# ---------- Main operations ----------

def convert_one(src: Path, settings: ConvertSettings) -> ConvertResult:
    try:
        if not src.exists():
            return ConvertResult(src=src, dst=None, ok=False, message="File not found")

        if not is_supported_input(src):
            return ConvertResult(src=src, dst=None, ok=False, message="Unsupported input format")

        img = _safe_open_image(src, settings.autorotate_exif)

        if settings.strip_metadata:
            img = _strip_metadata(img)

        if settings.resize_enabled:
            img = _resize(
                img=img,
                width=settings.width,
                height=settings.height,
                keep_aspect=settings.keep_aspect,
                mode=settings.resize_mode,
                do_not_upscale=settings.do_not_upscale,
            )

        dst = estimate_output_path(src, settings)

        out_format = settings.output_format

        # Handle transparency if output doesn't support alpha (JPEG/BMP typically)
        if out_format in ("JPEG", "BMP") and _has_alpha(img):
            img = _flatten_transparency(img, settings.flatten_bg_rgb)

        save_kwargs = {}

        if out_format == "JPEG":
            # JPEG must be RGB/L
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            save_kwargs.update({"quality": settings.quality, "optimize": settings.optimize})

        if out_format == "WEBP":
            save_kwargs.update({"quality": settings.quality, "method": 6})
            if settings.optimize:
                save_kwargs.update({"lossless": False})

        if out_format == "PNG":
            # Pillow "optimize" tries to reduce size; works but can be slower
            save_kwargs.update({"optimize": settings.optimize})

        if out_format == "TIFF":
            # Reasonable default compression
            save_kwargs.update({"compression": "tiff_deflate" if settings.optimize else "raw"})

        settings.output_dir.mkdir(parents=True, exist_ok=True)
        img.save(str(dst), format=out_format, **save_kwargs)

        return ConvertResult(src=src, dst=dst, ok=True, message="OK")
    except Exception as e:
        return ConvertResult(src=src, dst=None, ok=False, message=str(e))


def build_multisize_ico(src: Path, dst: Path, sizes: Sequence[int], autorotate_exif: bool, strip_metadata: bool) -> None:
    """
    Generates a proper multi-size .ico.
    Uses Pillow's ICO writer with a sizes list.
    """
    img = _safe_open_image(src, autorotate_exif)

    if strip_metadata:
        img = _strip_metadata(img)

    # ICO likes RGBA
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")

    # Ensure output folder exists
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Pillow wants list of (w, h)
    ico_sizes = [(s, s) for s in sorted(set(int(x) for x in sizes if int(x) > 0))]
    if not ico_sizes:
        raise ValueError("No icon sizes selected")

    img.save(str(dst), format="ICO", sizes=ico_sizes)
