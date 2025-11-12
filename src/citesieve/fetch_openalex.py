from __future__ import annotations
import time
from typing import List, Optional
from tqdm import tqdm
from .utils import get_json

def fetch_citers_openalex(core_id: str, ua: str, year_min: Optional[int], year_max: Optional[int]) -> list[dict]:
    base = "https://api.openalex.org/works"
    filt = f"cites:W{core_id}"
    if year_min or year_max:
        from_date = f"{year_min}-01-01" if year_min else "1800-01-01"
        to_date   = f"{year_max}-12-31" if year_max else "2100-12-31"
        filt += f",from_publication_date:{from_date},to_publication_date:{to_date}"
    params = {"filter":filt, "per_page":200, "cursor":"*", "sort":"publication_year:desc"}
    out, seen = [], set()
    pbar = tqdm(desc=f"OpenAlex citers W{core_id}", unit="works")
    while True:
        data = get_json(base, params=params, headers={"User-Agent":ua})
        if not data: break
        results = data.get("results", [])
        if not results: break
        for w in results:
            wid = w.get("id")
            if wid and wid not in seen:
                seen.add(wid); out.append(w); pbar.update(1)
        nxt = (data.get("meta") or {}).get("next_cursor")
        if not nxt: break
        params["cursor"] = nxt
        time.sleep(0.05)
    pbar.close()
    return out
