# Глубокое исследование UI/UX для проектирования конфигураторов (Guided Selling / Product Configuration)

Дата: 2026-02-21  
Фокус: конфигураторы с большим числом опций (B2C/B2B), где пользователь пошагово собирает продукт/комплект (включая 2D/3D превью).

---

## 1) Ментальная модель конфигуратора: что пользователь “пытается сделать”

Пользователь приходит не “выбирать атрибуты”, а:
1) **понять, что вообще возможно** (границы вариантов)
2) **быстро найти подходящий вариант** (не утонуть в опциях)
3) **быть уверенным, что конфигурация валидна** (совместимость/ограничения)
4) **видеть влияние выбора** (цена, сроки, внешний вид, спецификация)
5) **закончить и сохранить результат** (заказ/коммерческое/ссылка/экспорт)

Отсюда вытекают ключевые UX-задачи:
- снижение когнитивной нагрузки
- предотвращение ошибок/недопустимых комбинаций
- ясная обратная связь (что изменилось и почему)
- поддержка уверенности (trust & clarity)
- быстрый “путь к результату” (guided flow)

---

## 2) Системные принципы (то, что должно быть заложено в архитектуру UI)

### 2.1 Прогрессивное раскрытие сложности (Progressive Disclosure)
**Суть:** не показывайте всю сложность сразу — оставьте “основной путь” простым, а продвинутые настройки вынесите во вторичный слой.  
**Почему важно:** конфигураторы почти всегда перегружают опциями; progressive disclosure снижает ошибки и ускоряет освоение.

Реализация:
- режим **Basic / Advanced**
- “ещё параметры” внутри группы
- раскрытие параметров **только когда они релевантны** (условные блоки)

### 2.2 “Меньше догадок — больше прозрачности” (Cognitive Load Reduction)
В конфигураторах люди делают много микро-решений, поэтому критично:
- структура (группы, шаги)
- прозрачность (что будет дальше, что влияет на что)
- ясность формулировок
- поддержка (подсказки, примеры, объяснения, автоподбор)

---

## 3) Информационная архитектура (IA): стандартная карта экранов

### 3.1 Рекомендуемая структура
1) **Start / Use-case** (что собираем, для чего, базовая цель)
2) **Base model** (серия/линейка/платформа)
3) **Size / Geometry** (размеры, ограничения)
4) **Materials / Finish** (цвет/материал/фурнитура)
5) **Modules / Options** (комплектация)
6) **Accessories / Add-ons**
7) **Summary** (итог, валидность, цена, сроки, экспорт)
8) **Checkout / Request quote** (или лид-форма)

### 3.2 Два режима навигации (лучше иметь оба)
- **Wizard (пошаговый)**: лучший default для новичков
- **Direct edit (быстрый доступ)**: для опытных и возвратных пользователей  
  (например, кликабельная навигация по шагам + “jump to”)

---

## 4) Паттерны UX, специфичные для конфигураторов

### 4.1 Обработка недоступных опций (unavailable/disabled)
Это частая точка провала UX.

**Правило:** пользователь должен понять *почему опция недоступна* и *что нужно изменить*, чтобы она стала доступной.

Рекомендуемый паттерн:
- оставлять опции видимыми (для контекста), но:
  - **tooltip “Почему недоступно”**
  - **link “Исправить автоматически” / “перейти к конфликтующему параметру”**
  - переключатель “скрыть недоступные”

Важно: простое “disabled без объяснения” вызывает фрустрацию и блокирует сценарий.

### 4.2 “Покажи, что именно сейчас выбрано” (Selected State Clarity)
При множестве похожих вариантов люди теряют уверенность.

Обязательные элементы:
- явное **текущее значение** в заголовке группы
- “chips” выбранных атрибутов в summary
- подпись “какая вариация изображена” для превью
- “Reset group / Reset all”

### 4.3 Вариативность как атрибуты, а не как отдельные товары
Если вариации — это один продукт (цвет/размер/материал), не размножайте карточки товара.  
Показывайте вариации как **selectable attributes** внутри одной сущности.

---

## 5) UI-компоненты: эталонный набор для конфигуратора

### 5.1 Левая панель (или нижняя на мобиле): Attribute Panel
- группы/шаги
- контролы: swatches, segmented, dropdown, slider, stepper
- подсказки (i), “совет” (recommendation)
- индикаторы валидности по группе (зелёный/желтый/красный)

### 5.2 Центральная зона: Viewer / Preview
- 3D/2D превью
- быстрые пресеты камеры
- кнопки “explode / dimensions / environment”
- загрузка: skeleton + progressive assets

### 5.3 Правая/нижняя зона: Summary (sticky)
- итоговая цена
- сроки/lead time
- статус валидности + список конфликтов
- CTA: “Сохранить / Получить КП / Заказать”
- “Поделиться конфигурацией” (link snapshot)

---

## 6) Motion & Feedback (как сделать “дорого” и понятнее)

Цель motion в конфигураторе — не “красота”, а **снижение неопределенности**:
- анимация изменения объекта (material swap, module swap)
- подсветка изменённой области (brief highlight)
- микропереходы между шагами
- плавная фиксация sticky summary (без скачков)

Правила:
- анимация должна быть короткой и предсказуемой
- loading/processing must be explicit (spinner/skeleton + текст “пересчитываем цену”)

---

## 7) Формы, ошибки и валидации: “как не убить конверсию”

Конфигуратор — это “форма на стероидах”. Нужны:
- inline validation (на уровне поля)
- summary error block сверху/внизу
- сообщения рядом с проблемным контролом
- текст ошибок должен быть:
  - человеческим
  - конкретным
  - с инструкцией “что сделать”

Отдельно:
- не используйте “hostile” тон
- не перегружайте одновременно всеми индикаторами (красное + иконка + подсказка + баннер)

---

## 8) Рекомендации и “guided selling” как снижение выбора

Guided selling — это не только “wizard”, но и механика выбора:
- вопросы вместо параметров (“где будет стоять?”, “какая задача?”, “какой бюджет?”)
- автоподбор стартовой конфигурации
- recommended defaults
- “best value” метки
- фильтрация домена значений по контексту

---

## 9) Метрики UX для конфигураторов (что измерять)

По шагам:
- drop-off rate на каждом шаге
- время на шаг
- количество “invalid states” (и время до исправления)
- частота использования “undo/reset”
- частота “почему недоступно”
- конверсия в:
  - saved config
  - request quote
  - checkout

3D:
- время до первого рендера (TTFR)
- размер ассетов и доля догрузок
- FPS / jank events
- процент пользователей, которым нужен “2D fallback” (слабые устройства)

---

## 10) Тестирование и исследование (как быстро улучшать)

### 10.1 Юзабилити тесты
Сценарии:
- собрать типовой вариант “под задачу”
- собрать “сложный” вариант (проверка ошибок/ограничений)
- сравнить 2 конфигурации и выбрать
- вернуться по ссылке и изменить 1 параметр

### 10.2 Эксперименты
- A/B для flow (wizard vs direct edit)
- multivariate для микрокомпонентов (контролы выбора, структура шага)
- wizard-of-oz для раннего теста “умных подсказок” без настоящего движка

---

## 11) Чеклист “идеального” UX конфигуратора (коротко, по делу)

1) Пользователь всегда видит **где он** (шаг/прогресс)  
2) Всегда понятно **что выбрано** (current selection is explicit)  
3) Недоступность опций **объясняется** и **исправляется**  
4) Цена/срок/валидность обновляются **сразу** и прозрачно  
5) Есть **reset**, **undo**, **share link**  
6) Информация раскрывается **по мере необходимости** (progressive disclosure)  
7) Избегаете “choice overload” (группировка, рекомендации, поиск)  
8) Ошибки рядом с полем + summary, без агрессии и перегруза  
9) На мобиле: bottom-sheet панель, крупные тапы, “sticky summary”  
10) Производительность: быстрая интерактивность и прогрессивная загрузка ассетов

---

## 12) Ссылки-источники (подборка по самым полезным темам)

### Конфигураторы и guided selling
- Guided Selling vs Guided Configuration (понятия и подходы): https://configit.com/learn/blog/guided-selling-vs-guided-configuration  
- Пример архитектуры/мышления 3D+guided selling (практический контекст): https://www.threekit.com/blog/how-to-use-salesforce-product-configurator-b2b-guided-selling

### Вариативность и продуктовые атрибуты (сильная база для конфигуратора)
- NN/g: “Products with Multiple Variants” (вариации как атрибуты): https://www.nngroup.com/articles/products-with-multiple-variants/  
- Baymard: Product Details Page UX (исследования PDP): https://baymard.com/research/product-page  
- NN/g: Ecommerce Product Pages guidelines: https://www.nngroup.com/articles/ecommerce-product-pages/  
- NN/g: кейс про уверенность пользователя в выбранной вариации: https://www.nngroup.com/articles/ux-design-ecommerce/

### Снижение когнитивной нагрузки и прогрессивное раскрытие
- NN/g: 4 principles to reduce cognitive load in forms: https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/  
- NN/g: Progressive Disclosure: https://www.nngroup.com/articles/progressive-disclosure/

### Ошибки/валидации/сообщения
- NN/g: 10 design guidelines for reporting errors in forms: https://www.nngroup.com/articles/errors-forms-design-guidelines/  
- NN/g: Error-message guidelines: https://www.nngroup.com/articles/error-message-guidelines/  
- NN/g: Indicators vs validations vs notifications: https://www.nngroup.com/articles/indicators-validations-notifications/  
- NN/g: Hostile patterns in error messages: https://www.nngroup.com/articles/hostile-error-messages/

### Choice overload и длинные списки
- NN/g video: Hick’s Law & long menus: https://www.nngroup.com/videos/hicks-law-long-menus/  
- Laws of UX: Hick’s Law: https://lawsofux.com/hicks-law/  
- Laws of UX: Choice overload: https://lawsofux.com/choice-overload/

### Disabled/unavailable элементы (важно для “недоступных опций”)
- Smashing Magazine: pitfalls of disabled buttons: https://www.smashingmagazine.com/2021/08/frustrating-design-patterns-disabled-buttons/  
- Smashing Magazine: Designing a perfect configurator UX (разбор конфигуратора): https://www.smashingmagazine.com/2018/02/designing-a-perfect-responsive-configurator/  
- Smart Interface Design Patterns: hidden vs disabled (и объяснения): https://smart-interface-design-patterns.com/articles/hidden-vs-disabled/

### Wizard-паттерн
- Wizard lessons: https://www.voalabs.com/blog/6-lessons-from-designing-a-wizard  
- Web wizard guide: https://lab.interface-design.co.uk/the-ultimate-guide-to-web-wizard-design-5b6fb4201f94

---

## 13) Что сделать следующим шагом (чтобы превратить это в дизайн-систему)

1) Выбрать 1–2 “эталонных” flow: Wizard + Direct edit  
2) Нарисовать структуру панели атрибутов (группы/контролы/состояния)  
3) Определить правила недоступности: disabled + tooltip + fix link  
4) Специфицировать summary (price/validity/CTA) и его sticky поведение  
5) Сформировать motion spec (переходы/feedback/loading)  
6) Собрать библиотеку компонентов (states: default/hover/active/disabled/error/loading)

