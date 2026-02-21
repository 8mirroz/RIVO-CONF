import json

path1 = 'research/RIVO_Deliverables_Passport_DXF_IFC_JSON/05_sample_project.rivo.json'

with open(path1, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data.get('catalog', {}).get('items', []):
    item['imageRef'] = f"images/{item['article']}.png"

with open(path1, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated 05_sample_project.rivo.json")
