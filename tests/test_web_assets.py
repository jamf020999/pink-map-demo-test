"""Release/deployment consistency checks without HTTP requests."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class WebAssetsTests(unittest.TestCase):
    def test_html_still_has_518_places(self):
        html=(ROOT/'PinkMap_App.html').read_text(encoding='utf-8')
        match=re.search(r'const PLACES = (\[.*?\]);',html,flags=re.S)
        self.assertIsNotNone(match)
        places=json.loads(match.group(1))
        self.assertEqual(len(places),518)
        self.assertEqual(len({str(p[0]) for p in places}),518)

    def test_html_loads_browser_prediction_files(self):
        html=(ROOT/'PinkMap_App.html').read_text(encoding='utf-8')
        for name in ('model/traffic_model.js','model/predict.js', 'model/route_history.js'):
            self.assertIn(f'<script src="{name}"></script>',html)
            self.assertTrue((ROOT/name).is_file())
        self.assertIn('AI predicted travel time',html)


    def test_pedestrian_and_history_controls(self):
        html=(ROOT/'PinkMap_App.html').read_text(encoding='utf-8')
        for marker in ('value="walking"', 'value="driving"', 'id="routeHistory"',
                       'id="suggestions"', 'id="clearHistory"', 'id="exportHistory"',
                       "profile=mode==='walking'?'walking':'driving-traffic'"):
            self.assertIn(marker, html)
        self.assertIn('No traffic-delay AI prediction.', html)
        self.assertIn('historyStore.add(historyEntry)',html)

    def test_two_hour_cron(self):
        flow=(ROOT/'.github/workflows/collect.yml').read_text(encoding='utf-8')
        self.assertIn('cron: "7 */2 * * *"',flow)
        self.assertIn('python collect.py',flow)
        self.assertIn('MAPBOX_TOKEN',flow)

if __name__=='__main__':unittest.main()
