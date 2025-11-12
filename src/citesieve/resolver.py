from __future__ import annotations
from typing import List, Dict
from .utils import get_json

def resolve_openalex_by_title(title: str) -> List[Dict]:
    params = {"search": title, "per_page": 25, "sort": "relevance_score:desc"}
    data = get_json("https://api.openalex.org/works", params=params, headers={"User-Agent":"citesieve/0.1"})
    results = []
    if data and data.get("results"):
        for w in data["results"]:
            t = (w.get("display_name") or w.get("title") or "").lower()
            if t.startswith(title.lower()):
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
    # sort by cited_by_count desc
    return sorted(results, key=lambda d: d.get("cited_by_count",0), reverse=True)
