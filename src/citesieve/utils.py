from __future__ import annotations
import re, sys, time
from typing import Optional, Dict, Any
import requests
import yaml

def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        # default packaged config (assumes working dir root)
        path = "citesieve.config.yml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_json(url: str, params=None, headers=None, timeout=60) -> Optional[dict]:
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
        if r.status_code != 200:
            print(f"[ERROR] GET {url} -> {r.status_code}: {r.text[:200]}", file=sys.stderr)
            return None
        return r.json()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}", file=sys.stderr)
        return None
