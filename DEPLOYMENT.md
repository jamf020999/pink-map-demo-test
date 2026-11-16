# Deployment and runbook — Weeks 11 and 13

## Prerequisites

- A GitHub repository containing the PinkMap files at the **repository root**, not a nested second `PinkMap-main/` directory.
- GitHub Actions and GitHub Pages enabled; a Mapbox token with the Directions API available.
- GitHub repository secret **`MAPBOX_TOKEN`** for the scheduled Python collector. Do **not** commit private credentials.
- The site's existing Mapbox **public** browser token must be valid for the host where the site is deployed.

## Publish this release

1. **Back up** the existing repo or commit before changing files. Do not delete `data/auto_collected.csv`.
2. Extract the updated ZIP locally. Copy the **contents of `PinkMap-main/`** to the same root folder on the GitHub repository. Commit the changed and newly added files together, including `model/`, `tests/`, `scripts/`, new notebook, documentation and workflow files.
3. Check **Actions → PinkMap checks** for passing Python, JavaScript and mocked browser tests. A failing test is a release blocker until fixed.
4. Check **Actions → Collect traffic data**. Use **Run workflow** once to test a full real collection (50 Mapbox requests). If it fails, inspect the failed route IDs; the collector refuses to write an incomplete batch.
5. Open the repo's `data/auto_collected.csv` and confirm a newer run containing **50 rows** (route IDs 1–50, shared `collected_at` timestamp). From a clone, run `python scripts/check_collection.py`.
6. Verify `.github/workflows/collect.yml` contains `cron: "7 */2 * * *"`: every **two hours at minute 7 UTC**, *best effort*. Do not confuse schedule frequency with the actual number of completed runs.
7. In **Settings → Pages**, confirm publishing from the repository branch and **root** (or existing build workflow). Wait for the Pages deployment to report success; then refresh the demo URL.
8. Test `https://phunguyenm.github.io/PinkMap/PinkMap_App.html`: choose two locations, show routes, and verify the additional **AI predicted travel time (experimental)** line. Open browser Developer Tools if model scripts fail; check that the relative `model/traffic_model.js` and `model/predict.js` return HTTP 200.
9. Capture screenshots of the live demonstration, GitHub Actions logs, CSV, model accuracy report and GitHub Pages deployment result for the class.

**Important:** The assistant can prepare a release ZIP but **cannot verify a GitHub commit or live deployment from the ZIP alone**. The team must perform the steps above in its own GitHub account.

## What is deployed, and what is not

- **Deployed by GitHub Pages:** HTML+JavaScript navigation interface and a small **static trained AI model**; no backend process is needed for in-browser ML inference.
- **GitHub Actions backend:** Scheduled Python collector that calls Mapbox, checks completeness, and commits the resulting CSV.
- **External services:** Mapbox Directions, Geocoding, map imagery and GPS browser permissions.
- **Not deployed:** A shared application database, a prediction REST API, or live retraining at every collection. These are optional future expansions and are not claimed as completed.

## Refreshing the model after more 50-route data arrives

```bash
python -m pip install -r requirements-model.txt
python scripts/check_collection.py
python train_model.py
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_web_model.js
```

Check `model/metrics.json` for the new route coverage and accuracy before committing the exported files. Monitor whether the model beats the zero-delay baseline on independent newer data. A retrained model is not automatically better.

## Troubleshooting

- **Collector says missing token:** create/update the `MAPBOX_TOKEN` *GitHub Actions secret*, not a value inside a tracked source file.
- **A route fails or Mapbox rejects requests:** look at route ID, coordinates, token permissions, rate limits and the Mapbox error. No rows are appended from that incomplete collection; try again only after fixing the cause.
- **No scheduled run at the expected minute:** GitHub's scheduler may delay or skip jobs, and can disable schedules on inactive repositories. Look at actual Actions history before making a collection-frequency claim.
- **HTML routes work but no AI estimate:** ensure `model/traffic_model.js` and `model/predict.js` were committed in the correct relative folder. The page displays a warning if no model module loads.
- **Map is blank or directions fail:** check browser console, public Mapbox token restrictions, network access, Geocoding/Directions API responses and (for GPS) browser location permission. Use two built-in places if GPS is blocked.
- **Different numbers in notebooks and the website:** historic ML predicts a *delay from usual*; Mapbox currently computes *actual traffic-dependent routing*. They are not the same measurement. Model accuracy numbers from the old 15-route dataset do not validate the new 35 routes.
- **Git push fails in collection workflow:** check default-branch protection and workflow `contents: write` permission; resolve merge/rebase conflicts without erasing prior data.

## Rollback

If a deployment fails, revert the release commit and republish from a known working GitHub commit. **Never overwrite the collected CSV with a truncated version**; preserve new observations in a backup before reverting changes that include data.

## New release: Walking / frequent route suggestions / local search history

Deploy **all three** browser scripts together: `model/traffic_model.js`, `model/predict.js`, and `model/route_history.js`. The latter adds only browser-local state, so **no database, backend, or new GitHub secret is required**.

Verify from the deployed HTML: 1) Driving displays live traffic plus the experimental historical AI estimate; 2) Walking triggers `mapbox/walking`, displays Mapbox pedestrian routes and directions, and does **not** show a traffic/AI card; 3) repeat the same route twice to display a frequency-based destination suggestion; 4) the new trip appears in History and can be repeated, deleted, exported, and cleared. Check the browser Network tab for the correct profile. Route history remains private to each browser/profile and is not synced among students.

**Do not confuse** the browser's on-device history/suggestions with automated GitHub traffic collection. The latter still monitors **50 driving-traffic OD pairs every 2 hours (requested)**; using Walking in the website does not add pedestrian observations to `data/auto_collected.csv`.

Walking follows Mapbox's mapped path network. That is not a guarantee that all sidewalks, crossings, lighting, closures or accessibility conditions are safe or current. The team should test representative local routes before presenting.
