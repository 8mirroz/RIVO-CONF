#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _derive_output_path(config_path: Path) -> Path:
    source = str(config_path)
    if source.endswith(".rivo.json"):
        return Path(source.removesuffix(".rivo.json") + ".dxf")
    return config_path.with_suffix(".dxf")


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _point_xy(value: Any) -> tuple[float, float]:
    point = value if isinstance(value, dict) else {}
    return (_as_float(point.get("x", 0.0)), _as_float(point.get("y", 0.0)))


def _layer_for_article(article: str) -> str:
    return "RIVO_PROFILE" if str(article).startswith("100001") else "RIVO_CONNECTORS"


def _sorted_elements(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items = [item for item in value if isinstance(item, dict)]
    return sorted(items, key=lambda e: (str(e.get("id", "")), str(e.get("article", ""))))


def generate_dxf_stub(rivo_config: dict[str, Any], output_path: Path) -> Path:
    """
    Generate DXF with ezdxf, or a deterministic text preview when ezdxf is absent.
    """
    if not isinstance(rivo_config, dict):
        raise ValueError("rivo_config must be a dictionary")

    elements = _sorted_elements(rivo_config.get("elements"))

    try:
        import ezdxf
    except ImportError:
        lines = [
            "DXF MAPPING PREVIEW",
            "LAYERS: RIVO_PROFILE,RIVO_CONNECTORS,RIVO_SUPPORTS,RIVO_EQUIPMENT,RIVO_AXES,RIVO_DIMS,RIVO_TEXT",
        ]
        for elem in elements:
            art = str(elem.get("article", ""))
            layer = _layer_for_article(art)
            geom = elem.get("geom", {}) if isinstance(elem.get("geom"), dict) else {}
            lines.append(f"LAYER={layer};ART={art};GEOM_TYPE={geom.get('type', '')}")

        preview_path = output_path.with_suffix(output_path.suffix + ".txt")
        preview_path.write_text("\n".join(lines), encoding="utf-8")
        return preview_path

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4  # millimeters
    for name, color in (
        ("RIVO_PROFILE", 7),
        ("RIVO_CONNECTORS", 3),
        ("RIVO_SUPPORTS", 2),
        ("RIVO_EQUIPMENT", 4),
        ("RIVO_AXES", 1),
        ("RIVO_DIMS", 5),
        ("RIVO_TEXT", 7),
    ):
        if name not in doc.layers:
            doc.layers.add(name=name, color=color)

    msp = doc.modelspace()
    for elem in elements:
        article = str(elem.get("article", ""))
        layer = _layer_for_article(article)
        geom = elem.get("geom", {}) if isinstance(elem.get("geom"), dict) else {}
        geom_type = str(geom.get("type", "")).lower()

        if geom_type == "segment":
            start = _point_xy(geom.get("start"))
            end = _point_xy(geom.get("end"))
            msp.add_line(start, end, dxfattribs={"layer": layer})
        elif geom_type == "point":
            point = _point_xy(geom.get("point"))
            msp.add_text(
                f"ART:{article}",
                dxfattribs={"layer": "RIVO_TEXT", "insert": point, "height": 2.5},
            )

    doc.saveas(output_path)
    return output_path


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate DXF (or preview) from Rivo export JSON.")
    parser.add_argument("config", help="Path to .rivo.json (or compatible) input file.")
    parser.add_argument("-o", "--output", help="Output DXF path. Default: <input>.dxf")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    config_path = Path(args.config)
    output_path = Path(args.output) if args.output else _derive_output_path(config_path)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        written = generate_dxf_stub(config, output_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
