import re
from typing import Dict, List

def make_title_regex_map(patterns: Dict[str,str]):
    return {k: re.compile(v, re.I) for k,v in patterns.items()}

def is_type_excluded(typ: str, exclude_types: List[str]) -> str | None:
    t = (typ or "").strip().lower()
    return t if t in set(exclude_types) else None

def title_exclusion_reason(title: str, regex_map: Dict[str, re.Pattern]) -> str | None:
    tl = (title or "").strip()
    if not tl: return None
    for label, rgx in regex_map.items():
        if rgx.search(tl): return label
    return None

def usage_hint_hit(title: str, abstract: str, hints: List[str]) -> bool:
    text = f"{title} {abstract}".lower()
    return any(re.search(h, text) for h in hints)
