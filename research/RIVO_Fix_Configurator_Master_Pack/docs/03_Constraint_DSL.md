# 3. Constraint DSL + Explainable Validation

## 3.1 Типы правил

- HARD (запрет)
- AUTO_CORRECT (автокоррекция)
- SOFT (предупреждение)
- OPTIMIZATION (целевая функция)

## 3.2 Модель правила

```ts
type RuleType = "hard" | "auto_correct" | "soft" | "optimization";

interface Rule {
  id: string;
  type: RuleType;
  scope: "profile" | "node" | "structure" | "configuration";
  priority: number; // выше — раньше
  condition: Predicate;
  action: Action;
  explanation: {
    title: string;
    message: string;
    why: string[];
    suggestedFixes?: SuggestedFix[];
  };
}
```

## 3.3 Explainable Validation Result

```ts
interface ValidationResultItem {
  ruleId: string;
  status: "pass" | "fail" | "auto_corrected" | "warning";
  affected: { kind: string; ids: string[] };
  explanation: { title: string; message: string; why: string[] };
  suggestedFixes?: SuggestedFix[];
}
```

## 3.4 Автокоррекция

Pipeline:
1) apply HARD rules
2) apply AUTO_CORRECT rules
3) revalidate
4) if invalid → discard candidate solution

## 3.5 Оптимизация

Цели:
- MIN_PRICE
- MIN_WEIGHT
- MAX_SAFETY

Подход:
- OR-Tools CP-SAT (через интерфейс/сервис)
- или Z3-стиль SMT

