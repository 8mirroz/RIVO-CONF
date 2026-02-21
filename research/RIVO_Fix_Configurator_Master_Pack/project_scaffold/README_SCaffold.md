# Project Scaffold

Это каркас, чтобы быстро развернуть runnable проект по документации из `docs/`.

## Рекомендуемая структура репозитория
- backend/ (NestJS, TypeScript)
- frontend/ (Next.js, TypeScript)
- models/ (catalog/rules/pricing)
- docker/ (compose, init scripts)
- docs/

## Следующие шаги
1) Создать реальный NestJS проект (nest new backend)
2) Создать Next.js app (create-next-app frontend --ts)
3) Внедрить контракт `ConfigurationSnapshot`
4) Реализовать endpoints из `docs/06_API_Contract.md`
5) Подключить 3D (react-three-fiber) и render mapping

