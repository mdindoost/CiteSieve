from __future__ import annotations
from typing import List, Tuple, Optional
from tqdm import tqdm
from .utils import get_json
import re

def _norm_title(s: str) -> str:
    # normalize for strict equality: lowercase, collapse whitespace, strip punctuation-ish
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_:]+", " ", s)      # unify dashes/underscores to space
    s = re.sub(r"\s+", " ", s)            # collapse spaces
    return s

def s2_find_paper_ids(title: str, strict: bool = True) -> List[Tuple[str,str,int]]:
    """
    Returns a list of (paperId, title, year) candidates for the target title.
    If strict=True, only exact-normalized title matches are returned.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": title, "limit": 25, "fields": "paperId,title,year"}
    data = get_json(url, params=params, headers={"User-Agent":"citesieve/0.1"})
    out: List[Tuple[str,str,int]] = []
    if data and data.get("data"):
        tgt = _norm_title(title)
        for d in data["data"]:
            t = d.get("title") or ""
            yr = d.get("year")
            if strict:
                if _norm_title(t) == tgt:
                    out.append((d.get("paperId"), t, yr))
            else:
                # fallback prefix match
                if _norm_title(t).startswith(tgt[:max(1, len(tgt)//2)]):
                    out.append((d.get("paperId"), t, yr))
    return out

def s2_fetch_citers(paper_id: str, year_min: Optional[int], year_max: Optional[int]) -> List[dict]:
    """
    Paginates through Semantic Scholar citations list for a given paperId.
    """
    base = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    fields = "citingPaper.paperId,citingPaper.title,citingPaper.year,citingPaper.authors,citingPaper.externalIds,citingPaper.url"
    out = []
    offset = 0
    pbar = tqdm(desc=f"S2 citers {paper_id}", unit="works")
    while True:
        params = {"fields": fields, "limit": 1000, "offset": offset}
        data = get_json(base, params=params, headers={"User-Agent":"citesieve/0.1"})
        if not data:
            break
        items = data.get("data", [])
        if not items:
            break
        for it in items:
            cp = it.get("citingPaper") or {}
            yr = cp.get("year")
            if year_min and (yr is not None) and yr < year_min:
                continue
            if year_max and (yr is not None) and yr > year_max:
                continue
            out.append(cp)
            pbar.update(1)
        offset += len(items)
        if len(items) < 1000:
            break
    pbar.close()
    return out
