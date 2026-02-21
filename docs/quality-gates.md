# Quality Gates

Quality Gates обеспечивают автоматическую проверку качества кода и соответствие стандартам проекта RIVO CONF.

## Обзор

Quality Gates интегрированы в CI/CD пайплайн и проверяют:

1. **Тестирование** - Unit и integration тесты
2. **Линтинг** - Стиль кода и типизация
3. **Валидация контрактов** - OpenAPI specs, JSON schemas
4. **Соблюдение ownership** - Соответствие governance/ownership-map.yaml
5. **Lock paths** - Изменения только в разрешенных путях

## Структура

```
├── tests/                    # Тесты
│   ├── unit/                # Unit тесты
│   ├── integration/         # Integration тесты
│   ├── fixtures/            # Тестовые данные
│   ├── pytest.ini           # Конфигурация pytest
│   └── conftest.py          # Общие fixtures
│
├── ci/                      # CI/CD конфигурации
│   ├── workflows/           # GitHub Actions workflows
│   │   ├── test.yml        # Запуск тестов
│   │   ├── lint.yml        # Линтинг
│   │   └── quality-gate.yml # Quality gate
│   └── README.md
│
└── scripts/quality/         # Скрипты валидации
    ├── validate_contracts.js
    ├── check_ownership.py
    ├── check_lock_paths.py
    └── README.md
```

## Workflows

### test.yml
Запускается на каждый push и PR в main/develop.

**Проверки:**
- Unit тесты с coverage
- Integration тесты
- Загрузка coverage в Codecov

### lint.yml
Запускается на каждый push и PR в main/develop.

**Проверки:**
- Black (форматирование)
- Ruff (linting)
- MyPy (типизация)

### quality-gate.yml
Запускается на каждый PR в main/develop.

**Проверки:**
- Валидация контрактов
- Проверка ownership compliance
- Smoke тесты
- Gate decision

## Локальный запуск

### Установка зависимостей
```bash
pip install -r tests/requirements-test.txt
```

### Запуск тестов
```bash
# Все тесты
pytest tests/

# Только unit тесты
pytest tests/unit -v

# Только integration тесты
pytest tests/integration -v

# С coverage
pytest tests/ --cov --cov-report=html
```

### Валидация
```bash
# Проверка ownership
python scripts/quality/check_ownership.py

# Валидация контрактов
node scripts/quality/validate_contracts.js

# Smoke тесты
bash scripts/run_smoke_checks.sh
```

## Интеграция с Lock Policy

Quality Gates enforce lock policy из `governance/ownership-map.yaml`:

1. **check_ownership.py** - Проверяет что все измененные файлы имеют owner
2. **check_lock_paths.py** - Проверяет что изменения в пределах lock_paths из Issue

## Definition of Done

PR считается готовым когда:
- ✅ Все тесты проходят
- ✅ Coverage ≥ 80%
- ✅ Нет lint ошибок
- ✅ Контракты валидны
- ✅ Ownership compliance
- ✅ Изменения в lock_paths

## Troubleshooting

### pytest не найден
```bash
pip install -r tests/requirements-test.txt
```

### Ошибка ownership
Добавьте путь в `governance/ownership-map.yaml`

### Нарушение lock_paths
Изменения должны быть только в путях указанных в Issue

## Метрики

Отслеживаемые метрики качества:
- Test coverage (%)
- Test execution time (s)
- Lint violations count
- Contract validation errors
- Gate pass rate (%)
