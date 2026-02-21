# Карта Skills для RIVO CONF

## Базовый порядок применения
1. `rivo-multi-agent-orchestrator`
2. Доменный skill (`rivo-product-modeling` или `rivo-constraint-engine` или `rivo-cpq-and-api` или `rivo-ui-3d-experience`)
3. `rivo-quality-gates`

## Триггеры skills
- `rivo-multi-agent-orchestrator`
Использовать для декомпозиции задач, управления зависимостями, разрешения ownership-конфликтов, планирования релизных волн.

- `rivo-product-modeling`
Использовать для атрибутов, каталогов, инженерных параметров, version tags и compatibility-матриц.

- `rivo-constraint-engine`
Использовать для DSL-правил, explainability payload, auto-correct pipeline и фильтрации кандидатов.

- `rivo-cpq-and-api`
Использовать для API-контрактов, pricing/BOM логики, snapshot persistence и export endpoints.

- `rivo-ui-3d-experience`
Использовать для guided/reverse UX, поведения недоступных опций и mapping validated snapshot -> render state.

- `rivo-quality-gates`
Использовать перед merge/release для replay-детерминизма, contract compatibility и E2E-гейтов.

## Handoff протокол
- Продюсер домена публикует обновленные контрактные примеры.
- Консьюмер домена обновляет реализацию только после merge контрактов.
- Quality skill подтверждает replay и E2E путь.
