"""Shared, leakage-conscious traffic-delay training utilities.

Feature inputs do NOT include live traffic duration, traffic status, actual speed,
current delay, or route ID. This permits *experimental* inference on new routes,
but accuracy on new routes is not established by historical test metrics.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED = ['collected_at','route_id','distance_miles','traffic_seconds','typical_seconds']
FEATURE_NAMES = ['distance_miles', 'typical_seconds', 'hour_sin', 'hour_cos',
                 'dow_sin', 'dow_cos', 'is_weekend', 'rush_hour']


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    for col in ['distance_miles','traffic_seconds','typical_seconds','route_id']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['collected_at'] = pd.to_datetime(df['collected_at'], errors='coerce')
    df = df.dropna(subset=REQUIRED)
    df = df[(df['distance_miles'] > 0) & (df['traffic_seconds'] > 0) & (df['typical_seconds'] > 0)]
    df = df.drop_duplicates(subset=['route_id','collected_at'])
    # Stable sort by timestamp and route ID, so all records from a collector invocation
    # stay adjacent even when an invocation uses one shared timestamp.
    df = df.sort_values(['collected_at', 'route_id'], kind='mergesort').reset_index(drop=True)
    if df.empty:
        raise ValueError('No valid traffic records')
    gap = df['collected_at'].diff().dt.total_seconds().fillna(999999)
    id_reset = df['route_id'].diff().fillna(-1) <= 0
    df['collection_run'] = ((gap > 600) | id_reset).cumsum().astype(int)
    df['delay_seconds'] = df['traffic_seconds'] - df['typical_seconds']
    dow = df['collected_at'].dt.dayofweek
    hour = df['collected_at'].dt.hour
    df['hour_sin'] = np.sin(2*np.pi*hour/24)
    df['hour_cos'] = np.cos(2*np.pi*hour/24)
    df['dow_sin'] = np.sin(2*np.pi*dow/7)
    df['dow_cos'] = np.cos(2*np.pi*dow/7)
    df['is_weekend'] = (dow >= 5).astype(int)
    df['rush_hour'] = hour.isin([7,8,16,17]).astype(int)
    return df


def split_runs(df: pd.DataFrame):
    runs = sorted(df['collection_run'].unique())
    n = len(runs)
    if n < 10:
        raise ValueError('At least 10 independent collection runs required')
    train_end = max(1, int(n*0.70))
    val_end = max(train_end+1, int(n*0.80))
    train = df[df.collection_run.isin(runs[:train_end])].copy()
    val = df[df.collection_run.isin(runs[train_end:val_end])].copy()
    test = df[df.collection_run.isin(runs[val_end:])].copy()
    assert not (set(train.collection_run)&set(val.collection_run))
    assert not (set(train.collection_run)&set(test.collection_run))
    assert not (set(val.collection_run)&set(test.collection_run))
    assert max(train.collected_at) < min(val.collected_at)
    assert max(val.collected_at) < min(test.collected_at)
    return train, val, test


def features(df: pd.DataFrame):
    return df[FEATURE_NAMES].astype(float)
