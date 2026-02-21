# BIM-описание (IFC 4.0) для системы RIVO Fix / RIVO Set / RIVO Touch

## 1. IFC-стратегия
Цель: обеспечить корректный обмен с BIM/CDE, сохранив:
- состав (артикулы, количество, длины)
- типологию элементов
- связи узлов и креплений (на уровне «fastener/assembly»)
- привязку оборудования (санитарные терминалы)

Рекомендуемая схема:
- Каркас как **IfcElementAssembly** (или IfcAssembly) с вложенными элементами.
- Профили как **IfcMember** (или IfcBeam, если нужно поведение балки).
- Соединители/крепёж как **IfcFastener** (или IfcMechanicalFastener).
- Инсталляции как **IfcSanitaryTerminal** (или IfcFlowTerminal, подтип).
- Панели смыва как **IfcBuildingElementProxy** (категория «Accessories») или IfcDiscreteAccessory.

## 2. Иерархия пространств (минимум)
- IfcProject
  - IfcSite (опционально)
    - IfcBuilding
      - IfcBuildingStorey
        - IfcElementAssembly `RIVO_FIX_FRAME_<id>`
          - элементы профиля
          - крепёж/узлы
          - инсталляция
          - панель смыва (если в составе)

## 3. Мэппинг номенклатуры (Recommended Mapping)

### 3.1 Профиль
- Артикулы: 100001.1, 100098
- IFC: `IfcMember` (PredefinedType = NOTDEFINED)  
  Или `IfcBeam` при необходимости аналитики.
- Pset:
  - `Pset_ManufacturerTypeInformation`: Manufacturer, ModelReference(=ART)
  - `Pset_ProductRequirements`: load/path (опц.)
  - Пользовательский `Pset_RIVO_Common`: `Art`, `Role`, `LengthMm`, `CutId`, `PackRef`

### 3.2 Соединители/узлы/крепёж
- Артикулы: 100002, 100002.1, 100014, 100007*, 100004*, 100005*, 100006*, 100008, 100009, 100010, 100011, 100003*, 100012, 100013
- IFC: `IfcFastener` или `IfcMechanicalFastener`
- Связи:
  - `IfcRelConnectsElements` между профилями (A,B) с «референтом» fastener (через property или relationship)
  - Альтернатива: хранить fastener как часть assembly без явной топологии, но с `ConnectedTo` в Pset

### 3.3 Инсталляции (RIVO Set)
- 200001, 200002, 203001, 201001
- IFC: `IfcSanitaryTerminal` (PredefinedType:
  - WC (для 200001/200002 можно оставить NOTDEFINED + Pset)
  - BIDET
  - URINAL)
- Pset:
  - `Pset_SanitaryTerminalTypeCommon`
  - `Pset_ManufacturerTypeInformation` (Art)
  - `Pset_RIVO_Set`: `TankVolumeL`, `FlushPresetL`, `FlushOptionsL`, `MaxLoadKg`, `OutletDn`, `StudBolt`, `InstallDepthMm` (где применимо)

### 3.4 Панели смыва (RIVO Touch)
- 301001–301008, 302001–302007, 303001–303007
- IFC: `IfcDiscreteAccessory` (PredefinedType = NOTDEFINED) или `IfcBuildingElementProxy`
- Pset:
  - `Pset_ManufacturerTypeInformation` (Art)
  - `Pset_RIVO_Touch`: `WidthMm`, `HeightMm`, `ThicknessMm`, `Finish`

## 4. Геометрия (Representation)
- Каркас и профиль: `IfcExtrudedAreaSolid` (если известна форма сечения) или `IfcFacetedBrep` (если есть mesh/CAD).
- Узлы: `IfcFacetedBrep` (предпочтительно) или упрощённые solids.
- Уровень детализации:
  - LOD 200: упрощённые габариты
  - LOD 300: реальные сечения/отверстия (если производитель предоставляет)

Важно: если точная форма сечения профиля не задана в каталоге, в IFC допускается:
- хранить «условное» прямоугольное сечение + параметр `RealProfileRef` в Pset, указывающий на библиотеку производителя.

## 5. Идентификация и коды
- IfcGloballyUniqueId — генерируется движком
- `Name`: `RIVO <Art> <Role>`
- `Tag`: внутренний id (например, `elem-123`)
- `ObjectType`: `RIVO_<Art>`
- `Classification`: IfcClassificationReference (опционально)

## 6. Коллизии и атрибуты для MEP
Рекомендуемые атрибуты для проверок:
- `ClearanceMm` (зазоры под обслуживание/ревизию)
- `AccessPanelRequired` (bool)
- `ElectricalConduitAllowed` (bool)

## 7. Экспорт
- Формат: IFC4 (Coordination View 2.0 при необходимости)
- Единицы: мм
- Ось проекта: как в CAD/конфигураторе (X ширина, Y высота, Z глубина)
