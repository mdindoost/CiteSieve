# CiteSieve

CiteSieve pulls citations for a target paper, filters out obvious surveys/books/reviews, and estimates **actual usage** (papers that likely *use* the idea rather than only review it). It unions **OpenAlex** and **Semantic Scholar** to get broader coverage than either alone.

## Why
Google Scholar numbers are high but opaque (merged versions, many doc types). CiteSieve gives you:
- Transparent sources (OpenAlex + S2 Graph API)
- Reproducible filters (type and title-based)
- A usage estimate via lightweight textual signals

## Install
```bash
git clone https://github.com/<your-user>/CiteSieve.git
cd CiteSieve
python -m venv .venv && source .venv/bin/activate
pip install -e .


Quick start
# Minimal: search by title
citesieve --title "Simplifying Graph Convolutional Networks" --out sgc_sieve

# If you know OpenAlex or arXiv/DOI:
citesieve --openalex W2916106175 --openalex W2964124573 --out sgc_sieve

# Year bounds (optional)
citesieve --title "Simplifying Graph Convolutional Networks" --year-min 2019 --year-max 2025 --out sgc_2019_2025


Outputs (in current folder):

sgc_sieve.titles.txt — deduped titles after filters

sgc_sieve.filtered.csv — records with fields (source, id, year, authors, etc.)

Console stats — fetched counts, removals by reason, usage estimate

How “usage” is estimated

Type filters remove books, theses, standards, etc.

Title filters remove obvious surveys, “overview”, “state of the art”, tutorials, benchmarks.

Usage hints (optional, configurable): keeps/flags items that mention signals like “precompute features”, “decoupled propagation”, “A^K X”, “linearized GNN”.

You can customize patterns in citesieve.config.yml.

Config

See citesieve.config.yml
. You can pass a custom file with --config path.yml.

Caveats

Scholar has no official API; we don’t scrape it.

All text heuristics are approximate; tune patterns for your domain.

Contributing

PRs welcome! See issues for roadmap. Please add a test in tests/ for new features.


---

## `citesieve.config.yml`
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
    survey:            "\\bsurvey\\b"
    review:            "\\breview\\b|\\bliterature review\\b|\\bcomprehensive review\\b|\\bsystematic review\\b|\\bscoping review\\b|\\bmini-review\\b|\\bmeta[-\\s]?analysis\\b"
    state_of_the_art:  "\\bstate[-\\s]?of[-\\s]?the[-\\s]?art\\b"
    overview:          "\\boverview\\b"
    tutorial:          "\\btutorial\\b"
    benchmark:         "\\bbenchmark(s)?\\b"
    bibliometric:      "\\bbibliometric\\b"
    position:          "\\bposition paper\\b"
    editorial:         "\\beditorial\\b"
    handbook:          "\\bhandbook\\b"
    encyclopedia:      "\\bencyclopedia\\b"
    book:              "\\bbook\\b"

usage_hints:
  - "(precomput|propagat|diffus)\\s+(feature|embedding|representation)"
  - "\\bdecoupl(ed|e)\\s+(propagation|message\\s*passing)\\b"
  - "\\ba\\^?k\\s*x\\b"
  - "\\blinear(ized)?\\s+gnn\\b"
  - "\\bpost[-\\s]?propagation\\b"

http:
  user_agent: "citesieve/0.1 (contact: md72@njit.edu)"
