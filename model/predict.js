/* Runs in a browser or Node; relies only on the public, versioned tree data. */
(function (global) {
  'use strict';
  const model = global.PINKMAP_TRAFFIC_MODEL;
  if (!model || model.schema !== 1) return;
  const weekdays = {Mon:0,Tue:1,Wed:2,Thu:3,Fri:4,Sat:5,Sun:6};

  function houstonClock(date) {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago', hour: 'numeric', hourCycle: 'h23', weekday: 'short'
    });
    const parts = formatter.formatToParts(date);
    const hourText = parts.find(x => x.type === 'hour')?.value;
    const dayText = parts.find(x => x.type === 'weekday')?.value;
    const hour = Number(hourText) % 24;
    const dow = weekdays[dayText];
    if (!Number.isInteger(hour) || !Number.isInteger(dow)) throw new Error('Could not calculate Houston time');
    return {hour, dow};
  }

  function getFeatures(miles, typicalSeconds, date) {
    const {hour, dow} = houstonClock(date);
    const tau = 2 * Math.PI;
    return [miles, typicalSeconds, Math.sin(tau*hour/24), Math.cos(tau*hour/24),
      Math.sin(tau*dow/7), Math.cos(tau*dow/7), dow >= 5 ? 1 : 0,
      [7,8,16,17].includes(hour) ? 1 : 0];
  }

  function predictFeatures(x) {
    const m = model.model;
    if (m.type === 'linear') return m.intercept + m.coef.reduce((acc, c, i) => acc + c * x[i], 0);
    if (m.type === 'forest') {
      let total = 0;
      for (const tree of m.trees) {
        let node = tree;
        while (Array.isArray(node)) node = x[node[0]] <= node[1] ? node[2] : node[3];
        total += node;
      }
      return total / m.trees.length;
    }
    throw new Error('Unsupported PinkMap model format');
  }

  function predictRoute(miles, typicalSeconds, date = new Date()) {
    if (!Number.isFinite(miles) || miles <= 0 || !Number.isFinite(typicalSeconds) || typicalSeconds <= 0) return null;
    const delay = predictFeatures(getFeatures(miles, typicalSeconds, date));
    const estimated = Math.max(1, typicalSeconds + delay);
    return {delay_seconds: delay, estimated_seconds: estimated,
      trained_route_count: model.data_routes.length,
      held_out_mae_seconds: model.test_mae_seconds};
  }

  global.PinkMapAI = Object.freeze({predictRoute, predictFeatures, getFeatures, houstonClock});
})(globalThis);
