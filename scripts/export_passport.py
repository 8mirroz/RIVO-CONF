#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
- Гарантия на инсталляции RIVO Set - 10 лет.
- Рекомендуется фильтр механической очистки <= 100 мкм.
- Максимальное давление арматуры: <= 6 бар (ГОСТ 2874-82).

## 4. Правила монтажа (RIVO Fix)
Любая нагрузка от оборудования/обшивки должна иметь непрерывный путь передачи: оборудование -> крепеж/узел -> профиль -> опора/анкер -> основание.

---
Документ сгенерирован автоматически: {current_time}
"""


def _md_cell(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _build_bom_table(bom_lines: list[dict[str, Any]]) -> str:
    rows = ["| Артикул | Кол-во | Ед. изм. | Примечание |", "|---|---|---|---|"]
    for line in bom_lines:
        rows.append(
            "| {article} | {qty} | {uom} | {comment} |".format(
                article=_md_cell(line.get("article", "")),
                qty=_md_cell(line.get("qty", 0)),
                uom=_md_cell(line.get("uom", "шт")),
                comment=_md_cell(line.get("comment", "")),
            )
        )
    return "\n".join(rows)


def _derive_output_path(config_path: Path) -> Path:
    source = str(config_path)
    if source.endswith(".rivo.json"):
        return Path(source.removesuffix(".rivo.json") + ".passport.md")
    return config_path.with_suffix(config_path.suffix + ".passport.md")


def generate_passport(rivo_config: dict[str, Any], output_path: Path) -> Path:
    if not isinstance(rivo_config, dict):
        raise ValueError("rivo_config must be a dictionary")

    meta = rivo_config.get("meta", {}) if isinstance(rivo_config.get("meta"), dict) else {}
    frame = rivo_config.get("frame", {}) if isinstance(rivo_config.get("frame"), dict) else {}
    bom = rivo_config.get("bom", {}) if isinstance(rivo_config.get("bom"), dict) else {}
    bom_lines = [line for line in bom.get("lines", []) if isinstance(line, dict)] if isinstance(bom.get("lines"), list) else []

    report = PASSPORT_TEMPLATE.format(
        project_id=meta.get("projectId", "N/A"),
        date=meta.get("createdAt", "N/A"),
        author=meta.get("author", "N/A"),
        bom_table=_build_bom_table(bom_lines),
        frame_type=frame.get("type", "N/A"),
        width=frame.get("width", 0),
        height=frame.get("height", 0),
        depth=frame.get("depth", 0),
        stud_step=frame.get("studStep", 0),
        current_time=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )

    output_path.write_text(report, encoding="utf-8")
    return output_path


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown technical passport from Rivo export JSON.")
    parser.add_argument("config", help="Path to .rivo.json (or compatible) input file.")
    parser.add_argument("-o", "--output", help="Output markdown path. Default: <input>.passport.md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    config_path = Path(args.config)
    output_path = Path(args.output) if args.output else _derive_output_path(config_path)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        written = generate_passport(config, output_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
