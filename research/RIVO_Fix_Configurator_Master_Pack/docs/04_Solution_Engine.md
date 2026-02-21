# 4. Solution Engine (Reverse configuration)

Вход: requirements (height/width/depth/load/mountingType/...)

Выход: 2–3 валидных solution snapshot:
- economic
- balanced
- reinforced

## 4.1 Алгоритм генерации кандидатов

1) Геометрическая декомпозиция (каркас)
2) Подбор профиля (по прочности/прогибу)
3) Расстановка опор/креплений (по правилам)
4) Построение StructureGraph
5) Валидация Constraint Engine
6) CPQ расчёт цены и BOM
7) Ранжирование кандидатов (по цели)

## 4.2 Структурный граф

```ts
interface StructureGraph {
  id: string;
  nodes: Node[];
  members: Member[];
  supports: Support[];
  fasteners: Fastener[];
  metadata: Record<string, any>;
}
```

## 4.3 UX-выдача

Карточка решения:
- цена
- safety factor
- вес
- количество узлов
- превью 3D
- кнопка “Выбрать” → детализация → экспорт

