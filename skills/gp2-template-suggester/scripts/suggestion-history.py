#!/usr/bin/env python3
"""Rotating local history of template suggestions per objective.

Keeps the last N (default 20) suggestions per objective so the suggester skill
can avoid proposing the same framework + theme combination repeatedly, and the
same archetypes/moves combinations in consecutive batches.

Storage: one JSON file per objective at
    skills/gp2-template-suggester/history/<objetivo>.json

Each entry:
    {
      "ts": "<ISO 8601 UTC>",
      "objective": "<objective slug>",
      "framework": "<framework slug>",
      "theme": "<theme phrase>",
      "hook_formula": "<formula slug>",
      "archetypes": ["A1", "A5", "A3", "A6"],   # optional, list of A* slugs per slide
      "moves": ["M9", "M4"],                     # optional, list of M* slugs
      "template_id": "<supabase id or null>",
      "status": "dispatched|completed|failed",
      "notes": "<optional>"
    }

Commands:
    list <objetivo> [--limit N]   # also returns aggregated archetype/move counts
    append <objetivo> --framework X --theme "Y" --hook Z
                       [--archetypes "A1,A5,..."] [--moves "M9,M4"]
                       [--template-id ID] [--status STATE] [--notes "..."]
                       [--keep K]
    stats               # counts per objective
    purge <objetivo>    # wipe history for one objective (requires --confirm)

Backward compatibility: old entries without `archetypes`/`moves` are loaded
silently; aggregated counts only consider entries that have the fields.
The `--image-mode` flag from the previous schema is no longer required and
silently ignored if passed.

The history is advisory: the suggester treats semantic proximity as repetition,
not exact match. Stored data feeds the LLM's context window when deciding the
next batch.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_OBJECTIVES = {
    "aquisicao",
    "posicionamento",
    "engajamento",
    "educacao",
    "prova_social",
    "retencao",
}

DEFAULT_KEEP = 20

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"


def history_path(objective: str) -> Path:
    return HISTORY_DIR / f"{objective}.json"


def ensure_history_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_history(objective: str) -> list[dict[str, Any]]:
    path = history_path(objective)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_history(objective: str, entries: list[dict[str, Any]]) -> None:
    ensure_history_dir()
    path = history_path(objective)
    path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_objective(objective: str) -> None:
    if objective not in ALLOWED_OBJECTIVES:
        allowed = ", ".join(sorted(ALLOWED_OBJECTIVES))
        raise SystemExit(
            f"error: invalid objective '{objective}'. allowed: {allowed}"
        )


def parse_csv_slugs(value: str | None) -> list[str]:
    if not value:
        return []
    return [token.strip() for token in value.split(",") if token.strip()]


def aggregate_counts(entries: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Aggregated A*/M* counts across the provided entries."""
    archetype_counter: Counter[str] = Counter()
    move_counter: Counter[str] = Counter()
    for entry in entries:
        for slug in entry.get("archetypes") or []:
            if isinstance(slug, str) and slug:
                archetype_counter[slug] += 1
        for slug in entry.get("moves") or []:
            if isinstance(slug, str) and slug:
                move_counter[slug] += 1
    return {
        "archetype_counts": dict(archetype_counter.most_common()),
        "move_counts": dict(move_counter.most_common()),
    }


def cmd_list(args: argparse.Namespace) -> None:
    validate_objective(args.objective)
    entries = load_history(args.objective)
    limit = args.limit or len(entries)
    output = entries[-limit:] if limit > 0 else []
    payload = {
        "objective": args.objective,
        "entries": output,
        **aggregate_counts(output),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_append(args: argparse.Namespace) -> None:
    validate_objective(args.objective)
    entries = load_history(args.objective)

    archetypes = parse_csv_slugs(args.archetypes)
    moves = parse_csv_slugs(args.moves)

    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "objective": args.objective,
        "framework": args.framework,
        "theme": args.theme,
        "hook_formula": args.hook,
        "template_id": args.template_id,
        "status": args.status,
    }
    if archetypes:
        entry["archetypes"] = archetypes
    if moves:
        entry["moves"] = moves
    if args.notes:
        entry["notes"] = args.notes

    entries.append(entry)

    keep = max(1, args.keep)
    if len(entries) > keep:
        entries = entries[-keep:]

    save_history(args.objective, entries)
    print(json.dumps({"saved": entry, "total": len(entries)}, ensure_ascii=False, indent=2))


def cmd_stats(_: argparse.Namespace) -> None:
    ensure_history_dir()
    stats: dict[str, Any] = {}
    for objective in sorted(ALLOWED_OBJECTIVES):
        entries = load_history(objective)
        last = entries[-1] if entries else None
        stats[objective] = {
            "count": len(entries),
            "last_ts": last["ts"] if last else None,
            "last_framework": last["framework"] if last else None,
            "last_archetypes": last.get("archetypes") if last else None,
            "last_moves": last.get("moves") if last else None,
            **aggregate_counts(entries),
        }
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def cmd_purge(args: argparse.Namespace) -> None:
    validate_objective(args.objective)
    if not args.confirm:
        raise SystemExit(
            "error: refusing to purge without --confirm. "
            f"this will wipe history/{args.objective}.json"
        )
    path = history_path(args.objective)
    if path.exists():
        path.unlink()
        print(json.dumps({"purged": str(path)}, ensure_ascii=False))
    else:
        print(json.dumps({"noop": str(path), "reason": "did not exist"}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rotating local suggestion history for gp2-template-suggester."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List recent suggestions + aggregated counts")
    p_list.add_argument("objective", help=f"one of: {', '.join(sorted(ALLOWED_OBJECTIVES))}")
    p_list.add_argument("--limit", type=int, default=None, help="last N entries (default: all)")
    p_list.set_defaults(func=cmd_list)

    p_append = subparsers.add_parser("append", help="Add a suggestion to the history")
    p_append.add_argument("objective", help=f"one of: {', '.join(sorted(ALLOWED_OBJECTIVES))}")
    p_append.add_argument("--framework", required=True, help="framework slug (e.g., listicle)")
    p_append.add_argument("--theme", required=True, help="theme phrase")
    p_append.add_argument("--hook", required=True, help="hook formula slug")
    p_append.add_argument(
        "--archetypes",
        default=None,
        help='comma-separated A* slugs per slide (e.g., "A1,A5,A5,A3,A6")',
    )
    p_append.add_argument(
        "--moves",
        default=None,
        help='comma-separated M* slugs (e.g., "M9,M4")',
    )
    # Legacy flag — accepted silently for backward compatibility with old callers.
    p_append.add_argument("--image-mode", default=None, help=argparse.SUPPRESS)
    p_append.add_argument("--template-id", default=None, help="Supabase template ID once dispatched")
    p_append.add_argument(
        "--status",
        default="dispatched",
        choices=["dispatched", "completed", "failed"],
        help="state at time of recording",
    )
    p_append.add_argument("--notes", default=None, help="optional free-text note")
    p_append.add_argument(
        "--keep", type=int, default=DEFAULT_KEEP, help=f"rotating limit (default: {DEFAULT_KEEP})"
    )
    p_append.set_defaults(func=cmd_append)

    p_stats = subparsers.add_parser("stats", help="Show counts per objective")
    p_stats.set_defaults(func=cmd_stats)

    p_purge = subparsers.add_parser("purge", help="Wipe history for one objective")
    p_purge.add_argument("objective", help=f"one of: {', '.join(sorted(ALLOWED_OBJECTIVES))}")
    p_purge.add_argument("--confirm", action="store_true", help="required to actually delete")
    p_purge.set_defaults(func=cmd_purge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
