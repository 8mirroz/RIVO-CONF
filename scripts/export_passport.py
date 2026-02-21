#!/usr/bin/env python3
import json
import sys
from datetime import datetime

PASSPORT_TEMPLATE = """# ТЕХНИЧЕСКИЙ ПАСПОРТ ИЗДЕЛИЯ
**Проект:** {project_id}
**Дата создания:** {date}
**Автор:** {author}

## 1. Спецификация (BOM)
{bom_table}

## 2. Размеры и характеристики каркаса
- Тип стены: {frame_type}
- Габариты (Ш х В х Г): {width} мм х {height} мм х {depth} мм
- Шаг стоек: {stud_step} мм

## 3. Гарантии и требования
- Гарантия на инсталляции RIVO Set — 10 лет.
- Рекомендуется фильтр механической очистки ≤ 100 мкм.
- Максимальное давление арматуры: ≤ 6 бар (ГОСТ 2874-82).

## 4. Правила монтажа (RIVO Fix)
Любая нагрузка от оборудования/обшивки должна иметь непрерывный путь передачи: оборудование → крепёж/узел → профиль → опора/анкер → основание.

---
Документ сгенерирован автоматически: {current_time}
"""

def generate_passport(rivo_config: dict, output_path: str):
    meta = rivo_config.get("meta", {})
    frame = rivo_config.get("frame", {})
    bom_lines = rivo_config.get("bom", {}).get("lines", [])

    bom_table = "| Артикул | Кол-во | Ед. изм. | Примечание |\n|---|---|---|---|\n"
    for line in bom_lines:
        bom_table += f"| {line.get('article', '')} | {line.get('qty', 0)} | {line.get('uom', 'шт')} | {line.get('comment', '')} |\n"

    report = PASSPORT_TEMPLATE.format(
        project_id=meta.get("projectId", "N/A"),
        date=meta.get("createdAt", "N/A"),
        author=meta.get("author", "N/A"),
        bom_table=bom_table,
        frame_type=frame.get("type", "N/A"),
        width=frame.get("width", 0),
        height=frame.get("height", 0),
        depth=frame.get("depth", 0),
        stud_step=frame.get("studStep", 0),
        current_time=datetime.now().isoformat()
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Passport successfully written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "../research/RIVO_Deliverables_Passport_DXF_IFC_JSON/05_sample_project.rivo.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        output_file = config_path.replace(".rivo.json", ".passport.md")
        generate_passport(config, output_file)
    except Exception as e:
        print(f"Error processing {config_path}: {e}")
