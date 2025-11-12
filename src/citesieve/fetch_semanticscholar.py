from __future__ import annotations
from typing import List, Tuple, Optional
from tqdm import tqdm
from .utils import get_json

def s2_find_paper_ids(title: str) -> List[Tuple[str,str,int]]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": title, "limit": 10, "fields": "paperId,title,year"}
    data = get_json(url, params=params, headers={"User-Agent":"citesieve/0.1"})
    out = []
    if data and data.get("data"):
        for d in data["data"]:
            t = (d.get("title") or "").lower()
            yr = d.get("year")
            if t.startswith(title.lower()):
                out.append((d.get("paperId"), d.get("title"), yr))
    return out

def s2_fetch_citers(paper_id: str, year_min: Optional[int], year_max: Optional[int]) -> List[dict]:
    base = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    fields = "citingPaper.paperId,citingPaper.title,citingPaper.year,citingPaper.authors,citingPaper.externalIds,citingPaper.url"
    out, offset = [], 0
    pbar = tqdm(desc=f"S2 citers {paper_id}", unit="works")
    while True:
        data = get_json(base, params={"fields":fields,"limit":1000,"offset":offset}, headers={"User-Agent":"citesieve/0.1"})
        if not data: break
        items = data.get("data", [])
        if not items: break
        for it in items:
            cp = it.get("citingPaper") or {}
            yr = cp.get("year")
            if year_min and yr is not None and yr < year_min: continue
            if year_max and yr is not None and yr > year_max: continue
            out.append(cp); pbar.update(1)
        offset += len(items)
        if len(items) < 1000: break
    pbar.close()
    return out
