# Retrieval and machine use

Canonical explanations are Markdown sections with stable explicit anchors. The YAML catalogue provides routing metadata and a short statement; it is not a replacement for the section's full context. The index builder retrieves the entire section, including its boundary and source notes, and adds authority, adoption, jurisdiction and review metadata.

```bash
python scripts/build_index.py
python scripts/build_index.py --include-drafts --output retrieval/draft-index.jsonl
python scripts/build_index.py --include-drafts --query "IE-COM-001"
```

Default output contains current approved records only. This review package has none, so the approved-only index is intentionally empty. Explicit draft mode supports review and exploration and must remain visibly labelled. The helper search is a small lexical demonstration, not a production RAG engine or an evaluated language-model service. Legal drafts and real cases are not ingested.

Before production retrieval, appoint reviewers, record approval/review dates, verify source rights and law where relevant, test the target retrieval system and preserve the distinction between proposed policy and adopted authority. Retain qualifications, neighbouring context and source revisions. No retrieved passage confers action permissions. No API, MCP server, external sync or scheduled publishing is configured.

Index files are reproducible outputs of `scripts/build_index.py`; change canonical documents and metadata first. A downstream model must explain an empty result or unavailable source instead of generating a confident answer from nothing.
