from __future__ import annotations
import re, sys, time, os
from typing import Optional, Dict, Any
import requests
import yaml

# --- built-in default configuration (used if file missing or invalid) ---
_DEFAULT_CFG = {
    "filters": {
        "exclude_types": [
            "book", "book-chapter", "dissertation",
            "report", "magazine", "poster", "lecture"
        ],
        "title_patterns": {
            "survey": r"\bsurvey\b|\boverview\b|\bsummary\b",
            "review": r"\breview\b|\bcomparative study\b",
            "benchmark": r"\bbenchmark\b|\bevaluation\b|\bcomparison\b",
            "tutorial": r"\btutorial\b|\bprimer\b",
            "state_of_the_art": r"state[-\s]?of[-\s]?the[-\s]?art",
        },
    },
    "usage_hints": {
        "used": r"\buse[sd]?\b|\bapply[ied]\b|\bimplement(ed)?\b|\bintegrat(ed|es)\b",
        "build_on": r"\bextend(ed|s)?\b|\bbuild(s|ing)?\s+on\b",
        "based_on": r"\bbased\s+on\b|\badopt(ed|ing)?\b",
    },
    "http": {"user_agent": "citesieve/0.1"},
}

def load_config(path: Optional[str]) -> Dict[str, Any]:
    """Load YAML config if present, otherwise fall back to defaults."""
    path = path or "citesieve.config.yml"
    if not os.path.exists(path):
        print(f"[WARN] Config '{path}' not found — using built-in defaults.", file=sys.stderr)
        return _DEFAULT_CFG
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            return cfg or _DEFAULT_CFG
    except Exception as e:
        print(f"[WARN] Failed to parse config '{path}': {e}", file=sys.stderr)
        return _DEFAULT_CFG

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
