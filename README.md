# CiteSieve

CiteSieve is a lightweight command-line tool that analyzes citations of a given academic paper across **OpenAlex** and **Semantic Scholar**. It helps you identify which papers *actually use* the idea (vs. just mentioning or reviewing it). Perfect for meta-research, survey curation, or evaluating research influence.

## Why

Google Scholar numbers are high but opaque (merged versions, many doc types). CiteSieve gives you:

- Transparent sources (OpenAlex + Semantic Scholar)
- Reproducible filters (type and title-based)
- A usage estimate via lightweight textual signals

---
---

## 🚀 Features

- Combines **OpenAlex** and **Semantic Scholar** for wide citation coverage.
- Filters out reviews, books, surveys, and non-research document types.
- Flags likely *usage* citations via keyword heuristics (e.g., "decoupled propagation", "A^K X", etc.).
- Produces transparent `.csv` and `.txt` outputs for reproducibility.
- Fully configurable via YAML.

---

## ⚙️ Installation

```bash
git clone https://github.com/<your-user>/CiteSieve.git
cd CiteSieve
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Dependencies: Python 3.8+, `requests`, `tqdm`, `pyyaml`

---

## 🧭 Quick Start

### 1. Search by title (recommended)
```bash
citesieve --title "Simplifying Graph Convolutional Networks" --out sgc_sieve
```

### 2. Use known OpenAlex IDs
```bash
citesieve --openalex W2916106175 --openalex W2964124573 --out sgc_sieve
```

### 3. Add year filters
```bash
citesieve --title "Simplifying Graph Convolutional Networks" --year-min 2019 --year-max 2025 --out sgc_2019_2025
```

### 4. Custom config
```bash
citesieve --title "Simplifying Graph Convolutional Networks" --config my_custom.yml --out sgc_custom
```

---

## 📦 Outputs

Each run generates two files in the working directory:

| File | Description |
|------|--------------|
| `*.titles.txt` | Deduplicated list of titles that passed filters |
| `*.filtered.csv` | Detailed metadata: source, ID, title, year, authors, URL, etc. |

Example console output:

```
[WORK IDS]
- W2964124573 | year=2019 | cited_by=351 | Simplifying Graph Convolutional Networks
  https://openalex.org/W2964124573
[INFO] OpenAlex citers: 1536
[INFO] Semantic Scholar citers: 3486
[INFO] Union unique-by-title: 3744
[STATS]
Removed by TYPE: 84  (book: 20, review: 42, other: 22)
Removed by TITLE: 48  (survey: 26, tutorial: 12, benchmark: 10)
Kept (final):    3612
Likely usage:    278
Titles: sgc_sieve.titles.txt
CSV   : sgc_sieve.filtered.csv
```

---

## 🧠 How “usage” is estimated

1. **Type filters** exclude books, theses, reports, etc.  
2. **Title filters** exclude “survey”, “review”, “overview”, “tutorial”, etc.  
3. **Usage hints** flag papers with textual evidence of *methodological adoption*, e.g.:  
   - `precompute features`
   - `decoupled propagation`
   - `A^K X`
   - `linearized GNN`
   - `post-propagation`

All regex patterns are configurable in the YAML file.

---

## ⚙️ Config File (`citesieve.config.yml`)

Default config (auto-loaded unless you pass `--config`):

```yaml
filters:
  exclude_types:
    - book
    - book-chapter
    - book-part
    - book-section
    - book-series
    - book-track
    - monograph
    - reference-entry
    - encyclopedia-entry
    - edited-book
    - report
    - report-component
    - dissertation
    - other
    - standard

  title_patterns:
    survey:            "\bsurvey\b"
    review:            "\breview\b|\bliterature review\b|\bcomprehensive review\b|\bsystematic review\b|\bscoping review\b|\bmini-review\b|\bmeta[-\s]?analysis\b"
    state_of_the_art:  "\bstate[-\s]?of[-\s]?the[-\s]?art\b"
    overview:          "\boverview\b"
    tutorial:          "\btutorial\b"
    benchmark:         "\bbenchmark(s)?\b"
    bibliometric:      "\bbibliometric\b"
    position:          "\bposition paper\b"
    editorial:         "\beditorial\b"
    handbook:          "\bhandbook\b"
    encyclopedia:      "\bencyclopedia\b"
    book:              "\bbook\b"

usage_hints:
  - "(precomput|propagat|diffus)\s+(feature|embedding|representation)"
  - "\bdecoupl(ed|e)\s+(propagation|message\s*passing)\b"
  - "\ba\^?k\s*x\b"
  - "\blinear(ized)?\s+gnn\b"
  - "\bpost[-\s]?propagation\b"

http:
  user_agent: "citesieve/0.1 (contact: md72@njit.edu)"
```

## Why

Google Scholar numbers are high but opaque (merged versions, many doc types). CiteSieve gives you:

- Transparent sources (OpenAlex + Semantic Scholar)
- Reproducible filters (type and title-based)
- A usage estimate via lightweight textual signals

---

## 🧩 Tips

- Run once without `--year-min`/`--year-max` to get total coverage.  
- Inspect `filtered.csv` in Excel or pandas to slice results (`df[df.usage_flag=="yes"]`).  
- Adjust regex in config for your field (e.g., “transformer”, “fine-tuning”).  
- You can skip S2 or OpenAlex by modifying code paths in `cli.py` (advanced users).

---

## ⚠️ Caveats

- **Google Scholar** is *not* used (no API; scraping avoided).  
- **APIs have rate limits** — large citation lists may take a few minutes.  
- **Usage heuristics** are approximate; you can fine-tune or disable them.  
- Titles with typos or alternative names may need manual merging.  

---

## 🧪 Development

```bash
pytest tests/
black src/
```

To add features, open PRs or issues on GitHub. Contributions are welcome!

---

## 🧭 Example End-to-End Run

```bash
# 1. Activate your environment
source .venv/bin/activate

# 2. Run full analysis
citesieve --title "Simplifying Graph Convolutional Networks" --year-min 2019 --year-max 2025 --out sgc_full

# 3. Check outputs
head sgc_full.titles.txt
open sgc_full.filtered.csv  # or use pandas
```

---

## 📫 Contact

Maintainer: **Mohammad Dindoost**  
Email: md724@njit.edu  
Version: 0.1-pre