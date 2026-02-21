#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ARTICLE = "100001.1"
DEFAULT_FRAME = {"width": 1200, "height": 2500, "depth": 200}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _sorted_edges(graph: dict[str, Any]) -> list[dict[str, Any]]:
    edges = _as_list_of_dicts(graph.get("edges"))
    return sorted(
        edges,
        key=lambda e: (
            str(e.get("from", "")),
            str(e.get("to", "")),
            str(e.get("type", "")),
        ),
    )


def _sorted_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    raw_nodes = graph.get("nodes")
    if isinstance(raw_nodes, dict):
        nodes = [v for v in raw_nodes.values() if isinstance(v, dict)]
    else:
        nodes = _as_list_of_dicts(raw_nodes)
    return sorted(nodes, key=lambda n: str(n.get("id", "")))


def _default_segment(frame_height: int) -> dict[str, Any]:
    return {
        "type": "segment",
        "start": {"x": 0, "y": 0, "z": 0},
        "end": {"x": 0, "y": frame_height, "z": 0},
    }


def map_snapshot_to_export_config(snapshot_data: dict[str, Any], project_id: str) -> dict[str, Any]:
    """
    Transform ConfigurationSnapshot into RivoExportConfig.
    Keeps deterministic ordering for export stability.
    """
    if not isinstance(snapshot_data, dict):
        raise ValueError("snapshot_data must be a dictionary")
    if not project_id.strip():
        raise ValueError("project_id must not be empty")

    dimensions = _as_dict(snapshot_data.get("dimensions"))
    frame_height = _as_int(dimensions.get("height"), DEFAULT_FRAME["height"])

    rivo_config: dict[str, Any] = {
        "meta": {
            "projectId": project_id,
            "snapshotStateId": snapshot_data.get("stateId"),
            "createdAt": _utc_now_iso(),
            "units": "mm",
            "version": "1.0.0",
            "author": "RIVO Configurator",
        },
        "frame": {
            "type": "falsewall",
            "width": _as_int(dimensions.get("width"), DEFAULT_FRAME["width"]),
            "height": frame_height,
            "depth": _as_int(dimensions.get("depth"), DEFAULT_FRAME["depth"]),
            "studStep": 600,
            "origin": {"x": 0, "y": 0, "z": 0},
            "grid": {"snapMm": 1, "roundMm": 0.1},
            "constraints": {
                "maxWaterPressureBar": 6,
                "recommendedFilterMicron": 100,
                "waterStandard": "GOST 2874-82",
            },
        },
        "catalog": {"items": []},
        "elements": [],
        "bom": {"lines": _as_list_of_dicts(snapshot_data.get("bom"))},
        "views": {
            "front": {"mode": "cad", "dimensions": []},
            "side": {"mode": "cad", "dimensions": []},
        },
    }

    graph = _as_dict(snapshot_data.get("graph"))
    edges = _sorted_edges(graph)
    nodes = _sorted_nodes(graph)

    if nodes:
        outgoing_map: dict[str, list[dict[str, str]]] = {}
        for edge in edges:
            src = str(edge.get("from", ""))
            if not src:
                continue
            outgoing_map.setdefault(src, []).append(
                {"to": str(edge.get("to", "")), "type": str(edge.get("type", "corner"))}
            )

        for node in nodes:
            node_id = str(node.get("id", "")).strip() or f"node-{len(rivo_config['elements'])}"
            geom = _as_dict(node.get("geom")) or _default_segment(frame_height)
            element = {
                "id": node_id,
                "article": str(node.get("article", DEFAULT_ARTICLE)),
                "kind": str(node.get("kind", "profile")),
                "transform": _as_dict(node.get("transform"))
                or {"pos": {"x": 0, "y": 0, "z": 0}, "rot": {"rx": 0, "ry": 0, "rz": 0}},
                "geom": geom,
                "connections": outgoing_map.get(node_id, []),
            }
            rivo_config["elements"].append(element)
    else:
        for index, edge in enumerate(edges):
            element = {
                "id": f"mapped-elem-{index}",
                "article": DEFAULT_ARTICLE,
                "kind": "profile",
                "transform": {"pos": {"x": 0, "y": 0, "z": 0}, "rot": {"rx": 0, "ry": 0, "rz": 0}},
                "geom": _default_segment(frame_height),
                "connections": [{"to": edge.get("to", ""), "type": edge.get("type", "corner")}],
            }
            rivo_config["elements"].append(element)

    return rivo_config


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map ConfigurationSnapshot to RivoExportConfig JSON.")
    parser.add_argument("snapshot", help="Path to source snapshot JSON file.")
    parser.add_argument("--project-id", default="demo-proj", help="Project identifier for export metadata.")
    parser.add_argument(
        "--output",
        help="Output path for mapped JSON. If omitted, prints mapped JSON to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    snapshot_path = Path(args.snapshot)

    try:
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        mapped = map_snapshot_to_export_config(snapshot_data, args.project_id)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(mapped, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output_path)
    else:
        print(json.dumps(mapped, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
