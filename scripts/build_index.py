#!/usr/bin/env python3
"""Build a deterministic, local retrieval index. Drafts require explicit opt-in."""
from pathlib import Path
from datetime import date
import argparse,json,re,sys,yaml
ROOT=Path(__file__).resolve().parents[1]
def section_text(record):
    path,_,anchor=record['canonical_path'].partition('#');text=(ROOT/path).read_text()
    marker=f'<a id="{anchor}"></a>'
    if marker not in text:raise ValueError(f'Missing canonical anchor {record["id"]}')
    # Section includes full action, qualifications and source notes, not only the synopsis in YAML.
    before,after=text.split(marker,1)
    heading=before.rsplit('\n## ',1)[-1].strip()
    return '## '+heading+'\n\n'+after.split('\n## ',1)[0].strip()
def build(include_drafts=False,today=None):
    today=today or date.today().isoformat()
    records=yaml.safe_load((ROOT/'data/guidance.yaml').read_text())['records'];items=[]
    for r in records:
        approved=r['review_status']=='approved' and r['reviewed_on'] is not None and r['review_due'] is not None and r['reviewed_on']<=today<=r['review_due']
        if not approved and not include_drafts:continue
        if r['review_status']=='retired':continue
        items.append(dict(id=r['id'],title=r['title'],canonical_path=r['canonical_path'],text=section_text(r),authority_type=r['authority_type'],adoption_status=r['adoption_status'],review_status=r['review_status'],authoritative=False,source_ids=r['source_ids'],jurisdiction=r['jurisdiction'],limitations=r['limitations'],warning='Draft exploration only; not approved policy or legal advice.' if not approved else 'Approval is not legal certification; verify authority and applicability.'))
    return items
def search(items,query,limit=5):
    terms=set(re.findall(r'[a-z0-9]+',query.lower()))
    def score(r):
        if query.lower()==r['id'].lower():return 10000
        words=set(re.findall(r'[a-z0-9]+',(r['title']+' '+r['text']).lower()))
        return len(terms & words)
    return sorted([r for r in items if score(r)>0],key=lambda r:(-score(r),r['id']))[:limit]
def main():
    p=argparse.ArgumentParser();p.add_argument('--include-drafts',action='store_true');p.add_argument('--query');p.add_argument('--output',default='retrieval/index.jsonl');args=p.parse_args()
    items=build(args.include_drafts)
    if args.query:
        print(json.dumps({'mode':'draft_exploration' if args.include_drafts else 'approved_only','results':search(items,args.query),'empty_explanation':None if items else 'No approved current guidance records. Do not generate an authoritative answer.'},ensure_ascii=False,indent=2));return
    target=(ROOT/args.output).resolve()
    if not target.is_relative_to(ROOT):raise ValueError('Output must remain in repository')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in items))
    print(json.dumps({'records':len(items),'mode':'draft_exploration' if args.include_drafts else 'approved_only','output':str(target.relative_to(ROOT))}))
if __name__=='__main__':main()
