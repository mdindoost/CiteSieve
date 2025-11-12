from __future__ import annotations
import argparse, sys
from typing import Dict, List, Set

from .utils import load_config
from .resolver import resolve_openalex_by_title
from .fetch_openalex import fetch_citers_openalex
from .fetch_semanticscholar import s2_find_paper_ids, s2_fetch_citers
from .normalize import normalize_openalex, normalize_s2
from .filters import make_title_regex_map, is_type_excluded, title_exclusion_reason, usage_hint_hit
from .reporting import write_titles, write_csv

def main():
    p = argparse.ArgumentParser(description="CiteSieve: estimate actual usage among citers.")
    p.add_argument("--title", help="Target paper title (prefix match).")
    p.add_argument("--openalex", action="append", help="OpenAlex W-ID core or with W (e.g., 2916106175 or W2916106175). Can repeat.")
    p.add_argument("--year-min", type=int, default=None)
    p.add_argument("--year-max", type=int, default=None)
    p.add_argument("--out", default="citesieve_out")
    p.add_argument("--config", default=None, help="Path to YAML config (filters & hints).")
    args = p.parse_args()

    cfg = load_config(args.config)
    UA = cfg.get("http",{}).get("user_agent","citesieve/0.1")

    # Resolve OpenAlex IDs
    works = []
    if args.openalex:
        for oid in args.openalex:
            core = oid[1:] if oid.startswith("W") else oid
            works.append({"id_core": core, "id_full": f"https://openalex.org/W{core}", "title":"(provided)","year":None,"cited_by_count":None})
    elif args.title:
        works = resolve_openalex_by_title(args.title)
        if not works:
            print("[ERROR] Could not resolve target paper on OpenAlex.", file=sys.stderr)
            sys.exit(1)
    else:
        print("[ERROR] Provide --title or --openalex.", file=sys.stderr)
        sys.exit(1)

    print("\n[WORK IDS]")
    for d in works:
        print(f"- W{d['id_core']} | year={d.get('year')} | cited_by={d.get('cited_by_count')} | {d.get('title')}")
        print(f"  {d['id_full']}")

    # Fetch OA citers
    oa_all = []
    for d in works:
        oa_all.extend(fetch_citers_openalex(d["id_core"], UA, args.year_min, args.year_max))
    oa_norm = [normalize_openalex(w) for w in oa_all]
    print(f"\n[INFO] OpenAlex citers: {len(oa_norm)}")

    # Fetch S2 citers (search S2 for variants of the title)
    s2_norm = []
    if args.title:
        s2_cands = s2_find_paper_ids(args.title)
        if s2_cands:
            print("\n[S2 PAPER IDS]")
            for pid, ttl, yr in s2_cands:
                print(f"- {pid} | year={yr} | {ttl}")
            for pid, _, _ in s2_cands:
                s2_norm.extend([normalize_s2(cp) for cp in s2_fetch_citers(pid, args.year_min, args.year_max)])
    print(f"\n[INFO] Semantic Scholar citers: {len(s2_norm)}")

    # Union by title (case-insensitive)
    def tkey(r): return (r.get("title") or "").strip().lower()
    merged_map: Dict[str, dict] = {}
    for r in oa_norm + s2_norm:
        key = tkey(r)
        if key and key not in merged_map:
            merged_map[key] = r
    merged = list(merged_map.values())
    print(f"[INFO] Union unique-by-title: {len(merged)}")

    # Build filters
    ex_types = cfg["filters"]["exclude_types"]
    title_rx = make_title_regex_map(cfg["filters"]["title_patterns"])
    hints    = cfg.get("usage_hints", [])

    # Apply filters with accounting
    removed_type_count = 0; removed_title_count = 0
    removed_type_bd: Dict[str,int] = {}; removed_title_bd: Dict[str,int] = {}
    kept = []
    for r in merged:
        tr = is_type_excluded(r.get("type",""), ex_types)
        if tr:
            removed_type_count += 1; removed_type_bd[tr] = removed_type_bd.get(tr,0)+1; continue
        rr = title_exclusion_reason(r.get("title",""), title_rx)
        if rr:
            removed_title_count += 1; removed_title_bd[rr] = removed_title_bd.get(rr,0)+1; continue
        kept.append(r)

    # Usage flag (very light heuristic)
    for r in kept:
        r["usage_flag"] = "yes" if usage_hint_hit(r.get("title",""), "", hints) else "maybe"

    # Sort newest first
    kept_sorted = sorted(kept, key=lambda x: (x.get("year") or -1, x.get("title") or ""), reverse=True)

    # Outputs
    titles_path = f"{args.out}.titles.txt"
    csv_path    = f"{args.out}.filtered.csv"
    write_titles(titles_path, kept_sorted)
    write_csv(csv_path, kept_sorted)

    # Stats
    print("\n[STATS]")
    print(f"OpenAlex unique: {len({tkey(r) for r in oa_norm if tkey(r)})}")
    print(f"S2 unique:       {len({tkey(r) for r in s2_norm if tkey(r)})}")
    print(f"Union (titles):  {len(merged)}")
    if removed_type_count:
        bd = ", ".join(f"{k}: {v}" for k,v in sorted(removed_type_bd.items(), key=lambda x:-x[1]))
        print(f"Removed by TYPE: {removed_type_count}  ({bd})")
    else:
        print("Removed by TYPE: 0")
    if removed_title_count:
        bd = ", ".join(f"{k}: {v}" for k,v in sorted(removed_title_bd.items(), key=lambda x:-x[1]))
        print(f"Removed by TITLE:{removed_title_count}  ({bd})")
    else:
        print("Removed by TITLE: 0")

    used = sum(1 for r in kept_sorted if r["usage_flag"] == "yes")
    print(f"Kept (final):    {len(kept_sorted)}")
    print(f"Likely usage:    {used}  (flagged by usage hints; tune in config)")
    print(f"\nTitles: {titles_path}")
    print(f"CSV   : {csv_path}")
