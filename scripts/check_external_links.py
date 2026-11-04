#!/usr/bin/env python3
"""Optional network report. Reachability is not source verification or a CI gate."""
from pathlib import Path
import argparse,json,re,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=20);args=p.parse_args()
    urls=sorted({u for file in ROOT.rglob('*.md') for u in re.findall(r'\]\((https?://[^)]+)\)',file.read_text())})[:args.limit]
    rows=[]
    for url in urls:
        try:
            req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Inclusive-Employment-link-check/0.1'})
            with urllib.request.urlopen(req,timeout=8) as response:rows.append({'url':url,'status':response.status,'verification':'reachability_only'})
        except Exception as e:rows.append({'url':url,'status':'unknown_or_failed','detail':str(e)[:160],'verification':'not_verified'})
    target=ROOT/'validation/external-links.local.json';target.write_text(json.dumps(rows,indent=2));print(f'Wrote {len(rows)} bounded reachability results to {target.name}; manually review failures and redirects.')
if __name__=='__main__':main()
