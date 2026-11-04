# Validation instructions and limits

Use Python 3.11+ and `python -m pip install -r requirements-dev.txt` in a virtual environment. Run:

```bash
python scripts/validate.py
python scripts/test_validator.py
python scripts/build_index.py
python scripts/build_index.py --include-drafts --output retrieval/draft-index.jsonl
```

The validator checks JSON Schemas, dates, unique IDs, source/workflow links, workflow step order, canonical anchors, all forty numbered and thirty thematic input units, scenario metadata, internal Markdown links, basic Markdown lint and required files. Regression tests check rejection of malformed/unsupported metadata and retention of important boundaries in retrieval. They do not execute an employment workflow or evaluate a language model.

The optional `python scripts/check_external_links.py --limit 20` produces a bounded network reachability report. It is not a default CI requirement: network blocks and redirects can be inconclusive. The reviewed source-status report distinguishes actual GitHub retrieval/pins from unresolved dependencies and incomplete legislative reads.

See [acceptance criteria](acceptance-criteria.md), [scenario plan](scenario-tests.md), [retrieval plan](retrieval-tests.md), [technical report](technical-validation.md) and [release status](release-status.yaml). Manual accessibility, lived-experience, legal, privacy adoption and rights review remain separate gates.
