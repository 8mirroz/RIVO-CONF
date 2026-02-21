# 7. Задание для UI/UX агента (детальная разработка)

## Цель
Спроектировать интерфейс инженерного конфигуратора с 2 режимами:
- Guided Engineering Wizard
- Reverse Configuration (requirements → solutions)

## Входные источники
- `source_inputs/configurator_uiux_research.md`
- `source_inputs/RIVO_Fix_Configurator_User_Scenario.md`
- требования: explainable validation, прогресс, влияние на цену, сравнение решений

## Deliverables (обязательные)
1) Информационная архитектура (IA)
2) UI Flow диаграмма (экраны + состояния)
3) Компонентная архитектура (Design System + UI kit)
4) Макеты ключевых экранов (Desktop + Mobile)
5) Спецификация микрокопирайтинга для ошибок/ограничений
6) Спека анимаций (motion) и переходов
7) Accessibility (WCAG 2.2) чеклист

## Экраны (минимальный набор)

### Reverse Mode
- R1: Requirements Form
- R2: Solutions (3 карточки + compare)
- R3: Solution Details (3D + BOM + price + монтаж)
- R4: Export Center (PDF/DXF/IFC)
- R5: Save/Share (URL snapshot)

### Guided Mode
- G1: Product Type
- G2: Geometry
- G3: Load
- G4: Mounting
- G5: Modules
- G6: Validation
- G7: Summary (price/BOM)
- G8: Order/Export

## UX правила
- нельзя дать выбрать невалидное
- если недоступно — показать почему и как исправить
- каждое действие пересчитывает: constraints → price → BOM → render state

