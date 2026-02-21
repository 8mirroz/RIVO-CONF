# Анализ проекта RIVO CONF и выбор базы (Scripts & Skills)

## 1. Контекст проекта
RIVO CONF — система для конфигурации продуктов с параллельной работой агентов без конфликтов по контрактам. 
Определены следующие домены (из `AGENTS.md`):
- **Orchestrator** (управление мультиагентской средой, планы, окна интеграции)
- **Product Modeling** (схема каталога, атрибуты, справочники, версии)
- **Constraint Engine** (DSL, explainable validation, auto-correct)
- **CPQ / API** (ценообразование, BOM, snapshot, контракты)
- **UI / 3D Experience** (пользовательский интерфейс, 3D-вьюер, guided/reverse UX)
- **Quality Gates** (тесты, регрессии, merge/release-гейты)

## 2. Отобранные скрипты (из `repos/`)
Мы будем использовать готовые DevOps и управляющие скрипты из `antigravity-core/repos/packages/agent-os`:
1. `swarmctl.py` — **Orchestrator**. Основной скрипт для запуска и контроля параллельной работы мультиагентной системы.
2. `run_integration_tests.sh` и `run_regression_suite.py` — **Quality Gates**. Необходимы для автоматизированного прогона тестов после каждого доменного PR. В `AGENTS.md` прописано окно ежедневной интеграции.
3. `run_smoke_checks.sh` — **Quality Gates**. Используется для быстрой проверки (smoke) работоспособности после мержей.
4. `active_set_lib.py` и `publish_active_set.py` — **CPQ / Product Modeling**. Инструменты для работы со snapshot-версиями и релизными слепками правил. Они необходимы для фиксации version tags перед отдачей данных в 3D UI.

## 3. Отобранные скиллы (из `repos/skills/`)
Из каталогов `antigravity-skills` и `antigravity-awesome-skills` берем стандартизованные скиллы, строго ложащиеся на топологию агентов в проекте:

* **Orchestrator**
  - `agent-orchestration-multi-agent-optimize` — для тонкой настройки слаженной работы параллельных узкоспециализированных агентов.
  - `workflow-orchestration-patterns` — для выстраивания пайплайнов выполнения (Integration & Handoff).

* **Product Modeling**
  - `database-architect` — для создания эффективной схемы хранения сложных справочников продуктов и системы версионирования.
  - `business-analyst` — для качественной формализации бизнес-логики каталога.

* **Constraint Engine**
  - `python-pro` / `rust-pro` — для разработки быстрого и надежного языка правил (Constraint DSL). Для сложной математики и графов ограничений это критично.
  - `backend-architect` — для архитектуры движка правил (с поддержкой explainable validation).

* **CPQ / API**
  - `openapi-spec-generation` и `api-design-principles` — для фиксации API-контрактов до начала реализации. Изменение контрактов — самый конфликтный момент, поэтому жестко нужен качественный API First подход.
  - `backend-development-feature-development` — расчет скидок и ценообразования строго на сервере.

* **UI / 3D Experience**
  - `3d-web-experience` и `threejs-skills` — профильные компетенции для создания визуализации продукта и маппинга конфигуратора на 3D сцену.
  - `ui-ux-designer` и `frontend-developer` — интерфейс, работающий по принципу "никогда не позволяем невалидный выбор" (guided UX). 

* **Quality Gates**
  - `playwright-skill` и `test-automator` — автоматизация e2e-тестирования фронтенда.
  - `performance-testing-review-multi-agent-review` — перформанс-ревью движка правил и конфигуратора при множестве атрибутов.
  - `security-compliance-compliance-check` — для проверок артефактов перед релизом.

## 4. Общий вывод
Архитектура проекта RIVO CONF четко разбивается на микродомены, где каждый этап может покрываться изолированным процессом. Использование стандартных скриптов по работе со snapshot/integration run из `agent-os` и узкопрофильных скиллов из базы `skills` закроет все потребности RIVO без необходимости переизобретать велосипед, что соответствует глобальному правилу **Reuse > Rebuild**.

## 5. Дополнительные скиллы для повышения эффективности (DX & Agent Ops)
Проект подразумевает сложную параллельную работу модулей. Чтобы агенты и разработчики не тратили время впустую, обязательно подключаем следующие вспомогательные скиллы:

**5.1. Управление контекстом и мультиагентностью**
- `subagent-driven-development` и `dispatching-parallel-agents` — критически важно для эффективной параллелизации задач (один агент пишет Constraint DSL, другой в этот момент мапит UI атрибуты).
- `context-driven-development` и `context-optimization` — строгие правила удержания контекста, чтобы агенты не ломали контракты из-за забытых вводных.
- `architecture-decision-records` — для формализации спорных моментов (например, при конфликтах контрактов, как описано в `AGENTS.md`) в папку `governance/decisions/`.

**5.2. Ускорение интеграции (CI/CD и Git)**
- `git-pr-workflows-git-workflow` и `git-pr-workflows-pr-enhance` — строгая формализация веток (`agent/<domain>/<ticket>`) и автоматическая проверка PR перед мержем.
- `github-actions-templates` / `gitlab-ci-patterns` — для настройки ежедневного интеграционного и еженедельного стабилизационного окна. 
- `turborepo-caching` — радикально ускоряет сборку и прогон smoke-тестов за счет кэширования нетронутых доменов.

**5.3. Гарантия качества (Quality Assurance & DX)**
- `code-review-excellence` и `code-review-ai-ai-review` — жесткая приемка кода: совместимость контрактов, lint / type checks, отсутствие "anti-patterns".
- `tdd-orchestrator` — разработка Constraint Engine и CPQ калькулятора строго через тесты (сначала пишем ожидаемый snapshot, затем логику).
