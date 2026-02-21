# 5. CPQ (Pricing + BOM)

## 5.1 Вычисления (server-side)

- Пересчёт цены на каждый change event
- Генерация BOM строго из StructureGraph
- Версионность цен/каталога

## 5.2 BOM

```ts
interface BomItem {
  sku: string;
  name: string;
  qty: number;
  unit: "pcs" | "m" | "set";
  meta?: Record<string, any>; // длины реза, примечания, etc
}
```

## 5.3 PriceQuote

```ts
interface PriceLine {
  sku: string;
  title: string;
  qty: number;
  unitPrice: number;
  lineTotal: number;
}

interface PriceQuote {
  currency: "RUB" | "USD" | "EUR";
  subtotal: number;
  discounts: number;
  taxes: number;
  total: number;
  lines: PriceLine[];
}
```

