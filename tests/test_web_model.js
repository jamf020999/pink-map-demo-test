'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
require(path.join(root, 'model/traffic_model.js'));
require(path.join(root, 'model/predict.js'));
const ai = globalThis.PinkMapAI;
assert.ok(ai, 'browser AI module should load');
const chicago = ai.houstonClock(new Date('2026-11-15T13:00:00Z'));
assert.equal(chicago.hour, 7);
assert.equal(chicago.dow, 6);
for (const v of JSON.parse(fs.readFileSync(path.join(root, 'model/test_vectors.json'))).examples) {
  const result = ai.predictFeatures(v.features);
  assert.ok(Math.abs(result - v.expected_delay_seconds) < 0.01,
    `Python/JavaScript prediction mismatch: ${result} vs ${v.expected_delay_seconds}`);
}
const example = ai.predictRoute(7.2, 720, new Date('2026-11-15T13:00:00Z'));
assert.ok(Number.isFinite(example.estimated_seconds));
assert.equal(example.trained_route_count, globalThis.PINKMAP_TRAFFIC_MODEL.data_routes.length);
assert.equal(ai.predictRoute(0, 720), null);
console.log('Browser AI tests passed (time zone, prediction parity, inputs).');
