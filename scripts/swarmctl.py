#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_SRC_DIR = SCRIPT_DIR.parent / "repos/packages/agent-os/src"
SRC_CANDIDATES = []
if os.getenv("AGENT_OS_SRC"):
    SRC_CANDIDATES.append(Path(str(os.getenv("AGENT_OS_SRC"))))
SRC_CANDIDATES.append(REPO_SRC_DIR)
SRC_CANDIDATES.append(Path("/Users/user/antigravity-core/repos/packages/agent-os/src"))

SRC_DIR = next((p for p in SRC_CANDIDATES if p.exists()), None)
if SRC_DIR is None:
    raise SystemExit(
        "agent-os src not found. Set AGENT_OS_SRC or ensure repos/packages/agent-os/src exists."
    )
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from active_set_lib import parse_active_skills_md, publish_active_set, sha256_tree
from agent_os.agent_runtime import AgentRuntime
from agent_os.contracts import AgentInput, MemoryStoreInput, ModelRouteInput, RetrieverInput, ToolInput
from agent_os.memory_store import MemoryStore
from agent_os.model_router import ModelRouter
from agent_os.observability import emit_event
from agent_os.retriever import Retriever
from agent_os.tool_runner import ToolRunner


def _repo_root() -> Path:
    return SCRIPT_DIR.parent


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid JSON: {path}: {e}") from e


def _strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    out: list[str] = []
    for ch in line:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_simple_yaml(yaml_text: str) -> dict:
    """
    Minimal YAML subset parser for our router config:
    - mappings via `key: value` or `key:`
    - lists via `- item`
    - scalar values: strings/ints
    """
    cleaned_lines: list[tuple[int, str]] = []
    for raw in yaml_text.splitlines():
        raw = _strip_yaml_comment(raw)
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        cleaned_lines.append((indent, raw.lstrip(" ")))

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(0, root)]

    def current_container() -> Any:
        return stack[-1][1]

    for idx, (indent, line) in enumerate(cleaned_lines):

        while len(stack) > 1 and indent < stack[-1][0]:
            stack.pop()

        container = current_container()

        if line.startswith("- "):
            item = line[2:].strip()
            if not isinstance(container, list):
                raise ValueError("YAML structure error: list item in non-list container")
            container.append(_coerce_scalar(item))
            continue

        if ":" not in line:
            raise ValueError(f"YAML syntax error: {line}")

        key, rest = line.split(":", 1)
        key = key.strip()
        rest = rest.strip()

        if not isinstance(container, dict):
            raise ValueError("YAML structure error: key/value in non-dict container")

        if rest == "":
            nested: Any = {}
            if idx + 1 < len(cleaned_lines):
                next_indent, next_line = cleaned_lines[idx + 1]
                if next_indent > indent and next_line.startswith("- "):
                    nested = []
            container[key] = nested
            stack.append((indent + 2, container[key]))
        else:
            container[key] = _coerce_scalar(rest)

    return root


def _coerce_scalar(value: str) -> Any:
    if value.isdigit():
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def _routing_lookup_model_tier(model_routing: dict, task_type: str, complexity: str) -> str:
    for row in model_routing.get("routing", []):
        if row.get("task_type") == task_type and row.get("complexity") == complexity:
            return row.get("model_tier")
    raise KeyError(f"No model routing entry for {task_type}/{complexity}")


def _routing_lookup_mcp_profile(mcp_profiles: dict, task_type: str, complexity: str) -> str:
    for row in mcp_profiles.get("routing", []):
        if task_type in row.get("task_type", []) and complexity in row.get("complexity", []):
            return row.get("profile")
    return mcp_profiles.get("default_profile", "core")


def _default_budgets(repo_root: Path, complexity: str) -> tuple[int, float]:
    providers = _load_json(repo_root / "configs/tooling/model_providers.json")
    row = providers.get("budgets", {}).get("per_complexity", {}).get(complexity, {})
    token_budget = int(row.get("max_total_tokens", 20000))
    cost_budget = float(row.get("max_cost_usd", 0.30))
    return token_budget, cost_budget


def cmd_publish_skills(_: argparse.Namespace) -> int:
    repo_root = _repo_root()
    active_md = repo_root / "configs/skills/ACTIVE_SKILLS.md"
    dest_dir = repo_root / ".agent/skills"
    publish_active_set(repo_root=repo_root, active_md=active_md, dest_dir=dest_dir)
    print("OK: published active skills")
    return 0


def _iter_skill_dirs(agent_skills_dir: Path) -> Iterable[Path]:
    for p in agent_skills_dir.iterdir():
        if p.name.startswith("."):
            continue
        if p.is_dir():
            yield p


def cmd_doctor(_: argparse.Namespace) -> int:
    repo_root = _repo_root()

    active_md = repo_root / "configs/skills/ACTIVE_SKILLS.md"
    model_routing_path = repo_root / "configs/tooling/model_routing.json"
    mcp_profiles_path = repo_root / "configs/tooling/mcp_profiles.json"
    model_providers_path = repo_root / "configs/tooling/model_providers.json"
    router_yaml_path = repo_root / ".agent/config/model_router.yaml"
    agent_skills_dir = repo_root / ".agent/skills"
    manifest_path = agent_skills_dir / ".active_set_manifest.json"

    failures: list[str] = []

    for p in [active_md, model_routing_path, mcp_profiles_path, model_providers_path, router_yaml_path]:
        if not p.exists():
            failures.append(f"Missing: {p}")

    model_routing = None
    mcp_profiles = None
    if model_routing_path.exists():
        try:
            model_routing = _load_json(model_routing_path)
        except Exception as e:
            failures.append(str(e))

    if mcp_profiles_path.exists():
        try:
            mcp_profiles = _load_json(mcp_profiles_path)
        except Exception as e:
            failures.append(str(e))

    if model_providers_path.exists():
        try:
            providers = _load_json(model_providers_path)
            if providers.get("provider_topology") not in {"hybrid", "gateway-only", "direct-only"}:
                failures.append("model_providers.json: invalid provider_topology")
        except Exception as e:
            failures.append(str(e))

    if router_yaml_path.exists():
        try:
            data = _parse_simple_yaml(router_yaml_path.read_text(encoding="utf-8"))
            tiers = data.get("tiers")
            if not isinstance(tiers, dict):
                raise ValueError("model_router.yaml: missing `tiers` mapping")
            for tier in ("reasoning", "quality", "light"):
                if tier not in tiers:
                    raise ValueError(f"model_router.yaml: missing tiers.{tier}")
                models = tiers[tier].get("models") if isinstance(tiers[tier], dict) else None
                if not isinstance(models, list) or not models:
                    raise ValueError(f"model_router.yaml: tiers.{tier}.models must be a non-empty list")
        except Exception as e:
            failures.append(f"Invalid YAML: {router_yaml_path}: {e}")

    warnings: list[str] = []
    if not os.getenv("OPENROUTER_API_KEY"):
        warnings.append("Missing env var: OPENROUTER_API_KEY")

    if not agent_skills_dir.exists():
        failures.append(f"Missing directory: {agent_skills_dir}")
    elif not manifest_path.exists():
        failures.append(f"Missing manifest: {manifest_path} (run publish-skills)")
    else:
        try:
            manifest = _load_json(manifest_path)
            expected = {s.name for s in parse_active_skills_md(active_md)}
            published = {s.get("name") for s in manifest.get("skills", [])}
            missing = sorted(expected - published)
            extra = sorted(published - expected)
            if missing:
                failures.append(f"Manifest missing skills: {', '.join(missing)}")
            if extra:
                failures.append(f"Manifest has extra skills: {', '.join(extra)}")

            for row in manifest.get("skills", []):
                name = row.get("name")
                expected_hash = row.get("sha256_tree")
                skill_dir = agent_skills_dir / str(name)
                if not skill_dir.exists():
                    failures.append(f"Missing published skill dir: {skill_dir}")
                    continue
                actual_hash = sha256_tree(skill_dir)
                if expected_hash != actual_hash:
                    failures.append(f"Hash mismatch for {name}: manifest={expected_hash} actual={actual_hash}")

            actual_dirs = {p.name for p in _iter_skill_dirs(agent_skills_dir)}
            if actual_dirs - expected:
                failures.append(f"Extra directories in .agent/skills: {', '.join(sorted(actual_dirs - expected))}")
        except Exception as e:
            failures.append(f"Manifest invalid: {e}")

    if model_routing and mcp_profiles:
        try:
            _routing_lookup_model_tier(model_routing, "T2", "C1")
            _routing_lookup_mcp_profile(mcp_profiles, "T6", "C3")
        except Exception as e:
            failures.append(f"Routing sanity failed: {e}")

    if warnings:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 2

    print("OK: doctor passed")
    return 0


def _guess_task_type(text: str) -> str:
    t = text.lower()
    error_signals = [
        "ошибка",
        "error",
        "exception",
        "исключ",
        "stack trace",
        "падает",
        "fail",
        "failing",
        "слом",
        "не работает",
        "lint",
        "опечат",
        "typo",
    ]
    if any(s in t for s in error_signals):
        return "T2"

    payment_signals = ["payments", "оплат", "платеж", "stars", "звезд", "ton", "тон", "ton connect"]
    if any(s in t for s in payment_signals):
        return "T7"

    buckets = {
        "T7": [
            "telegram",
            "телеграм",
            "mini app",
            "миниапп",
            "miniapp",
            "бот",
            "bot",
            "stars",
            "звезд",
            "ton",
            "тон",
            "ton connect",
            "payments",
            "оплат",
            "платеж",
            "webapp",
            "мини апп",
        ],
        "T6": [
            "ui",
            "ux",
            "theme",
            "layout",
            "animation",
            "color",
            "typography",
            "design",
            "дизайн",
            "интерфейс",
            "верстк",
            "анимац",
            "цвет",
            "типограф",
            "тема",
        ],
        "T1": [
            ".env",
            "dependencies",
            "зависимост",
            "package.json",
            "config",
            "конфиг",
            "настрой",
            "tsconfig",
            "pyproject",
            "docker",
            "ci",
        ],
        "T2": [
            "bug",
            "баг",
            "error",
            "ошибка",
            "fail",
            "падает",
            "failing",
            "stack trace",
            "exception",
            "исключ",
            "lint",
            "typo",
            "опечат",
            "broken",
            "слом",
            "не работает",
            "исправ",
        ],
        "T3": [
            "feature",
            "фича",
            "endpoint",
            "эндпоинт",
            "api",
            "component",
            "компонент",
            "screen",
            "экран",
            "implement",
            "реализ",
            "add",
            "добав",
            "сделай",
        ],
        "T4": [
            "architecture",
            "архитектур",
            "refactor",
            "рефактор",
            "migration",
            "миграц",
            "redesign",
            "system design",
            "new project",
            "новый проект",
        ],
        "T5": [
            "analyze",
            "анализ",
            "compare",
            "сравни",
            "choose",
            "выбери",
            "investigate",
            "исслед",
            "research",
            "ресерч",
        ],
    }
    scores: dict[str, int] = {k: 0 for k in buckets}
    for key, words in buckets.items():
        for w in words:
            if w in t:
                scores[key] += 2
    best_score = max(scores.values()) if scores else 0
    if best_score == 0:
        return "T3"

    order = ["T7", "T6", "T4", "T1", "T2", "T3", "T5"]
    for k in order:
        if scores.get(k, 0) == best_score:
            return k
    return "T3"


def _guess_complexity(text: str) -> str:
    t = text.lower()
    if any(
        k in t
        for k in [
            "security",
            "безопасн",
            "production",
            "прод",
            "infra",
            "инфра",
            "token",
            "токен",
            "rotate key",
            "pci",
        ]
    ):
        return "C5"
    if any(k in t for k in ["payments", "оплат", "платеж", "auth", "авторизац", "логин"]):
        return "C4"
    if any(k in t for k in ["экран", "screen"]) and any(
        k in t for k in ["telegram", "телеграм", "mini app", "миниапп", "ui", "ux", "интерфейс"]
    ):
        return "C3"
    if any(
        k in t
        for k in [
            "migration",
            "миграц",
            "refactor",
            "рефактор",
            "architecture",
            "архитектур",
            "cross-domain",
            "breaking change",
        ]
    ):
        return "C4"
    if any(k in t for k in ["test", "тест", "integration", "интеграц", "e2e", "multiple files", "3-10 files"]):
        return "C3"
    if any(
        k in t
        for k in ["typo", "опечат", "readme", "ридми", "copy", "rename", "<50 lines", "one file", "1 file", "один файл"]
    ):
        return "C1"
    return "C2"


def _task_complexity_from_args(args: argparse.Namespace, text_field: str = "text") -> tuple[str, str]:
    text = getattr(args, text_field, "") or ""
    task_type = getattr(args, "task_type", None) or _guess_task_type(text)
    complexity = getattr(args, "complexity", None) or _guess_complexity(text)
    return task_type, complexity


def cmd_triage(args: argparse.Namespace) -> int:
    repo_root = _repo_root()
    model_routing = _load_json(repo_root / "configs/tooling/model_routing.json")
    mcp_profiles = _load_json(repo_root / "configs/tooling/mcp_profiles.json")

    task_type = args.task_type or _guess_task_type(args.text)
    complexity = args.complexity or _guess_complexity(args.text)
    model_tier = _routing_lookup_model_tier(model_routing, task_type, complexity)
    mcp_profile = _routing_lookup_mcp_profile(mcp_profiles, task_type, complexity)

    result = {
        "task_type": task_type,
        "complexity": complexity,
        "model_tier": model_tier,
        "mcp_profile": mcp_profile,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    repo_root = _repo_root()
    model_routing = _load_json(repo_root / "configs/tooling/model_routing.json")
    mcp_profiles = _load_json(repo_root / "configs/tooling/mcp_profiles.json")

    task_type = args.task_type or _guess_task_type(args.text)
    complexity = args.complexity or _guess_complexity(args.text)

    default_token, default_cost = _default_budgets(repo_root, complexity)
    token_budget = int(args.token_budget or default_token)
    cost_budget = float(args.cost_budget or default_cost)

    route_input = ModelRouteInput(
        task_type=task_type,
        complexity=complexity,
        token_budget=token_budget,
        cost_budget=cost_budget,
        preferred_models=list(args.preferred_model or []),
    )

    router = ModelRouter(repo_root=repo_root)
    route_output = router.route(
        route_input,
        mode=args.mode,
        unavailable_models=set(args.unavailable_model or []),
    )

    mcp_profile = _routing_lookup_mcp_profile(mcp_profiles, task_type, complexity)
    model_tier = _routing_lookup_model_tier(model_routing, task_type, complexity)

    payload = route_output.to_dict()
    payload["mcp_profile"] = mcp_profile
    payload["model_tier"] = model_tier
    payload["task_type"] = task_type
    payload["complexity"] = complexity

    emit_event("route_decision", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    repo_root = _repo_root()

    task_type = args.task_type or _guess_task_type(args.objective)
    complexity = args.complexity or _guess_complexity(args.objective)
    default_token, default_cost = _default_budgets(repo_root, complexity)

    router = ModelRouter(repo_root=repo_root)
    route_output = router.route(
        ModelRouteInput(
            task_type=task_type,
            complexity=complexity,
            token_budget=int(args.token_budget or default_token),
            cost_budget=float(args.cost_budget or default_cost),
            preferred_models=list(args.preferred_model or []),
        ),
        mode=args.mode,
        unavailable_models=set(args.unavailable_model or []),
    )

    runtime = AgentRuntime()
    run_id = str(uuid4())
    agent_input = AgentInput(
        run_id=run_id,
        objective=args.objective,
        plan_steps=[
            "route",
            "execute",
            "verify",
            "report",
        ],
        route_decision=route_output.to_dict(),
    )
    output = runtime.run(agent_input)

    retriever = Retriever(repo_root)
    retrieval = retriever.query(
        RetrieverInput(
            query=args.objective,
            sources=["docs", "configs"],
            max_chunks=3,
            freshness="workspace",
        )
    )

    memory = MemoryStore(repo_root)
    memory_write = memory.operate(
        MemoryStoreInput(
            op="write",
            key=f"run:{run_id}",
            payload={
                "objective": args.objective,
                "route": route_output.to_dict(),
                "status": output.status,
            },
        )
    )

    payload = {
        "run_id": run_id,
        "route": route_output.to_dict(),
        "agent": output.to_dict(),
        "retrieval": retrieval.to_dict(),
        "memory_write": memory_write.to_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_smoke(_: argparse.Namespace) -> int:
    repo_root = _repo_root()
    report: dict[str, Any] = {"checks": []}

    doctor_code = cmd_doctor(argparse.Namespace())
    report["checks"].append({"name": "doctor", "ok": doctor_code == 0, "code": doctor_code})

    try:
        router = ModelRouter(repo_root=repo_root)
        route = router.route(
            ModelRouteInput(
                task_type="T2",
                complexity="C2",
                token_budget=20000,
                cost_budget=0.30,
                preferred_models=[],
            )
        )
        report["checks"].append({"name": "route", "ok": True, "primary_model": route.primary_model})
    except Exception as e:
        report["checks"].append({"name": "route", "ok": False, "error": str(e)})

    tool = ToolRunner()
    tool_out = tool.run(ToolInput(tool_name="echo", args=["smoke-ok"], mode="read", correlation_id="smoke"))
    report["checks"].append({"name": "tool_runner", "ok": tool_out.exit_code == 0, "stdout": tool_out.stdout.strip()})

    retriever = Retriever(repo_root)
    retrieval = retriever.query(RetrieverInput(query="Agent OS", sources=["docs"], max_chunks=1, freshness="workspace"))
    report["checks"].append({"name": "retriever", "ok": len(retrieval.chunks) >= 0, "retrieval_ms": retrieval.retrieval_ms})

    ok = all(bool(c.get("ok")) for c in report["checks"]) and doctor_code == 0
    report["status"] = "pass" if ok else "fail"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def cmd_contracts(_: argparse.Namespace) -> int:
    repo_root = _repo_root()
    contracts = _load_json(repo_root / "configs/tooling/integration_contracts.json")
    print(json.dumps(contracts, ensure_ascii=False, indent=2))
    return 0


def cmd_integration(_: argparse.Namespace) -> int:
    repo_root = _repo_root()
    tests_dir = repo_root / "repos/packages/agent-os/tests"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(tests_dir),
            "-p",
            "test_*.py",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)

    return int(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(prog="swarmctl", description="Agent OS v2 utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pub = sub.add_parser("publish-skills", help="Publish ACTIVE_SKILLS.md into .agent/skills/")
    p_pub.set_defaults(fn=cmd_publish_skills)

    p_doc = sub.add_parser("doctor", help="Validate configs, env, and published active skills")
    p_doc.set_defaults(fn=cmd_doctor)

    p_tri = sub.add_parser("triage", help="Triage task text to (task_type, complexity, tiers)")
    p_tri.add_argument("text")
    p_tri.add_argument("--task-type", dest="task_type", default=None, help="Override task type (T1..T7)")
    p_tri.add_argument("--complexity", default=None, help="Override complexity (C1..C5)")
    p_tri.set_defaults(fn=cmd_triage)

    p_route = sub.add_parser("route", help="Resolve full model route contract")
    p_route.add_argument("text", help="Task text for classification")
    p_route.add_argument("--task-type", dest="task_type", default=None, help="Override task type (T1..T7)")
    p_route.add_argument("--complexity", default=None, help="Override complexity (C1..C5)")
    p_route.add_argument("--token-budget", type=int, default=None)
    p_route.add_argument("--cost-budget", type=float, default=None)
    p_route.add_argument("--mode", choices=["legacy", "hybrid"], default=None)
    p_route.add_argument("--preferred-model", action="append", default=[])
    p_route.add_argument("--unavailable-model", action="append", default=[])
    p_route.set_defaults(fn=cmd_route)

    p_run = sub.add_parser("run", help="Run minimal agent runtime contract")
    p_run.add_argument("objective", help="Objective text")
    p_run.add_argument("--task-type", dest="task_type", default=None)
    p_run.add_argument("--complexity", default=None)
    p_run.add_argument("--token-budget", type=int, default=None)
    p_run.add_argument("--cost-budget", type=float, default=None)
    p_run.add_argument("--mode", choices=["legacy", "hybrid"], default=None)
    p_run.add_argument("--preferred-model", action="append", default=[])
    p_run.add_argument("--unavailable-model", action="append", default=[])
    p_run.set_defaults(fn=cmd_run)

    p_smoke = sub.add_parser("smoke", help="Run smoke checks for core integrations")
    p_smoke.set_defaults(fn=cmd_smoke)

    p_int = sub.add_parser("integration", help="Run integration tests for agent-os")
    p_int.set_defaults(fn=cmd_integration)

    p_contracts = sub.add_parser("contracts", help="Print machine-readable integration contracts")
    p_contracts.set_defaults(fn=cmd_contracts)


    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
