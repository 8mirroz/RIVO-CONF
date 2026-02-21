#!/usr/bin/env python3
import json
import sys

def generate_dxf_stub(rivo_config: dict, output_path: str):
    """
    Generates a primitive structured text output or actual DXF via ezdxf 
    representing the Structural DXF Spec for RIVO Fix.
    """
    elements = rivo_config.get("elements", [])
    
    try:
        import ezdxf
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4  # Millimeters
        
        # Setup layers
        layers = [
            ("RIVO_PROFILE", 7), ("RIVO_CONNECTORS", 3), 
            ("RIVO_SUPPORTS", 2), ("RIVO_EQUIPMENT", 4),
            ("RIVO_AXES", 1), ("RIVO_DIMS", 5), ("RIVO_TEXT", 7)
        ]
        for name, color in layers:
            doc.layers.add(name=name, color=color)

        msp = doc.modelspace()

        for elem in elements:
            art = elem.get("article", "")
            # Basic mapping logic based on layer
            layer = "RIVO_PROFILE" if art.startswith("100001") else "RIVO_CONNECTORS"
            
            geom = elem.get("geom", {})
            if geom.get("type") == "segment":
                start = geom.get("start", {"x":0,"y":0,"z":0})
                end = geom.get("end", {"x":0,"y":0,"z":0})
                msp.add_line((start["x"], start["y"]), (end["x"], end["y"]), dxfattribs={"layer": layer})
            elif geom.get("type") == "point":
                pos = geom.get("point", {"x":0,"y":0,"z":0})
                msp.add_text(f"ART:{art}", dxfattribs={"layer": "RIVO_TEXT"}).set_placement((pos["x"], pos["y"]))

        doc.saveas(output_path)
        print(f"Real DXF generated at {output_path} (ezdxf)")
    except ImportError:
        # Fallback to pseudo-DXF mapping debug format
        print("ezdxf not installed. Generating DXF mapping preview text.")
        lines = []
        lines.append("DXF MAPPING PREVIEW (Layers: RIVO_PROFILE, RIVO_CONNECTORS, RIVO_SUPPORTS, RIVO_EQUIPMENT)")
        for elem in elements:
            art = elem.get("article", "")
            layer = "RIVO_PROFILE" if str(art).startswith("100") else "RIVO_EQUIPMENT"
            geom = elem.get("geom", {})
            lines.append(f"LAYER: {layer} | ART: {art} | GEOM_TYPE: {geom.get('type')}")
        
        with open(output_path + ".txt", 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"Fallback DXF text preview generated at {output_path}.txt")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "../research/RIVO_Deliverables_Passport_DXF_IFC_JSON/05_sample_project.rivo.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        output_file = config_path.replace(".rivo.json", ".dxf")
        generate_dxf_stub(config, output_file)
    except Exception as e:
        print(f"Error processing {config_path}: {e}")
