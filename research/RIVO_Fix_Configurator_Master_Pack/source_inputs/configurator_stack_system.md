# Конфигуратор (2D/3D + CPQ) — референсная система (v1→v3)

Дата: 2026-02-21  
Цель: собрать технологический стек и архитектуру конфигуратора в единую систему: UI → правила/ограничения → расчет → визуализация → артефакты → заказ/интеграции.

---

## 1) Что именно мы строим (термины и слои)

**Конфигуратор** в индустриальном смысле = связка 3-х подсистем:

1) **Guided UI (витрина)**  
   Панели атрибутов/шагов, объяснение ограничений, цена/срок, сравнение вариантов, история.

2) **Configuration Engine (мозг)**  
   - *Rule-based*: if/then бизнес-правила и зависимости  
   - *Constraint-based (CSP/CP/SAT/SMT)*: переменные + домены + ограничения, интерактивное поддержание валидности

3) **CPQ / Output (коммерческая часть)**  
   Цена, BOM, коммерческое, спецификация, PDF, экспорт в ERP/CRM/e-commerce.

Опциональные надстройки:
- **Parametric CAD** (если нужно генерировать геометрию для производства)
- **AR/VR** (WebXR/Native)

---

## 2) Референсная архитектура (модули и границы)

### 2.1 High-level diagram (слои)
1. **Web/App UI** (Next.js/React)  
2. **State & Session** (конфигурация, undo/redo, снапшоты)  
3. **Config API** (backend)  
4. **Configuration Engine** (rules/constraints)  
5. **Pricing/BOM Engine**  
6. **Asset/3D Pipeline** (glTF, компрессия, CDN)  
7. **Documents/Exports** (PDF/spec/quote)  
8. **Integrations** (PIM/ERP/CRM/Payments)

### 2.2 Микросервисы / домены (рекомендуемая разбивка)
- **catalog-service**  
  Продукты, атрибуты, домены значений, локализация, версии.
- **config-service**  
  Сессии конфигурации, валидатор, объяснения ошибок, снапшоты, сравнение.
- **rules-engine** (может быть библиотека внутри config-service)  
  Интерпретатор правил или мост к solver.
- **pricing-bom-service**  
  Цены, скидки, валюта, сроки, BOM, спецификации.
- **render-service** (опционально)  
  Серверный рендер превью/картинок, пакетная генерация.
- **asset-service**  
  Управление glTF, текстурами, метаданными, версиями и CDN.
- **document-service**  
  PDF / DOCX / JSON exports (quote, spec, assembly list).
- **integration-service**  
  ERP/CRM/PIM/Commerce adapters.

Для v1 допускается монолит (один backend), но **границы доменов** лучше держать.

---

## 3) Данные и контракты (ключевые сущности)

### 3.1 Product Model (каталог)
**ProductFamily**
- id, name, locale
- attributes[] (набор параметров)
- rulesetId (какие правила применяются)
- pricingModelId
- assetPackId

**Attribute**
- key (например `width`)
- type: enum | number | boolean | string | material | module
- domain (список допустимых или диапазон)
- ui: label, group, step, componentHint (select/slider/swatch)
- dependencies (опционально, если rule-based)

**Domain**
- enumValues[] (с метаданными: label, swatch, priceDelta, assetRef)
- numberRange: min, max, step, units

**AssetPack**
- gltfRefs[] (части модели)
- materialLibrary
- cameraPresets
- environmentPresets (HDRI)
- LOD presets

---

### 3.2 Configuration Session (то, что выбирает пользователь)
**Configuration**
- id (uuid)
- productFamilyId
- locale, currency
- selections: { [attributeKey]: value }
- derived: { price, bom, warnings, leadTime }
- validity: valid|invalid
- explanation: list of constraint messages
- history[] (undo/redo)
- createdAt, updatedAt
- versionTag (для воспроизводимости)

**ConstraintMessage**
- code (например `WIDTH_TOO_LARGE_FOR_MODULE_X`)
- severity: error|warning|info
- message (локализуемый)
- relatedAttributes[]
- suggestedFixes[] (опционально)

---

### 3.3 Pricing/BOM
**PriceQuote**
- basePrice
- lineItems[] (component, delta, qty)
- discounts, taxes, totals
- currency
- rulesApplied[]

**BOM**
- items[] { sku, name, qty, unit, options, notes }
- revision
- exportFormats: JSON/CSV

---

## 4) Логика конфигурации: rule-based vs constraint-based

### 4.1 Rule-based (быстрый старт)
Используйте, когда:
- атрибутов мало (до ~20–30)
- ограничений немного, они простые
- допускается частичная ручная проверка комбинаций

Формат правил (пример):
- IF material == "oak" THEN maxWidth = 2400
- IF module == "A" AND height > 2800 THEN disableOption("B")

Плюсы: проще дебажить, проще авторить бизнесу  
Минусы: быстро разрастается и становится хрупко

### 4.2 Constraint-based (правильный путь для сложных изделий)
Используйте, когда:
- много взаимосвязанных ограничений
- модульность, совместимость частей, заводские допуски
- нужна интерактивность: мгновенно показывать допустимые значения

Концепция:
- переменные: width, height, module, material, ...
- домены: диапазоны/наборы
- ограничения: совместимость, геометрия, производство, цена

Инструменты:
- OR-Tools (CP-SAT)
- Z3 (SMT)
- MiniZinc (моделирование)

---

## 5) 3D стек: pipeline и runtime

### 5.1 Runtime (браузер)
- Next.js + React
- Three.js (или react-three-fiber)
- drei + postprocessing
- PBR материалы, HDRI окружение
- камера/lighting presets

### 5.2 Ассеты
- glTF 2.0 как формат
- компрессия: Draco (геометрия), KTX2 (текстуры — по необходимости)
- LOD: низкий/средний/высокий
- структура модели: модульные части (nodes) с tag-метаданными

### 5.3 Визуальные режимы
- realtime (WebGL)
- server thumbnails (опционально)
- AR preview (опционально)

---

## 6) UI/UX система (guided selling)

### 6.1 Обязательные паттерны
- **Декомпозиция на шаги**: Base → Size → Materials → Modules → Accessories → Summary
- **Explainability**: “Почему недоступно?” + предлагаемый фикс
- **Progress + price feedback**: изменения цены и срока после каждого шага
- **History**: undo/redo, “вернуться к шагу”
- **Shareable config**: ссылка на конфигурацию (snapshot)

### 6.2 Компоненты интерфейса (минимальный набор)
- AttributePanel (группы атрибутов)
- OptionCard / Swatch / Slider
- ConfigSummary (цена/срок/ошибки)
- CompatibilityBanner (ошибки/предупреждения)
- ViewerToolbar (камера, explode, dimensions, reset)
- CompareDrawer (v2)
- ExportModal (PDF/BOM)

### 6.3 Motion (чтобы “дорого” выглядело)
- мягкие переходы между шагами
- micro-feedback при выборе (hover/press)
- skeleton на загрузку ассетов
- “smart scroll” и sticky summary

---

## 7) Backend стек (референс)

### Вариант A (JS/TS fullstack)
- Next.js (frontend)
- Node.js + NestJS/Fastify (backend)
- PostgreSQL (catalog/config snapshots)
- Redis (сессии/кеш допустимых доменов)
- S3-compatible storage + CDN (ассеты)
- Queue (BullMQ/Redis) для генерации превью/PDF

### Вариант B (Python engine + JS frontend)
- Next.js (frontend)
- FastAPI (backend)
- OR-Tools/Z3 (engine)
- PostgreSQL + Redis
- S3 + CDN

---

## 8) Версионность и воспроизводимость (критично)

### 8.1 Версия каталога
- productFamilyVersion (semver)
- rulesetVersion (semver)
- pricingVersion (semver)
- assetPackVersion (semver)

### 8.2 Snapshot
Каждый shared link должен хранить:
- selections
- версии каталога/правил/прайса/ассетов
- locale/currency
- computed derived (опционально, но полезно для истории)

---

## 9) Безопасность и качество (минимальные требования)

### 9.1 Перформанс
- LCP < 2.5s (лендинги)
- TTI / интерактивность < 3–4s
- конфиг-операция (пересчет доменов/валидности): < 150ms на горячем кеше
- загрузка 3D ассетов: progressive + LOD

### 9.2 Тесты
- unit: rules/pricing/bom
- property-based: генерация случайных конфигураций и проверка валидности
- e2e: сценарии “собрать → заказать”
- визуальные: screenshot regression (3D превью и UI)

### 9.3 Наблюдаемость
- трассировка пересчетов (engine latency)
- лог ошибок правил
- метрики конверсии по шагам

---

## 10) План реализации: v1 → v3

### v1 (4–8 недель, MVP)
- Rule-based engine (простые зависимости)
- Web UI + 3D viewer
- price estimate + basic BOM
- shareable snapshot link
- админка: загрузка ассетов + таблица атрибутов/опций

### v2 (следующий этап)
- Constraint-based engine (solver) или гибрид
- explainability + suggested fixes
- сравнение конфигураций
- серверный рендер превью + PDF quote

### v3 (enterprise)
- CAD-parametric генерация (если нужно производство)
- интеграции ERP/CRM/PIM
- multi-tenant, роли, аудит, workflow approvals

---

## 11) Практический “минимальный стек v1” (рекомендовано)

**Frontend**
- Next.js + TypeScript
- Tailwind + shadcn/ui (или эквивалент)
- Motion.dev (анимации)
- react-three-fiber + drei

**Backend**
- Fastify/NestJS или FastAPI
- PostgreSQL + Redis
- JSON schema контракты

**Logic**
- Rule-based DSL (JSON rules) + validator
- (подготовка) интерфейс для будущего solver

**Assets**
- glTF pipeline + Draco
- CDN

---

## 12) Ссылки (ядро)
- Three.js examples: https://threejs.org/examples/
- react-three-fiber: https://github.com/pmndrs/react-three-fiber
- drei: https://github.com/pmndrs/drei
- glTF 2.0 spec: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Draco: https://github.com/google/draco
- KHR_draco_mesh_compression: https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_draco_mesh_compression/README.md
- OR-Tools CP: https://developers.google.com/optimization/cp
- Z3: https://github.com/Z3Prover/z3
- MiniZinc: https://www.minizinc.org/
- Motion docs: https://motion.dev/docs
- Threekit Configurator API: https://developer.threekit.com/reference/configurator-api

---

## 13) Приложение: пример “контрактов” (минимально)

### 13.1 catalog.json (фрагмент)
```json
{
  "productFamilyId": "kitchen_v1",
  "version": "1.0.0",
  "attributes": [
    { "key": "width", "type": "number", "domain": { "min": 1200, "max": 3600, "step": 50, "unit": "mm" } },
    { "key": "material", "type": "enum", "domain": { "values": ["oak","walnut","white"] } }
  ]
}
```

### 13.2 rules.json (фрагмент, rule-based)
```json
[
  {
    "if": { "material": "oak" },
    "then": { "setMax": { "width": 2400 } },
    "explain": { "code": "OAK_MAX_WIDTH", "message": "Для дуба максимальная ширина 2400 мм." }
  }
]
```

### 13.3 config-session.json (фрагмент)
```json
{
  "id": "uuid",
  "productFamilyId": "kitchen_v1",
  "selections": { "width": 2500, "material": "oak" },
  "validity": "invalid",
  "explanation": [
    { "code": "OAK_MAX_WIDTH", "severity": "error", "relatedAttributes": ["width","material"] }
  ]
}
```
