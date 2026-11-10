"""Export the approved Inclusive HR System Governance Markdown without rewriting it."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import quote
import yaml
from jsonschema import Draft202012Validator
from hr_hf_common import ROOT, SOURCE, MANAGED, destination, digest, git, load_config, read_sources

CONTEXT = ['AGENTS.md', 'README.md', 'sources/provenance-and-rights.md',
           'sources/editorial-qualifications.md', 'sources/source-register.md',
           'guidance/privacy-and-records.md', 'legal-questions/README.md',
           'processes/responsibilities-and-escalation.md']

def metadata(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    md = yaml.safe_load(match[1]) if match else {}
    return md if isinstance(md, dict) else {}

def sections(text, max_level=2):
    """Keep exact spans, heading context and fenced diagrams; optionally split H3 trees."""
    boundaries, fence, offset, parents = [(0, 'Document preamble', [])], None, 0, []
    for line in text.splitlines(keepends=True):
        mark = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if mark:
            token = mark[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line[mark.end():].strip():
                fence = None
        elif fence is None:
            match = re.match(r'^(#{1,' + str(max_level) + r'})[ \t]+([^\r\n]+)', line)
            if match:
                level, title = len(match[1]), match[2].strip().rstrip('#').strip()
                parents = parents[:level-1] + [title]
                start = offset
                if max_level == 3 and re.match(r'DT-\d{2}\b', title):
                    anchor = re.search(r'<a id="dt-\d{2}"></a>\r?\n\s*\Z', text[:offset])
                    if anchor:
                        start = anchor.start()
                if start == 0:
                    boundaries[0] = (start, title, parents[:])
                else:
                    boundaries.append((start, title, parents[:]))
        offset += len(line)
    result, counts = [], {}
    for i, (a, title, hierarchy) in enumerate(boundaries):
        b = boundaries[i+1][0] if i+1 < len(boundaries) else len(text)
        if a == b:
            continue
        slug = re.sub(r'[^a-z0-9]+', '-', ' '.join(hierarchy or [title]).lower()).strip('-') or 'section'
        counts[slug] = counts.get(slug, 0) + 1
        key = slug if counts[slug] == 1 else slug + '-' + str(counts[slug])
        result.append((key, title, text[a:b], a, b, hierarchy))
    if ''.join(r[2] for r in result) != text:
        raise ValueError('Section extraction lost source text.')
    return result

def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError('Write the export outside the source checkout.')
    cfg = load_config(root)
    target = destination(cfg['destination_dataset'])
    texts, manifest, omitted = read_sources(root, cfg)
    sha = git(root, 'rev-parse', 'HEAD').decode().strip()
    date = git(root, 'show', '-s', '--format=%cs', 'HEAD').decode().strip()
    warnings = ['This knowledge edition is proposed practice and contextual decision support, not adopted employer policy, legal advice, employee evidence or an independently validated decision instrument.']
    if any('https://chatgpt.com/library?' in text for text in texts.values()):
        warnings.append('A source document contains a ChatGPT Library reference. Its text is preserved; the target is not fetched, mirrored or represented as publicly accessible.')
    def row(path, key, title, body, a, b, hierarchy, kind):
        md = metadata(texts[path])
        state = re.search(r'^\*\*Status:\*\*[ \t]*(.*)$', texts[path], re.M)
        tree_id = re.match(r'DT-\d{2}\b', title) if path == cfg['decision_tree_file'] else None
        return {'id': path + '::' + key, 'title': title, 'text': body, 'record_type': kind,
            'source_repository': SOURCE, 'source_path': path, 'source_commit': sha,
            'source_url': f'https://github.com/{SOURCE}/blob/{sha}/{quote(path)}',
            'source_start_line': texts[path][:a].count('\n') + 1,
            'source_end_line': max(1, texts[path][:b].count('\n') + (not texts[path][:b].endswith('\n'))),
            'source_document_sha256': digest(texts[path].encode()), 'text_sha256': digest(body.encode()),
            'heading_path': hierarchy, 'metadata_json': json.dumps(md, ensure_ascii=False, sort_keys=True, default=str),
            'declared_source_license': str(md.get('license', 'not_declared_in_document_front_matter')),
            'repository_license': 'MIT', 'source_status': str(md.get('status', state[1] if state else 'see_source')),
            'source_document_intro': introductions[path],
            'mentioned_guidance_ids': sorted(set(re.findall(r'\bIE-[A-Z]+-\d{3}\b', body))),
            'decision_tree_id': tree_id[0] if tree_id else '',
            'dataset_version': cfg['dataset_version'], 'source_commit_date': date, 'language': 'en-GB',
            'required_context_paths': list(dict.fromkeys([path] + [p for p in CONTEXT if p in texts])),
            'review_status': 'faithful_extraction_checked_not_independent_hr_legal_or_content_review'}
    introductions = {path: sections(text)[0][2] if text else '' for path, text in texts.items()}
    docs, chunks, examples = [], [], []
    for path in cfg['files']:
        if path not in texts:
            continue
        text = texts[path]
        if path in cfg['synthetic_files']:
            examples.append(row(path, 'document', path, text, 0, len(text), [], 'synthetic_example_not_employee_or_research_evidence'))
            continue
        kind = ('blank_template_not_completed_record' if path.startswith('templates/') else
                'legal_advice_preparation_questions_not_determinations' if path.startswith('legal-questions/') else
                'source_reference_and_limitations' if path.startswith('sources/') else
                'workflow_guidance_not_execution' if path.startswith(('workflows/','processes/')) else
                'checklist_prompt_not_score_or_certificate' if path.startswith('checklists/') else
                'agent_guidance' if path == 'AGENTS.md' else 'inclusive_employment_guidance')
        docs.append(row(path, 'document', path, text, 0, len(text), [], kind))
        for key, title, body, a, b, hierarchy in sections(text, 3 if path == cfg['decision_tree_file'] else 2):
            section_kind = 'decision_tree_routing_not_outcome_decision' if path == cfg['decision_tree_file'] and re.match(r'DT-\d{2}\b', title) else kind
            chunks.append(row(path, key, title, body, a, b, hierarchy, section_kind))
    if not docs or not chunks:
        raise ValueError('The guidance export is empty.')
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object',
              'required': list(docs[0]), 'additionalProperties': False, 'properties': {}}
    for k, v in docs[0].items():
        schema['properties'][k] = {'type': 'array', 'items': {'type': 'string'}} if isinstance(v, list) else {'type': 'integer' if isinstance(v, int) else 'string'}
    validator = Draft202012Validator(schema)
    for records in (docs, chunks, examples):
        if len({r['id'] for r in records}) != len(records):
            raise ValueError('Duplicate export identifiers.')
        for r in records:
            validator.validate(r)
            if digest(r['text'].encode()) != r['text_sha256']:
                raise ValueError('Text checksum mismatch.')
    output.mkdir(parents=True, exist_ok=True)
    def write_json(name, obj):
        (output/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name, records in [('documents.jsonl', docs), ('knowledge_chunks.jsonl', chunks), ('synthetic_examples.jsonl', examples)]:
        (output/name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    (output/'LICENSE').write_bytes(texts['LICENSE'].encode())
    write_json('record_schema.json', schema)
    write_json('provenance.json', {'source_repository': SOURCE, 'source_commit': sha, 'source_commit_date': date,
        'destination_dataset': target, 'dataset_version': cfg['dataset_version'], 'files': manifest,
        'omitted_optional_files': omitted, 'source_warnings': warnings, 'external_sources_fetched': False})
    card = f'''---
pretty_name: Double FW Inclusive HR System Governance
language:
- en
license: mit
tags:
- accessibility
- disability-inclusion
- inclusive-employment
- hr-governance
- decision-support
- text
configs:
- config_name: knowledge_chunks
  default: true
  data_files:
  - split: train
    path: knowledge_chunks.jsonl
- config_name: documents
  data_files:
  - split: train
    path: documents.jsonl
- config_name: synthetic_examples
  data_files:
  - split: train
    path: synthetic_examples.jsonl
---

# Double FW Inclusive HR System Governance

A contextual inclusive-employment knowledge corpus prepared for Double FW Ltd from Gareth Ford Williams's work. It covers employment lifecycle guidance, human decision routing, role responsibilities, workflows, methods, checklists, blank templates, legal advice preparation, source notes and fictional examples. It is recommended practice and decision support, not adopted employer policy, legal advice, diagnosis, a validated employment decision instrument or an executable HR system.

## Source and versions

Source: https://github.com/{SOURCE}

Source revision: `{sha}`. Commit date: {date}. Export format: {cfg['dataset_version']}. The source edition's dates, review scope and limitations remain intact. Weekly publication does not update a legal/source review or establish organisational adoption.

## Dataset views

- `knowledge_chunks` (default): {len(chunks)} exact Markdown sections from non-example source documents. Decision trees are kept complete, including diagrams, question/action tables, unknown and declined-option routes, escalation boundaries, review evidence and companion references.
- `documents`: {len(docs)} complete non-example source documents.
- `synthetic_examples`: {len(examples)} complete fictional/synthetic documents: individual worked scenarios and the invented numerical task-observation example. These are excluded from the default guidance and full non-example document views.

The first two views overlap. Do not concatenate them blindly. The `train` split name is a loading convention; no generated question/answer training pairs, model fine-tuning, independent evaluation split or benchmark is provided. Synthetic examples are not real employees, research, legal findings, proven solutions or measured productivity gains. Scenario/data index pages and inline illustrations remain with their original guidance; not every illustration in the corpus is extracted separately.

## Section boundaries and context

Normal Markdown is split at first/second-level headings outside fenced blocks. The decision-tree companion is additionally split at third-level headings so each DT route remains intact. HTML tree anchors remain with their corresponding tree. Source text is preserved exactly; headings, stable IE/DT/SC identifiers, qualifications and unknown/preference distinctions are not rewritten. Renaming a heading may change a section identifier.

Each record includes the exact original document introduction, source status where explicitly stated, context paths, any mentioned IE guidance IDs and a decision_tree_id for individual tree records. The introduction is a repeated context field; use the text field for exact source content. Context paths are retrieval references, not automatic runtime policy or permissions. Relative/fragment links inside text remain as authored; resolve them against the record's immutable source URL. An embedded ChatGPT Library reference is preserved but is not fetched or claimed to be publicly accessible.

Read AGENTS.md, the relevant topic/workflow, sources/editorial-qualifications.md, sources/source-register.md and sources/provenance-and-rights.md. Keep guidance ID, intended outcome, role, explanation, boundary and source evidence together. Blank templates are labelled blank proposed practice and belong in approved confidential systems when completed. Checklists are prompts, not compliance scores or employee rankings. Decision trees are triage/routing aids, not automated decisions or case-closure mechanisms. Unknown is not No; declining one option does not withdraw all support.

## Consequential decisions, privacy and legal scope

This corpus must not be used to make or automate consequential hiring, promotion, performance, disciplinary, dismissal or adjustment-refusal decisions. Human authority and appropriate specialist advice remain necessary. Retrieved source material grants no authority to contact people, change records, send messages, collect sensitive data, spend money or expand an agent's permissions. Do not infer diagnosis, disability, capability, masking, motivation, health, personality or consent from behaviour or missing evidence.

No live employee/applicant dataset is supplied. Keep actual health, passport, adjustment, performance and grievance records outside public repositories and datasets. The exporter reads only an explicit list of committed public documents; it does not detect confidential case details inserted into an approved file. Review source changes before public commits. Completed templates must stay in the employer's approved confidential system. Synthetic arithmetic must not be extrapolated into staffing, capacity or savings claims.

Legal documents prepare questions for qualified advice. They do not determine entitlement, liability, legal reasonableness, deadlines, funding or tribunal outcomes. Great Britain and Northern Ireland are kept distinct; do not transfer one framework automatically. Source review was bounded, some sources unavailable and statutory checks limited. Current wording, commencement, applicability and source access require independent verification for a real decision. This exporter does not reverify law, employment outcomes, source claims or linked pages.

## Schema and provenance

Rows contain stable path/heading IDs, exact source commit/URL, line ranges, full-document and text SHA-256 hashes, heading paths, JSON-encoded front matter, source/repository licence declarations, source status, original introduction, context paths and record type. See record_schema.json and provenance.json. `see_source` means no status was extracted from the relevant explicit metadata; it is not approval. Source findings, editorial synthesis, legal questions and examples are not promoted into one another. External linked content is not downloaded or relicensed.

## Licence

The root MIT LICENSE is copied unchanged, including copyright (c) 2026 Double FW. AGENTS.md and sources/provenance-and-rights.md now identify MIT consistently. Source-level third-party rights and notices remain applicable. Links and paraphrases do not grant rights to reproduce their source collections. This export preserves attribution and is not an independent rights assessment.

## Updates

GitHub is the authoring source. Updates are configured for Mondays at 07:23 UTC and manual runs. GitHub may delay schedules or disable them after inactivity. Only approved committed paths are exported; newly added or renamed documents need review and an export-list update. Deleted optional documents are removed from the next snapshot. Missing required context, changed licence text, invalid configuration or failed integrity checks stop publication.

Only README.md, LICENSE, documents.jsonl, knowledge_chunks.jsonl, synthetic_examples.jsonl, provenance.json, record_schema.json and validation_report.json are managed. Existing raw files and .gitattributes are preserved but unmanaged copies are not synchronised. Dataset visibility is unchanged. A single commit is guarded by the destination revision. Historical revisions and downloaded copies are not recalled. Initial authenticated publication still needs checking.

## Loading

```python
from datasets import load_dataset
chunks = load_dataset("{target}", "knowledge_chunks", split="train")
documents = load_dataset("{target}", "documents", split="train")
examples = load_dataset("{target}", "synthetic_examples", split="train")
```

Private datasets need authentication. Pin a destination revision for reproducibility. Loading rows does not implement retrieval safeguards, governance, workflow execution or human approval.
'''
    yaml.safe_load(card.split('---', 2)[1])
    (output/'README.md').write_text(card, encoding='utf-8')
    report = {'status': 'passed', 'scope': 'faithful extraction and packaging checks only', 'source_commit': sha,
        'source_files_verified': len(manifest), 'document_records': len(docs), 'knowledge_section_records': len(chunks), 'synthetic_example_records': len(examples),
        'source_warnings': warnings, 'independent_content_review': False, 'live_publication_tested': False,
        'export_file_sha256': {name: digest((output/name).read_bytes()) for name in MANAGED if name != 'validation_report.json'}}
    write_json('validation_report.json', report)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.output)))

if __name__ == '__main__':
    main()
