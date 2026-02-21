# 1. Архитектура системы (5 слоёв)

Система конфигуратора строится как независимые слои:

1) **Product Definition Layer**
- атрибуты/параметры/домены
- типы конфигураций
- справочник узлов/профилей/крепежа
- версии (semver) на каталоги и прайсинг

2) **Configuration Logic Layer (Constraint Engine)**
- проверка совместимости
- dependency rules
- explainable validation (почему нельзя)
- автокоррекция (если разрешено)

3) **CPQ Layer**
- price calculation (server-side)
- BOM generation
- manufacturing parameters
- export (PDF/DXF/IFC) через сервисы

4) **Presentation Layer**
- guided selling wizard + режим reverse configuration
- показывать только допустимое
- прогресс/цена/валидность/объяснения

5) **Visualization Layer**
- 3D как визуализация validated конфигурации
- mapping: StructureGraph → render state
- никаких правил в 3D

## Две UX-модели

**Guided Engineering:** пошаговый мастер (новички/дилеры)  
**Reverse Configuration:** ввод требований → генерация 2–3 валидных вариантов (эконом/баланс/усиленный)

