# RIVO Fix Configurator — Master Pack (из всей беседы)

Дата сборки: 2026-02-21

## Что внутри

### 1) `source_inputs/`
Исходные файлы, которые были предоставлены в ходе беседы (как есть), включая:
- инженерные PDF и модели
- UX/UI исследования
- системный стек/архитектура
- сценарии пользователя
- индексы ссылок

### 2) `docs/`
Консолидированная документация по системе (production-ready подход):
- Product Schema / Product Model
- Constraint DSL + Explainable Validation
- Solution Engine (reverse configuration)
- CPQ (Pricing + BOM)
- API Contract (REST)
- DB Schema + Versioning
- UI/UX ТЗ (отдельное задание для UI/UX агента)
- Roadmap до enterprise

### 3) `project_scaffold/`
Каркас репозитория (структура папок и “точки расширения”).
Это **не полнофункциональный код**, а scaffolding, чтобы инженер/агенты могли быстро развернуть реальный проект по документации.

## Как использовать

1. Начать с `docs/00_INDEX.md`
2. Согласовать Product Model → Constraints → CPQ → API → UI → 3D → Order → Integrations
3. На основе `project_scaffold/` развернуть реальный репозиторий.

## Важно

- Логика/валидация и цена должны жить на сервере.
- UI никогда не должен позволять невалидный выбор.
- 3D получает только validated snapshot → render state.

