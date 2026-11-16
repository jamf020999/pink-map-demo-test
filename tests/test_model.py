"""Model/data contracts; no calls to Mapbox or external services."""
import json
import unittest
from pathlib import Path

import pandas as pd

from model_pipeline import FEATURE_NAMES, prepare_data, split_runs, features

ROOT=Path(__file__).resolve().parents[1]

class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=prepare_data(pd.read_csv(ROOT/'data/auto_collected.csv'))
        cls.train,cls.val,cls.test=split_runs(cls.df)

    def test_data_not_deleted(self):
        self.assertGreaterEqual(len(self.df),2595)
        self.assertGreaterEqual(self.df.route_id.nunique(),15)
        self.assertTrue(self.df.traffic_seconds.gt(0).all())

    def test_run_split_no_leakage(self):
        for a,b in [(self.train,self.val),(self.train,self.test),(self.val,self.test)]:
            self.assertFalse(set(a.collection_run)&set(b.collection_run))
        self.assertLess(self.train.collected_at.max(),self.val.collected_at.min())
        self.assertLess(self.val.collected_at.max(),self.test.collected_at.min())

    def test_no_target_leakage_in_features(self):
        for name in ('traffic_seconds','delay_seconds','traffic_status','avg_speed_mph','route_id'):
            self.assertNotIn(name,FEATURE_NAMES)
        self.assertEqual(list(features(self.train).columns),FEATURE_NAMES)

    def test_serialized_model_and_metrics(self):
        model=(ROOT/'model/traffic_model.js').read_text()
        self.assertIn('globalThis.PINKMAP_TRAFFIC_MODEL = ',model)
        metrics=json.loads((ROOT/'model/metrics.json').read_text())
        self.assertLessEqual(metrics['source_rows'],len(self.df))
        self.assertEqual(metrics['train_rows']+metrics['validation_rows']+metrics['test_rows'],metrics['source_rows'])
        self.assertEqual(metrics['source_route_count'],len(metrics['source_route_ids']))

if __name__=='__main__': unittest.main()
