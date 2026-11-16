# PinkMap: pedestrian routes, frequent searches, and saved route history

## New UI features

1. Choose **Driving** (existing `mapbox/driving-traffic`) or **Walking** (`mapbox/walking`).
2. Search the 518 built-in places, custom addresses or current GPS position. For walking, Mapbox returns the pedestrian network's approved/available routing options, with distance, duration and walking directions if provided. Do not equate API-returned routes with official safety or accessibility approval.
3. Driving displays current/typical travel-time differences and the **experimental historical Random Forest** travel-time prediction. Walking has no traffic-versus-typical label and does not receive the driving AI prediction.
4. Every successful search adds a browser-local entry under **Recent routes**. Repeat the search to get **fresh** Mapbox results (no old traffic cache), or delete/export/clear the history.
5. After the same origin→destination pair is searched **at least twice in the same mode**, a **Predicted destination** recommendation appears. It uses an on-device statistical frequency ranking with extra weight for the current four-hour **Houston** time interval. This is a *prediction of what route a user may search next*, not a prediction of whether a person physically traveled it.

## Data and privacy

`model/route_history.js` stores up to 300 recent route-search records in `localStorage` key `pinkmap_route_history_v1`, limited to the current browser/profile. No server or database is used. A route record includes IDs/names, non-GPS destination coordinates where available, transport mode, searched timestamp, returned estimate and selected route index. Real-time GPS coordinates of the user's **My current location** are intentionally not saved; repeating a GPS-origin search asks for current location permission again. Custom address snapshots are kept locally and may reveal sensitive location choices; deleting/clearing history avoids retaining those on shared computers.

Export saves JSON to the user's device. There is no cross-device sync or background travel tracking. Local history cannot validate that the individual actually drove or walked the trip. Mapbox still receives coordinates for requested directions subject to Mapbox policies.

## Model and collector scope

- `collect.py` and the GitHub Actions workflow continue to monitor 50 fixed **driving** OD pairs, with the schedule requesting a run every two hours.
- The Random Forest model still uses historical **driving** route observations from the original 15 monitored routes, and remains experimental for arbitrary places.
- The separate **frequent-destination predictor** learns from this browser's searches (mode, origin, repeated destination and Houston time block) and never changes the trained Random Forest weights. It is a simple interpretable pattern-recommender, not a trained neural network or proof of forecasting actual journeys.
- If the walking Mapbox API fails, the application shows an error, not a direct-line pedestrian shortcut.

## Test

Run `node tests/test_web_history.js` and `python tests/browser_smoke.py` (requires Playwright + Chromium), plus the existing test suite. Live deployment checks are listed in `TESTING.md` as S16–S24. No new backend or database is necessary for this prototype.
