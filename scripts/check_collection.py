"""Read-only 50-route rollout checker; run after publishing the new collector."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

CSV=Path(__file__).resolve().parents[1]/'data'/'auto_collected.csv'
with CSV.open(newline='',encoding='utf-8') as f:
    data=list(csv.DictReader(f))
route_counts=Counter(int(r['route_id']) for r in data)
by_timestamp=defaultdict(set)
for r in data:
    by_timestamp[r['collected_at']].add(int(r['route_id']))
complete=[t for t,ids in by_timestamp.items() if ids == set(range(1,51))]
print('Rows in file:',len(data))
print('Unique historical route IDs:',len(route_counts))
print('Routes 16–50 with observations:',sum(route_counts[i]>0 for i in range(16,51)),'/ 35')
print('Complete 50-route runs with one timestamp:',len(complete))
print('Latest complete 50-route run:',max(complete) if complete else 'NONE YET')
print('Last recorded observation:',max((r['collected_at'] for r in data),default='NONE'))
if not complete:
    print('ACTION: Confirm the new collector was committed and inspect GitHub Actions logs.')
