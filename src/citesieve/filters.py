"""
filters.py
----------
Filtering and pattern utilities for CiteSieve.

- make_title_regex_map(patterns): compile config regex once.
- title_exclusion_reason: works with compiled regex OR raw pattern strings.
- is_type_excluded: type-based filtering.
- usage_hint_hit: lightweight usage signals.
- filter_records: batch filter using provided patterns & type list.
"""

import re
from typing import List, Dict, Optional, Tuple, Any


def make_title_regex_map(patterns: Dict[str, str]) -> Dict[str, re.Pattern]:
    """
    Compile title filter regex patterns from config.
    patterns: mapping of reason -> regex string
    returns:  mapping of reason -> compiled re.Pattern (case-insensitive)
    """
    rx_map: Dict[str, re.Pattern] = {}
    for key, pattern in patterns.items():
        try:
            rx_map[key] = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            # Keep going even if a pattern is invalid
            print(f"[WARN] Invalid title regex for '{key}': {pattern} ({e})")
    return rx_map


def make_usage_hint_map() -> Dict[str, str]:
    """
    Build a regex map of hints that a citation likely *used* the method,
    not just mentioned it. (Kept for potential future use.)
    """
    return {
        "used": r"\buse[sd]?\b|\bapply[ied]\b|\bimplement(ed)?\b|\bintegrat(ed|es)\b",
        "build_on": r"\bextend(ed|s)?\b|\bbuild(s|ing)?\s+on\b",
        "based_on": r"\bbased\s+on\b|\badopt(ed|ing)?\b",
    }


def is_type_excluded(typ: str, exclude_types: List[str]) -> Optional[str]:
    """
    Return the excluded type if the given `typ` matches one of `exclude_types`.
    Otherwise return None.
    """
    if not typ:
        return None
    t = typ.strip().lower()
    for e in exclude_types:
        if t == e.lower() or e.lower() in t:
            return e
    return None


def title_exclusion_reason(title: str, title_patterns: Dict[str, Any]) -> Optional[str]:
    """
    Return a keyword reason (like 'survey' or 'review') if the title matches
    any exclusion regex.

    `title_patterns` may be:
      - dict[str, re.Pattern]  (preferred; from make_title_regex_map)
      - dict[str, str]         (raw regex strings; backward compatible)
    """
    if not title:
        return None
    for reason, pat in title_patterns.items():
        try:
            if isinstance(pat, re.Pattern):
                if pat.search(title):
                    return reason
            else:
                # raw string pattern
                if re.search(pat, title, re.IGNORECASE):
                    return reason
        except re.error as e:
            print(f"[WARN] Skipping invalid title regex for '{reason}': {pat} ({e})")
            continue
    return None


def usage_hint_hit(title: str, usage_hints: Dict[str, str]) -> Optional[str]:
    """
    Return a 'usage hint' keyword if the title suggests the cited paper actually
    used or extended the target method.
    """
    if not title:
        return None
    for reason, pattern in usage_hints.items():
        try:
            if re.search(pattern, title, re.IGNORECASE):
                return reason
        except re.error as e:
            print(f"[WARN] Skipping invalid usage regex for '{reason}': {pattern} ({e})")
            continue
    return None


def filter_records(
    records: List[Dict],
    exclude_types: List[str],
    title_patterns: Dict[str, Any],
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Filter out records based on type and title.
    Returns (filtered_records, stats_dict).

    `title_patterns` can be compiled patterns (recommended) or raw strings.
    """
    # Build stats skeleton using provided keys if compiled map, else from raw keys
    reason_keys = list(title_patterns.keys())
    stats: Dict[str, Any] = {
        "removed_by_type": 0,
        "removed_by_title": 0,
        "reason_counts": {k: 0 for k in reason_keys},
    }

    filtered: List[Dict] = []
    for rec in records:
        typ = rec.get("type", "") or ""
        title = rec.get("title", "") or ""

        # Type-based exclusion
        tr = is_type_excluded(typ, exclude_types)
        if tr:
            stats["removed_by_type"] += 1
            continue

        # Title-based exclusion
        rr = title_exclusion_reason(title, title_patterns)
        if rr:
            stats["removed_by_title"] += 1
            if rr not in stats["reason_counts"]:
                stats["reason_counts"][rr] = 0
            stats["reason_counts"][rr] += 1
            continue

        filtered.append(rec)

    return filtered, stats


def summarize_stats(stats: Dict[str, Any]) -> str:
    """
    Pretty-print removal statistics.
    (Kept for compatibility; not used by CLI directly.)
    """
    out = []
    out.append(f"Removed by TYPE: {stats.get('removed_by_type', 0)}")
    out.append(f"Removed by TITLE: {stats.get('removed_by_title', 0)}")
    if "reason_counts" in stats:
        for k, v in stats["reason_counts"].items():
            if v > 0:
                out.append(f"  {k}: {v}")
    return "\n".join(out)
