"""Network-free collector and route integrity tests; safe for GitHub Actions."""
import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

import collect

ROOT = Path(__file__).resolve().parents[1]


def fake_response():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {'routes':[{'distance':12345.0,'duration':800.1,'duration_typical':755.4}]}
    return response


class CollectorTests(unittest.TestCase):
    def test_exactly_50_valid_routes(self):
        self.assertTrue(collect.validate_routes())
        self.assertEqual([r['route_id'] for r in collect.ROUTES],list(range(1,51)))

    def test_notebook_route_list_matches_collector(self):
        import ast
        nb=json.loads((ROOT/'PinkMap_1_Collect_Data.ipynb').read_text())
        lists=[]
        for c in nb['cells']:
            if c['cell_type'] != 'code':continue
            tree=ast.parse(''.join(c['source']))
            for n in tree.body:
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ROUTES' for t in n.targets):
                    lists.append(ast.literal_eval(n.value))
        self.assertEqual(len(lists),1)
        self.assertEqual(lists[0],collect.ROUTES)

    def test_mapbox_parsing_and_common_timestamp(self):
        timestamp=datetime(2026,11,15,17,7,tzinfo=ZoneInfo('America/Chicago'))
        with patch.object(collect.requests,'get',return_value=fake_response()) as get:
            result=collect.get_route_row(collect.ROUTES[0],timestamp,token='fake-token')
        self.assertEqual(result['collected_at'],'2026-11-15 17:07:00')
        self.assertAlmostEqual(result['distance_miles'],7.671,places=3)
        self.assertEqual(result['typical_seconds'],755.4)
        self.assertEqual(get.call_args.kwargs['params']['access_token'],'fake-token')

    def test_invalid_response_retries_then_fails(self):
        response=fake_response()
        response.json.return_value={'routes':[{'distance':0,'duration':0,'duration_typical':None}]}
        with patch.object(collect.requests,'get',return_value=response) as get, patch.object(collect.time,'sleep'):
            with self.assertRaises(RuntimeError):
                collect.get_route_row(collect.ROUTES[0],datetime.now(ZoneInfo('America/Chicago')),token='fake-token')
        self.assertEqual(get.call_count,2)

    def test_failed_batch_does_not_modify_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'data.csv'; out.write_text('original-bytes\n')
            with patch.object(collect,'TOKEN','test-token'), patch.object(collect,'OUT_FILE',str(out)), \
                 patch.object(collect,'get_route_row',side_effect=RuntimeError('offline')):
                with self.assertRaises(SystemExit) as err:
                    collect.main()
            self.assertEqual(err.exception.code,1)
            self.assertEqual(out.read_text(),'original-bytes\n')

    def test_complete_batch_is_atomic_and_preserves_previous_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'data.csv'
            prior={k:'' for k in collect.COLUMNS}; prior.update({'route_id':1,'collected_at':'2026-10-07 14:41:38'})
            with out.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=collect.COLUMNS);writer.writeheader();writer.writerow(prior)
            def fake_route(trip, ts):
                r={k:'x' for k in collect.COLUMNS};r.update({'route_id':trip['route_id'],
                   'collected_at':ts.strftime('%Y-%m-%d %H:%M:%S')});return r
            with patch.object(collect,'TOKEN','test-token'), patch.object(collect,'OUT_FILE',str(out)), \
                 patch.object(collect,'get_route_row',side_effect=fake_route):
                collect.main()
            with out.open() as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),51)
            self.assertEqual(rows[0]['collected_at'],'2026-10-07 14:41:38')
            self.assertEqual({r['route_id'] for r in rows[1:]},{str(i) for i in range(1,51)})
            self.assertEqual(len({r['collected_at'] for r in rows[1:]}),1)


if __name__ == '__main__': unittest.main()
