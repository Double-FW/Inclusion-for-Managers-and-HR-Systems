#!/usr/bin/env python3
"""Validate this documentation package. No network and no personal data processing."""
from pathlib import Path
import csv,json,re,sys
from urllib.parse import unquote,urlsplit
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
def load(path):return yaml.safe_load((ROOT/path).read_text(encoding='utf-8'))
def errors_for(schema_name,record):
    schema=json.loads((ROOT/f'schemas/{schema_name}.schema.json').read_text())
    return [str(e.message) for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(record)]
def headings(text):
    text=re.sub(r'```.*?```','',text,flags=re.S)
    found=set(re.findall(r'<a id="([^"]+)"',text)); counts={}
    for title in re.findall(r'^#{1,6} (.+)$',text,re.M):
        slug=re.sub(r'[^\w\- ]','',title.lower()).replace(' ','-')
        n=counts.get(slug,0);counts[slug]=n+1
        found.add(slug+(f'-{n}' if n else ''))
    return found
def local_reference(path,reference):
    url=urlsplit(reference)
    if url.scheme or reference.startswith('//'):return None
    target=(path.parent/unquote(url.path)).resolve() if url.path else path.resolve()
    if not target.is_relative_to(ROOT):return f'Escapes repository: {reference}'
    if not target.exists():return f'Missing path: {reference}'
    if url.fragment and target.suffix=='.md' and unquote(url.fragment) not in headings(target.read_text()):return f'Missing anchor: {reference}'
    return None
def collect():
    errs=[];counts={}
    datasets=[('data/guidance.yaml','records','guidance'),('evidence/sources.yaml','sources','source'),('evidence/dependencies.yaml','dependencies','dependency'),('evidence/claims.yaml','claims','claim'),('validation/scenarios.yaml','scenarios','scenario')]
    data={}
    for path,key,kind in datasets:
        wrapper=load(path)
        if set(wrapper)!={'version',key}:errs.append(f'{path}: unexpected wrapper fields')
        items=wrapper[key];data[key]=items;counts[key]=len(items)
        ids=[x['id'] for x in items]
        if len(set(ids))!=len(ids):errs.append(f'{path}: duplicate IDs')
        for x in items:
            errs.extend(f'{path}:{x["id"]}: {e}' for e in errors_for(kind,x))
    wfs=[yaml.safe_load(p.read_text()) for p in sorted((ROOT/'workflows').glob('*.yaml'))]
    wids={x['id'] for x in wfs};counts['workflows']=len(wfs)
    if wids!={'W1','W2','W3','W4','W5'} or len(wfs)!=5:errs.append('Expected exactly five workflow IDs W1-W5')
    source_ids={x['id'] for x in data['sources']};guide_ids={x['id'] for x in data['records']}
    for x in wfs:
        errs.extend(f'{x["id"]}: {e}' for e in errors_for('workflow',x))
        ids=[s['id'] for s in x['steps']]
        if len(ids)!=len(set(ids)):errs.append(f'{x["id"]}: duplicate step IDs')
        for i,s in enumerate(x['steps']):
            expected=ids[i+1] if i+1<len(ids) else None
            if s['next_step']!=expected:errs.append(f'{x["id"]}: disconnected or incorrect step order')
        for branch in x['decisions']:
            if branch['at_step'] not in ids or branch['next_step'] not in ids+['escalate','close']:
                errs.append(f'{x["id"]}: unknown conditional workflow state')
        for p in x['template_paths']+[x['canonical_path']]:
            if not (ROOT/p).is_file():errs.append(f'{x["id"]}: missing {p}')
    for key in ['records','claims']:
        for x in data[key]:
            if not set(x['source_ids'])<=source_ids:errs.append(f'{x["id"]}: unknown source')
            e=local_reference(ROOT/'README.md',x['canonical_path'])
            if e:errs.append(f'{x["id"]}: {e}')
            if x.get('workflow_id') and x['workflow_id'] not in wids:errs.append(f'{x["id"]}: unknown workflow')
            if x.get('reviewed_on') and x.get('review_due') and x['review_due']<x['reviewed_on']:errs.append(f'{x["id"]}: review due precedes review')
    for x in data['dependencies']:
        if x['source_id'] not in source_ids:errs.append(f'{x["id"]}: unknown dependency source')
    if len(data['dependencies'])!=17:errs.append('Expected seventeen requested dependencies')
    for x in data['scenarios']:
        if not set(x['guidance_ids'])<=guide_ids or x['workflow_id'] not in wids:errs.append(f'{x["id"]}: unknown scenario reference')
        if x['execution_status']=='not_run' and x['observed_result'] is not None:errs.append(f'{x["id"]}: not-run case claims an observed result')
        if x['execution_status']!='not_run' and not x['observed_result']:errs.append(f'{x["id"]}: executed case lacks evidence')
    with (ROOT/'evidence/input-disposition.csv').open(encoding='utf-8',newline='') as handle:
        inputs=list(csv.DictReader(handle))
    nids={r['input_id'] for r in inputs if r['input_id'].startswith('N')}
    uids={r['input_id'] for r in inputs if r['input_id'].startswith('U')}
    if nids!={f'N{i:02d}' for i in range(1,41)}:errs.append('Numbered input coverage incomplete')
    if uids!={f'U{i:02d}' for i in range(1,31)}:errs.append('Thematic input coverage incomplete')
    if len({r['input_id'] for r in inputs})!=len(inputs):errs.append('Duplicate input ID')
    for row in inputs:
        if row['guidance_ids'] not in guide_ids:errs.append(f'{row["input_id"]}: unknown destination guidance')
        e=local_reference(ROOT/'README.md',row['destination'])
        if e:errs.append(f'{row["input_id"]}: {e}')
        if not row['rationale'] or row['disposition'] not in ['retained','consolidated','qualified','rejected','awaiting_evidence']:errs.append(f'{row["input_id"]}: missing disposition/reason')
    counts['input_units']=len(inputs)
    # Minimal Markdown lint intentionally excludes line length: prose and tables are readable when wrapped by clients.
    for p in sorted(ROOT.rglob('*.md')):
        text=p.read_text(encoding='utf-8');rel=p.relative_to(ROOT)
        if text.count('```')%2:errs.append(f'{rel}: unmatched code fence')
        if not text.endswith('\n'):errs.append(f'{rel}: missing final newline')
        if re.search(r'[ \t]+\n',text):
            # Markdown double spaces are permitted deliberate line breaks.
            if any(re.search(r'[\t]+$|(?<! ) $| {3,}$',line) for line in text.splitlines()):errs.append(f'{rel}: unintended trailing whitespace')
        if not re.search(r'^# ',text,re.M):errs.append(f'{rel}: no document title')
        codefree=re.sub(r'```.*?```','',text,flags=re.S)
        for ref in re.findall(r'\[[^\]]+\]\(([^)]+)\)',codefree):
            e=local_reference(p,ref)
            if e:errs.append(f'{rel}: {e}')
    for file in ['README.md','AGENTS.md','GOVERNANCE.md','SECURITY.md','CONTRIBUTING.md','LICENSE','CHANGELOG.md','.github/workflows/validate.yml']:
        if not (ROOT/file).is_file():errs.append(f'Missing required file {file}')
    for schema_file in (ROOT/'schemas').glob('*.json'):
        try:Draft202012Validator.check_schema(json.loads(schema_file.read_text()))
        except Exception as e:errs.append(f'{schema_file.name}: invalid schema: {e}')
    return errs,counts
def main():
    errors,counts=collect()
    for error in errors:print('ERROR:',error)
    print(json.dumps({'status':'fail' if errors else 'pass','counts':counts,'errors':len(errors)},sort_keys=True))
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
