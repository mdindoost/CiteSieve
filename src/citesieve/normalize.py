def normalize_openalex(w: dict) -> dict:
    title = (w.get("title") or w.get("display_name") or "").strip()
    year  = w.get("publication_year"); typ = (w.get("type") or "").strip().lower()
    cited_by = w.get("cited_by_count", 0); doi = w.get("doi") or ""
    pdf = ""; url = ""
    pl = w.get("primary_location") or {}
    if pl:
        url = pl.get("landing_page_url") or ""; pdf = pl.get("pdf_url") or ""
    oa = w.get("open_access") or {}
    if oa and not pdf: pdf = oa.get("oa_url") or ""
    authors = "; ".join((au.get("author") or {}).get("display_name","") for au in (w.get("authorships") or []) if (au.get("author") or {}).get("display_name"))
    return {"source":"openalex","id":w.get("id",""),"title":title,"year":year,"type":typ,"cited_by":cited_by,"authors":authors,"doi":doi,"url":url,"pdf":pdf}

def normalize_s2(cp: dict) -> dict:
    title = (cp.get("title") or "").strip(); year = cp.get("year")
    authors = "; ".join(a.get("name") for a in (cp.get("authors") or []) if a.get("name"))
    doi = (cp.get("externalIds") or {}).get("DOI") or ""; url = cp.get("url") or ""
    return {"source":"semanticscholar","id":cp.get("paperId",""),"title":title,"year":year,"type":"","cited_by":"","authors":authors,"doi":doi,"url":url,"pdf":""}
