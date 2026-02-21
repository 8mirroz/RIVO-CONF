# 2. Product Model (шаблон структуры)

Этот документ — целевая структура Product Definition Layer.  
Фактические значения берутся из `source_inputs/RIVO_Fix_Engineering_Model.md` и PDF.

## 2.1 Атрибуты (пример)

- width: number (мм), min/max/step
- height: number (мм), min/max/step
- depth: number (мм), min/max/step
- load: number (кг/Н), min/max
- mountingType: enum (floor-wall | wall | floor | ceiling ...)
- equipmentModules: enum[] (toilet | bidet | piping | ...)

## 2.2 Каталог компонентов

- profiles[]
  - id, geometry, E/Ix/Wx, maxLength, weightPerMeter, costPerMeter
- nodes[]
  - id, compatibleProfiles[], maxMoment, maxShear, angles[]
- fasteners[]
  - id, usageRules, cost

## 2.3 Derived Values (server-side)

- structureGraphId
- safetyFactor
- calculatedPrice
- bomId
- validationState

## 2.4 Версионирование

- catalogVersion
- rulesVersion
- pricingVersion
- assetsVersion
- configurationVersion (snapshot)

