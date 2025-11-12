"""
filters.py
----------
Filtering and pattern utilities for CiteSieve.

Provides helper functions for excluding certain work types
(e.g., surveys, reviews, dissertations, books) and for detecting
title keywords that suggest non-original work.
"""

import re
from typing import List, Dict, Optional, Tuple


def make_title_regex_map() -> Dict[str, str]:
    """
    Build regex map for exclusion and inclusion keyword patterns.
    Keys describe the reason for exclusion; values are case-insensitive regexes.
    """
    return {
        "survey": r"\bsurvey\b|\boverview\b|\bsummary\b",
        "review": r"\breview\b|\bcomparative study\b",
        "benchmark": r"\bbenchmark\b|\bevaluation\b|\bcomparison\b",
        "tutorial": r"\btutorial\b|\bprimer\b",
        "state_of_the_art": r"state[-\s]?of[-\s]?the[-\s]?art",
    }


def make_usage_hint_map() -> Dict[str, str]:
    """
    Build a regex map of hints that a citation likely *used* the method,
    not just mentioned it.
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
    for e in exclude_types:
        if e.lower() in typ.lower():
            return e
    return None


def title_exclusion_reason(title: str, title_patterns: Dict[str, str]) -> Optional[str]:
    """
    Return a keyword reason (like 'survey' or 'review') if the title matches
    any exclusion regex. Otherwise return None.
    """
    if not title:
        return None
    for reason, pattern in title_patterns.items():
        if re.search(pattern, title, re.IGNORECASE):
            return reason
    return None


def usage_hint_hit(title: str, usage_hints: Dict[str, str]) -> Optional[str]:
    """
    Return a 'usage hint' keyword if the title suggests the cited paper actually
    used or extended the target method.
    """
    if not title:
        return None
    for reason, pattern in usage_hints.items():
        if re.search(pattern, title, re.IGNORECASE):
            return reason
    return None


def filter_records(records: List[Dict], exclude_types: List[str]) -> Tuple[List[Dict], Dict[str, int]]:
    """
    Filter out records based on type and title.
    Returns (filtered_records, stats_dict).
    """
    title_patterns = make_title_regex_map()
    stats = {
        "removed_by_type": 0,
        "removed_by_title": 0,
        "reason_counts": {r: 0 for r in title_patterns},
    }

    filtered = []
    for rec in records:
        typ = rec.get("type", "")
        title = rec.get("title", "")

        # Type-based exclusion
        if is_type_excluded(typ, exclude_types):
            stats["removed_by_type"] += 1
            continue

        # Title-based exclusion
        reason = title_exclusion_reason(title, title_patterns)
        if reason:
            stats["removed_by_title"] += 1
            stats["reason_counts"][reason] += 1
            continue

        filtered.append(rec)

    return filtered, stats


def summarize_stats(stats: Dict[str, int]) -> str:
    """
    Pretty-print removal statistics.
    """
    out = []
    out.append(f"Removed by TYPE: {stats.get('removed_by_type', 0)}")
    out.append(f"Removed by TITLE: {stats.get('removed_by_title', 0)}")
    if "reason_counts" in stats:
        for k, v in stats["reason_counts"].items():
            if v > 0:
                out.append(f"  {k}: {v}")
    return "\n".join(out)
