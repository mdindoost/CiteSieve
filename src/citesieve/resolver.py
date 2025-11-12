from __future__ import annotations
from typing import List, Dict
from .utils import get_json
import re

def _norm_title(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_:]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def resolve_openalex_by_title(title: str) -> List[Dict]:
    params = {"search": title, "per_page": 25, "sort": "relevance_score:desc"}
    data = get_json("https://api.openalex.org/works", params=params, headers={"User-Agent":"citesieve/0.1"})
    results = []
    tgt = _norm_title(title)
    if data and data.get("results"):
        for w in data["results"]:
            t = (w.get("display_name") or w.get("title") or "")
            if _norm_title(t) != tgt:
                continue
            wid_full = w.get("id","")
            if wid_full.startswith("https://openalex.org/W"):
                core = wid_full.split("/")[-1][1:]
                results.append({
                    "id_core": core,
                    "id_full": wid_full,
                    "title": w.get("display_name") or w.get("title"),
                    "year": w.get("publication_year"),
                    "cited_by_count": w.get("cited_by_count", 0)
                })
    return sorted(results, key=lambda d: d.get("cited_by_count",0), reverse=True)
