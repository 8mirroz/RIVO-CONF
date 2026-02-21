#!/usr/bin/env python3
import json
import sys

def generate_ifc_stub(rivo_config: dict, output_path: str):
    """
    Generates a primitive structured text output or actual IFC via ifcopenshell 
    representing the IFC4 Mapping Spec for RIVO Fix.
    """
    elements = rivo_config.get("elements", [])
    meta = rivo_config.get("meta", {})

    try:
        import ifcopenshell
        # In a real environment, we would build the IfcProject hierarchy
        # Since ifcopenshell can be complex to bootstrap from scratch in a snippet,
        # we will assume the environment has an IFC boilerplate or we use mapping logs.
        raise ImportError("Use mapping fallback for IFC to avoid complex boilerplate")
    except ImportError:
        # Pseudo-IFC mapping debug format
        lines = ["IFC4 HIERARCHY MAPPING"]
        lines.append(f"IfcProject (ID: {meta.get('projectId', 'proj')})")
        lines.append("  IfcBuilding")
        lines.append("    IfcBuildingStorey")
        lines.append("      IfcElementAssembly (Name: RIVO_FIX_FRAME)")

        for elem in elements:
            art = str(elem.get("article", ""))
            
            if art.startswith("100001"):
                ifc_class = "IfcMember"
                pset = "Pset_RIVO_Common"
            elif art.startswith("100"):
                ifc_class = "IfcFastener"
                pset = "Pset_RIVO_Common"
            elif art.startswith("200") or art.startswith("201") or art.startswith("203"):
                ifc_class = "IfcSanitaryTerminal"
                pset = "Pset_RIVO_Set"
            elif art.startswith("30"):
                ifc_class = "IfcDiscreteAccessory"
                pset = "Pset_RIVO_Touch"
            else:
                ifc_class = "IfcBuildingElementProxy"
                pset = "Pset_Common"

            lines.append(f"        {ifc_class} | ART: {art} | Pset: {pset} | ID: {elem.get('id')}")

        with open(output_path + ".txt", 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"IFC Hierarchy mapping preview generated at {output_path}.txt")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "../research/RIVO_Deliverables_Passport_DXF_IFC_JSON/05_sample_project.rivo.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        output_file = config_path.replace(".rivo.json", ".ifc")
        generate_ifc_stub(config, output_file)
    except Exception as e:
        print(f"Error processing {config_path}: {e}")
