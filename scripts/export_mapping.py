#!/usr/bin/env python3
import json
from uuid import uuid4
from datetime import datetime, timezone

def map_snapshot_to_export_config(snapshot_data: dict, project_id: str) -> dict:
    """
    Transforms a ConfigurationSnapshot into a RivoExportConfig format.
    - ConfigurationSnapshot contains `stateId`, `dimensions`, `graph`, `bom`
    - RivoExportConfig maps graph -> elements[], bom -> bom.lines[]
    """
    rivo_config = {
        "meta": {
            "projectId": project_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "units": "mm",
            "version": "1.0.0",
            "author": "RIVO Configurator"
        },
        "frame": {
            "type": "falsewall",
            "width": snapshot_data.get("dimensions", {}).get("width", 1200),
            "height": snapshot_data.get("dimensions", {}).get("height", 2500),
            "depth": snapshot_data.get("dimensions", {}).get("depth", 200),
            "studStep": 600,
            "origin": {"x": 0, "y": 0, "z": 0},
            "grid": {"snapMm": 1, "roundMm": 0.1},
            "constraints": {
                "maxWaterPressureBar": 6,
                "recommendedFilterMicron": 100,
                "waterStandard": "GOST 2874-82"
            }
        },
        "catalog": {
            "items": [] # Catalog items could be resolved via a registry
        },
        "elements": [],
        "bom": {
            "lines": snapshot_data.get("bom", [])
        },
        "views": {
            "front": {"mode": "cad", "dimensions": []},
            "side": {"mode": "cad", "dimensions": []}
        }
    }

    # Map StructureGraph edges and nodes to Elements array (simplified representation)
    graph = snapshot_data.get("graph", {})
    edges = graph.get("edges", [])
    
    # Normally, graph nodes hold the geometry and article data. We dummy map here.
    for i, edge in enumerate(edges):
        element = {
            "id": f"mapped-elem-{i}",
            "article": "100001.1", # Default placeholder
            "kind": "profile",
            "transform": {"pos": {"x": 0, "y": 0, "z": 0}, "rot": {"rx": 0, "ry": 0, "rz": 0}},
            "geom": {
                "type": "segment",
                "start": {"x": 0, "y": 0, "z": 0},
                "end": {"x": 0, "y": rivo_config["frame"]["height"], "z": 0}
            },
            "connections": [
                {"to": edge.get("to", ""), "type": edge.get("type", "corner")}
            ]
        }
        rivo_config["elements"].append(element)

    return rivo_config

if __name__ == "__main__":
    # Test mapping
    stub_snapshot = {
        "stateId": str(uuid4()),
        "dimensions": {"width": 900, "height": 2600, "depth": 150},
        "bom": [
            {"article": "100001.1", "qty": 2000, "uom": "mm", "comment": "Profile length"}
        ],
        "graph": {
            "rootNode": "root-1",
            "edges": [
                {"from": "root-1", "to": "child-1", "type": "inline"}
            ]
        }
    }
    out = map_snapshot_to_export_config(stub_snapshot, "demo-proj")
    print("Mapped Config:")
    print(json.dumps(out, indent=2))
