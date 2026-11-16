/* Browser-independent unit tests for local history, mode separation and recommendations. */
'use strict';
const assert = require('node:assert/strict');
const items = new Map();
global.localStorage = {
  getItem(key) { return items.has(key) ? items.get(key) : null; },
  setItem(key, value) { items.set(key, value); },
  removeItem(key) { items.delete(key); }
};
require('../model/route_history.js');
const h = global.PinkMapRouteHistory;
const a = ['p1', 'Rice University', 29.71656, -95.40294];
const b = ['p2', 'Hermann Park', 29.71486, -95.38889];
const from = h.snapshot(a), to = h.snapshot(b);
assert.deepEqual(h.snapshot(['me', 'My current location', 29.7, -95.3]),
  {id: 'me', name: 'My current location', lat: null, lon: null});
assert.equal(h.read().length, 0);
const make = (id, mode, at) => ({id, mode, at, from, to,
  routeIndex:0, durationSeconds:600, distanceMeters:1000});
assert.equal(h.add(make('1', 'driving', '2026-11-02T16:00:00Z')), true);
assert.equal(h.add(make('2', 'driving', '2026-11-03T16:00:00Z')), true);
assert.equal(h.add(make('3', 'walking', '2026-11-04T16:00:00Z')), true);
assert.equal(h.read().length, 3);
assert.equal(h.suggest(h.read(), {mode:'driving', fromId:'p1', hour:10})[0].count, 2);
assert.equal(h.suggest(h.read(), {mode:'walking', fromId:'p1', hour:10}).length, 0);
assert.equal(h.suggest(h.read(), {mode:'driving', fromId:'not-an-origin', hour:10}).length, 0);
assert.equal(h.updateSelected('2', 1, 650, 1200), true);
assert.equal(h.read().find(e=>e.id==='2').routeIndex, 1);
assert.equal(h.read().find(e=>e.id==='2').durationSeconds, 650);
assert.equal(h.remove('1'), true);
assert.equal(h.suggest(h.read(), {mode:'driving', fromId:'p1', hour:10}).length, 0);
assert.throws(()=>h.add({...make('4','driving','2026-11-03T16:00:00Z'), durationSeconds:-1}),
  /Invalid route history/);
items.set(h.KEY, '{broken');
assert.deepEqual(h.read(), []);
assert.equal(h.clear(), true);
assert.deepEqual(h.read(), []);
console.log('Browser route history tests passed (local save/read, GPS privacy, mode, frequent searches, update/remove, corrupt storage).');
