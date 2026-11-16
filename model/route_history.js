/* PinkMap's local-only trip-search history and frequency-based recommendations.
   No network calls, shared database, GPS trail recording, or claim of ML training.
   Usage patterns are based on successful route searches, not actual journeys. */
(function (global) {
  'use strict';
  const KEY = 'pinkmap_route_history_v1';
  const LIMIT = 300;
  const MODES = ['driving', 'walking'];

  function safeRead() {
    try {
      const rows = JSON.parse(global.localStorage.getItem(KEY) || '[]');
      return Array.isArray(rows) ? rows.filter(validEntry).slice(0, LIMIT) : [];
    } catch (_) { return []; }
  }
  function safeWrite(rows) {
    try { global.localStorage.setItem(KEY, JSON.stringify(rows.slice(0, LIMIT))); return true; }
    catch (_) { return false; }
  }
  function validPlace(p) {
    return p && typeof p.id === 'string' && p.id.length <= 110 &&
      typeof p.name === 'string' && p.name.length <= 400 &&
      (p.lat === null || (typeof p.lat === 'number' && Number.isFinite(p.lat))) &&
      (p.lon === null || (typeof p.lon === 'number' && Number.isFinite(p.lon)));
  }
  function validEntry(e) {
    return e && typeof e.id === 'string' && MODES.includes(e.mode) &&
      validPlace(e.from) && validPlace(e.to) && e.from.id !== e.to.id &&
      typeof e.at === 'string' && Number.isFinite(Date.parse(e.at)) &&
      Number.isFinite(e.durationSeconds) && e.durationSeconds > 0 &&
      Number.isFinite(e.distanceMeters) && e.distanceMeters > 0;
  }
  function snapshot(p) {
    // Never persist the user's live GPS coordinates. Replaying GPS asks permission again.
    return { id: String(p[0]), name: String(p[1]),
      lat: p[0] === 'me' ? null : Number(p[2]),
      lon: p[0] === 'me' ? null : Number(p[3]) };
  }
  function add(entry) {
    if (!validEntry(entry)) throw new Error('Invalid route history entry');
    const rows = safeRead();
    rows.unshift(entry);
    return safeWrite(rows);
  }
  function updateSelected(id, routeIndex, durationSeconds, distanceMeters) {
    const rows = safeRead();
    const entry = rows.find(e => e.id === id);
    if (!entry) return false;
    if (Number.isInteger(routeIndex) && routeIndex >= 0 &&
        Number.isFinite(durationSeconds) && durationSeconds > 0 &&
        Number.isFinite(distanceMeters) && distanceMeters > 0) {
      entry.routeIndex = routeIndex;
      entry.durationSeconds = durationSeconds;
      entry.distanceMeters = distanceMeters;
      return safeWrite(rows);
    }
    return false;
  }
  function remove(id) { return safeWrite(safeRead().filter(r => r.id !== id)); }
  function clear() { return safeWrite([]); }
  function hourInHouston(date) {
    const hour = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago', hour: 'numeric', hourCycle: 'h23'
    }).format(new Date(date));
    return Number(hour) % 24;
  }
  function hourBlock(hour) { return Math.floor(hour / 4); }
  function suggest(rows, options = {}) {
    const mode = MODES.includes(options.mode) ? options.mode : 'driving';
    const fromId = options.fromId == null ? null : String(options.fromId);
    const currentHour = Number.isInteger(options.hour) ? options.hour : hourInHouston(new Date());
    const groups = new Map();
    for (const r of rows) {
      if (!validEntry(r) || r.mode !== mode || (fromId !== null && r.from.id !== fromId)) continue;
      const key = JSON.stringify([r.from.id, r.to.id, mode]);
      let item = groups.get(key);
      if (!item) {
        item = { from: r.from, to: r.to, mode, count: 0, hourMatches: 0, lastUsed: r.at };
        groups.set(key, item);
      }
      item.count++;
      if (hourBlock(hourInHouston(r.at)) === hourBlock(currentHour)) item.hourMatches++;
      if (r.at > item.lastUsed) item.lastUsed = r.at;
    }
    return [...groups.values()].filter(item => item.count >= 2)
      .sort((a, b) => (b.hourMatches * 2 + b.count) - (a.hourMatches * 2 + a.count) ||
        b.lastUsed.localeCompare(a.lastUsed))
      .slice(0, 3);
  }
  global.PinkMapRouteHistory = Object.freeze({KEY, LIMIT, snapshot, add,
    read: safeRead, remove, clear, suggest, updateSelected, hourInHouston});
})(globalThis);
