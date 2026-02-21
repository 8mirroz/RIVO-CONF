# RIVO CONF — Правила мультиагентской разработки

## 1. Цель
Преобразовать исследовательский пакет RIVO Fix в production-кодовую базу через параллельную работу агентов без конфликтов по контрактам и файлам.

## 2. Приоритет источников истины
При противоречиях использовать порядок:
1. `research/RIVO_Fix_Configurator_Master_Pack/docs/00_INDEX.md`
2. `research/RIVO_Fix_Configurator_Master_Pack/docs/01_System_Architecture.md`
3. `research/RIVO_Fix_Configurator_Master_Pack/docs/02_Product_Model_Template.md`
4. `research/RIVO_Fix_Configurator_Master_Pack/docs/03_Constraint_DSL.md`
5. `research/RIVO_Fix_Configurator_Master_Pack/docs/04_Solution_Engine.md`
6. `research/RIVO_Fix_Configurator_Master_Pack/docs/05_CPQ.md`
7. `research/RIVO_Fix_Configurator_Master_Pack/docs/06_API_Contract.md`
8. `research/RIVO_Fix_Configurator_Master_Pack/docs/08_DB_Schema_and_Versioning.md`
9. `research/RIVO_Fix_Configurator_Master_Pack/docs/09_Roadmap.md`
10. `research/RIVO_Fix_Engineering_Model.md`

Если конфликт не снимается, создать решение в `governance/decisions/` до начала реализации.

## 3. Обязательные Skills
Использовать локальные skills по области задачи:
- `skills/rivo-multi-agent-orchestrator`
- `skills/rivo-product-modeling`
- `skills/rivo-constraint-engine`
- `skills/rivo-cpq-and-api`
- `skills/rivo-ui-3d-experience`
- `skills/rivo-quality-gates`

## 4. Топология агентов и маршрутизация (Adaptive Swarm)
- **Orchestrator** (Gemini 3.1 Pro): план, зависимости, окна интеграции.
- **Product Modeling** (GPT-5.3-Codex / Cline FREE): схема каталога, атрибуты, справочники.
- **Constraint Engine** (Gemini 3.1 Pro): сложная логика, DSL, explainable validation.
- **CPQ/API** (GPT-5.3-Codex): ценообразование, BOM, API-контракты.
- **UI/3D** (Claude Sonnet 4.5 / Gemini 3.1): guided/reverse UX, состояния, mapping.
- **Quality Gates** (Haiku 4.5 / Opus 4.6): тесты, регрессии, merge/release-гейты.

**Правила маршрутизации (Path):**
- Рутинные правки (C1-C2) делают бесплатные модели (Fast Path).
- Специфичные фичи (C3) делает Codex + Haiku (Quality Path).
- Кросс-доменные архитектурные изменения (C4-C5) оркестрируются Opus 4.6 (Swarm Path).

Привязка владения путями описана в `governance/ownership-map.yaml`.
Порядок включения и handoff skills описан в `governance/skills-map.md`.

## 5. Правила владения (жесткие)
- У каждого типа артефактов один ответственный домен.
- Изменения чужого домена в рамках задачи запрещены без явного запроса.
- Любые изменения контрактов (`OpenAPI`, schema, DSL, snapshot) делаются до реализации.
- Ломающие изменения контракта требуют version bump и migration notes.

## 6. Протокол веток и PR
- Формат ветки: `agent/<domain>/<ticket-or-scope>`.
- PR по возможности только в рамках одного домена.
- Перед ревью выполнить rebase; после старта ревью не делать force-push.
- Прямые коммиты в `main` запрещены.

Обязательные проверки PR:
1. Совместимость контрактов.
2. Тесты домена.
3. Snapshot replay тест.
4. Lint/type checks.
5. Changelog по доменному изменению.

## 7. Процедура предотвращения конфликтов
1. Опубликовать intent: файлы, выходы, затронутые контракты.
2. Зарезервировать ownership в таск-трекере.
3. Слить контрактный PR до кодовых PR.
4. Сливать реализации в порядке зависимостей.
5. После каждой пачки merge запускать integration smoke.

## 8. Каденс интеграции
- Ежедневное окно интеграции: только полностью зеленые PR.
- Еженедельное окно стабилизации: только bugfix/hardening.
- Freeze перед релизом: 48 часов, только blocker-fixes.

## 9. Definition of Done (глобально)
Задача завершена только если:
- валидация/цена/BOM считаются на сервере,
- UI не позволяет невалидный выбор и объясняет причину,
- 3D получает только validated snapshot,
- тесты и документация обновлены,
- в snapshot сохранены version tags (`catalog/rules/pricing/assets`).

## 10. Запрещенные анти-паттерны
- Ценообразование во frontend.
- Constraint-логика внутри viewer.
- Disabled без объяснения причины.
- Изменение контракта без версии.
- Мультидоменные mega-PR без согласования orchestrator.
