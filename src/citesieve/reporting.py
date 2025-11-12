import csv
from typing import List, Dict

FIELDS = ["source","id","title","year","type","cited_by","authors","doi","url","pdf","usage_flag"]

def write_titles(path: str, records: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write((r.get("title") or "").strip() + "\n")

def write_csv(path: str, records: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in FIELDS})
