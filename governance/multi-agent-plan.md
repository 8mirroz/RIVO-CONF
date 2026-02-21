# RIVO CONF — Анализ папки research и план мультиагентной разработки

Дата: 2026-02-21

## 1. Что уже готово в `research/`
Сильные стороны текущего пакета:
- описаны целевая архитектура и roadmap (`docs/01`, `docs/09`),
- есть каркас product model (`docs/02`),
- зафиксированы типы правил DSL и explainability (`docs/03`),
- задан reverse engine pipeline (`docs/04`),
- описаны CPQ и черновой REST-контракт (`docs/05`, `docs/06`),
- есть snapshot/versioning модель БД (`docs/08`),
- задано подробное UI/UX ТЗ и сценарии (`docs/07`, `configurator_uiux_research.md`).

## 2. Критичные пробелы
Пакет готов для проектирования, но не для немедленного прод-кодинга:
- `project_scaffold/` почти пустой, runtime-кода нет,
- OpenAPI не формализован до строгих схем,
- нет исполняемых наборов catalog/rules/pricing,
- нет модели ownership по файлам для параллельных агентов,
- нет CI-гейтов, replay-регрессий и release-governance.

## 3. Риски при старте без правил
- расхождение контрактов между UI, solver, CPQ и export,
- коллизии PR при параллельной правке shared-артефактов,
- неустойчивость snapshot replay из-за версионных дрейфов,
- перенос бизнес-логики во frontend,
- поздние интеграционные падения на этапе E2E.

## 4. Разделение ролей без пересечений
1. Orchestrator Agent
Выходы: dependency graph, план релизных волн, merge-порядок.

2. Product Modeling Agent
Выходы: схемы атрибутов, справочники, правила версионирования.

3. Constraint Engine Agent
Выходы: rule packs, pipeline валидации, explainability payload.

4. CPQ/API Agent
Выходы: OpenAPI, pricing/BOM модули, snapshot API.

5. UI/3D Agent
Выходы: guided/reverse интерфейсы, интеграция viewer через validated snapshot.

6. Quality Gates Agent
Выходы: CI-матрица, replay-тесты, release checklist.

## 5. Contract-first последовательность
1. Утвердить канонические схемы:
- `ConfigurationSnapshot`
- `ValidationResultItem`
- `PriceQuote`
- `BomItem`
- `StructureGraph`

2. Зафиксировать OpenAPI v1 для:
- `/api/solutions/generate`
- `/api/configuration/validate`
- `/api/cpq/calculate`
- `/api/export/pdf|dxf|ifc`

3. Реализовать доменные адаптеры:
- solver,
- CPQ,
- viewer mapping.

4. Добавить replay-тесты snapshot на совместимость версий.

## 6. Детальный план на 12 недель
### Phase 0 — Foundation (Неделя 1)
- Развернуть реальный монорепо-каркас на базе scaffold.
- Добавить ownership map и skeleton CI.
- Заморозить v1-контракты и schema IDs.
Критерий выхода: проект запускается и тестируется одной командой, контракты опубликованы.

### Phase 1 — Core Domain Engine (Недели 2-4)
- Собрать v1 dataset product model.
- Реализовать HARD/AUTO/SOFT pipeline.
- Реализовать reverse generation (2-3 валидных кандидата).
Критерий выхода: детерминированная генерация и валидация на фиксированных входах.

### Phase 2 — CPQ + Snapshot Backbone (Недели 5-6)
- Серверный расчет цены и BOM из `StructureGraph`.
- Персистентный snapshot с version tags.
- Поддержка compare/undo-ready version storage.
Критерий выхода: одинаковый snapshot при одинаковых версиях дает одинаковый CPQ-результат.

### Phase 3 — UX + Viewer Integration (Недели 7-9)
- Guided wizard и reverse режим.
- Explainable ошибки с suggested fixes.
- Viewer работает только от validated snapshot.
Критерий выхода: E2E путь от требований до summary и preview.

### Phase 4 — Export + Stabilization (Недели 10-11)
- MVP PDF export.
- Базовый DXF export.
- Полный smoke/regression набор.
Критерий выхода: стабильная выгрузка и зеленые регрессии.

### Phase 5 — Release Readiness (Неделя 12)
- Security/performance проход.
- Freeze документации и runbooks.
- Rollback план и demo-сценарии.
Критерий выхода: checklist релиза закрыт.

## 7. Merge-стратегия без конфликтов
- Узкие PR внутри одного домена.
- Сначала контрактные PR, потом реализация.
- Ежедневная интеграционная пачка.
- Еженедельный stabilization freeze.
- Cross-domain PR только с approval orchestrator.

## 8. Минимальные quality gates
1. Проверка schema/type.
2. Unit-тесты домена.
3. Snapshot replay тест.
4. Contract compatibility diff.
5. Critical smoke E2E:
`requirements -> generate -> validate -> cpq -> export`.

## 9. Первый исполнимый backlog (по приоритету)
1. Реальный репозиторий из scaffold.
2. Канонические JSON Schema + OpenAPI.
3. Seed-данные catalog/rules/pricing из инженерных материалов.
4. API валидации и reverse solver.
5. API CPQ/BOM.
6. Frontend shell для guided/reverse.
7. Viewer mapping от validated state.
8. PDF export.
9. DXF export.
10. Базовые audit/observability артефакты.

## 10. Как использовать созданные skills
- `rivo-multi-agent-orchestrator`: декомпозиция, зависимости, merge-порядок.
- `rivo-product-modeling`, `rivo-constraint-engine`, `rivo-cpq-and-api`, `rivo-ui-3d-experience`: реализация по доменам.
- `rivo-quality-gates`: обязательная валидация перед merge/release.
