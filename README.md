# PinkMap — Houston traffic-aware route explorer

PinkMap helps users compare **Mapbox driving and walking routes**, see whether each option is faster/slower than its *typical travel time*, and inspect a separate **experimental machine-learning estimate** of traffic delay. This project was created for an AI/ML course at Houston Community College (Fall 2026).

**Team:** Phu, Jose, Mary, Christian  
**Live application:** https://phunguyenm.github.io/PinkMap/PinkMap_App.html

## Current architecture

```
50 fixed origin/destination pairs (collect.py)
     | GitHub Actions requests collection every 2 hours (UTC)
     v
Mapbox Directions API (driving-traffic)
     v
data/auto_collected.csv  →  model_pipeline.py + train_model.py
                                   |
                                   v
                         model/traffic_model.js
                                   |
                                   v
PinkMap_App.html  ←  model/predict.js  [historical driving ML estimate]
       |           ←  model/route_history.js [browser-local usage prediction]
       |
       +---------- Mapbox Directions API [driving-traffic OR walking paths]
       +---------- Mapbox Geocoding [optional new addresses]
```

**No separate backend or database is needed for the current prototype.** The map uses Mapbox's APIs in the browser; the historical collector runs as a scheduled GitHub Action; the small trained model is embedded in a public JavaScript asset. A shared server-side database is explicitly **deferred**.

## Use the live demo

1. Open the [PinkMap live demo](https://phunguyenm.github.io/PinkMap/PinkMap_App.html) (or open `PinkMap_App.html` locally with its `model/` folder beside it).
2. Choose a **From** and **To** location using the searchable boxes (518 built-in locations at the time of this release). GPS and address search require browser permission and access to the Mapbox service.
3. Select **Driving** or **Walking**, then click **Show routes**. Mapbox returns route geometry, travel time and distance. **Only Driving** provides current traffic versus typical time; walking provides pedestrian routes and turn instructions where available.
4. **Driving** cards can also display **AI predicted travel time (experimental)** based on the trained historical model. This value is calculated **independently** from current `r.duration` so it is not a restatement of the Mapbox traffic duration.

### New: pedestrian routes, route history, and personalized suggestions

- **Pedestrian routes:** Choose Walking for Mapbox `mapbox/walking` directions based on mapped sidewalks and paths. The app displays only actual Mapbox-returned route geometry; it does **not** draw imaginary direct-line paths. Walking does not use the driving-traffic or driving-trained AI model. Map data is not an accessibility or safety certification: construction, closed paths, crossings, and wheelchair access must be checked independently.
- **Saved route history:** Every successful route search is recorded locally in this browser, including the selected origin/destination, mode, date, travel estimate and selected alternative. Use **Repeat** to rerun it, **×** to delete a single entry, **Clear history** for all, or **Export history** to download a JSON backup. History is not synced to GitHub or a shared database. GPS coordinates selected through **My current location** are **not** saved to history; repeating those routes requests current browser location permission again.
- **Frequent-route predictions:** Once a particular origin→destination pair has been searched at least **twice in the same travel mode**, PinkMap shows a **Predicted destination / Predicted frequent routes** suggestion. It ranks repeated searches, giving extra weight to searches from the current four-hour Houston time block. This is an on-device **usage-frequency statistical prediction**, not the historical Random Forest traffic model; it predicts what destination a user may choose, not traffic speed. These predictions describe route *searches*, not confirmed journeys.
- **Separate AI travel-time predictions:** The historical Random Forest still displays an experimental estimate on Driving cards only. The model was trained on the original 15 monitored driving routes; walking performance and predictions on arbitrary routes have not been validated.

**Distinguish the two estimates:**
- **Current travel time / “Fastest now” / “Least congested”** are computed from *live Mapbox responses*, not the ML model.
- **AI predicted travel time** is an *experimental prediction* based on typical duration, distance and Houston calendar features, not a guarantee, a navigation recommendation, or measured GPS travel time.

The historical dataset used to train the currently exported model contains **2,595 observations of the original 15 monitored routes**, collected October 7–November 15, 2026. **No observed data for routes 16–50 is present in the included historical CSV.** Its accuracy on the new routes or arbitrary pairs of the 518 locations has **not** been established. The model should be retrained after the new routes accumulate data.

## Files and folders

| Path | Role |
|---|---|
| `PinkMap_App.html` | Live browser interface and Mapbox routing |
| `collect.py` | Defines **50** monitored routes and collects one complete batch per successful run |
| `.github/workflows/collect.yml` | Collection requested **every 2 hours** (cron `7 */2 * * *`, UTC); supports manual runs |
| `PinkMap_1_Collect_Data.ipynb` | Manual Google Colab collector with the same 50 fixed routes |
| `data/auto_collected.csv` | Preserved historical Mapbox traffic observations (not GPS journeys) |
| `data/processed/` | Optional cleaned train/validation/test CSV snapshots generated by Notebook 2 |
| `PinkMap_2_Clean_Explore_Baseline.ipynb` | Cleaning, EDA, baseline, and collection-run-grouped train/validation/test splits |
| `model_pipeline.py` | Reusable data preparation and leakage-controlled split logic |
| `train_model.py` | Trains, validates, tests, and exports a traffic-delay regressor |
| `PinkMap_3_Train_Deploy_Model.ipynb` | Notebook interface for the training/export script |
| `model/traffic_model.js` | Static trained-model weights loaded by the website |
| `model/predict.js` | JavaScript driving model inference, using **America/Chicago** time |
| `model/route_history.js` | Browser-local route history and frequent-destination prediction logic |
| `model/metrics.json` | Historical model validation/test results |
| `tests/`, `.github/workflows/tests.yml` | Python, Node, and mocked-browser automated checks |
| `scripts/check_collection.py` | Shows current coverage and whether complete 50-route runs have arrived |
| `DEPLOYMENT.md`, `TESTING.md`, `DEMO_GUIDE.md` | Deployment, acceptance testing, and class demo instructions |
| `WEEKS_11_13_STATUS.md` | Course-requirements tracking and unverified items |

## Set up automatic 50-route collection

1. GitHub repository → **Settings → Secrets and variables → Actions → New repository secret**. Create `MAPBOX_TOKEN` with a token authorized for the Directions API. **Never commit a private token.**
2. Commit `collect.py`, `.github/workflows/collect.yml`, and the entire `tests/` directory together.
3. The cron expression `7 */2 * * *` **requests a run every 2 hours** at minute 7, **UTC**. GitHub may delay or skip scheduled runs; a cron schedule is not proof of an executed collection.
4. Open **Actions → Collect traffic data → Run workflow** to test one full collection after committing. This requests 50 Mapbox route estimates and may use API quota.
5. Confirm its log says **“Saved 50 complete observations”** and inspect the updated `data/auto_collected.csv`.
6. Run `python scripts/check_collection.py` to verify coverage. The 35 new routes cannot have historical observations until new collections are committed.

The collector validates 50 unique route IDs and coordinates, retries a failed HTTP request once, and **does not append a partial 50-route batch**. If any route fails twice, the workflow fails, prints the failing route IDs, and preserves the previous CSV. Existing observations are never erased during successful appends.

### Manual Colab collection

`PinkMap_1_Collect_Data.ipynb` also contains the 50 routes. In Colab, insert your public Mapbox token and run all cells. It saves `route_data.csv` to Google Drive. This is **separate** from the automatic GitHub collector and does not update the repository unless you upload/merge its CSV yourself. Keep its data separate until properly deduplicated.

## Train and redeploy the historical AI model

From the full project root with Python 3.12 or compatible:

```bash
python -m pip install -r requirements-model.txt
python train_model.py
```

Or run `PinkMap_3_Train_Deploy_Model.ipynb` with the complete repository files available. The script splits **whole collection runs** chronologically, evaluates linear and several Random Forest candidates on validation data, retrains the selected model on train+validation data, and measures error on untouched future test runs. It writes:

- `model/traffic_model.js`: trained model that can be loaded by the browser as a normal script (works without a database or web server).
- `model/metrics.json`: data coverage, split counts, and model/test error metrics.
- `model/test_vectors.json`: numerical test cases used to verify that Python and JavaScript predictions agree.

For the included historical snapshot, the selected Random Forest (depth 6) achieved **52.00 seconds test MAE**, versus **65.65 seconds test MAE** for always predicting zero delay; **35** collection runs (**525** rows) were held out for testing. These are prediction errors, **not seconds of commute time saved**. They apply only to the historical 15-route coverage and must be retested after adding 16–50.

The browser model uses **only** `[distance_miles, typical_seconds, hour_sin, hour_cos, dow_sin, dow_cos, is_weekend, rush_hour]`. It does **not** use the current observed traffic time, already-calculated delay, speed derived from traffic time, or route ID; thus it can issue experimental estimates for unfamiliar routes, but unfamiliar-route accuracy is not established.

## Automated tests and manual sign-off

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_web_model.js
node tests/test_web_history.js
python -m playwright install chromium
python tests/browser_smoke.py
```

See **[FEATURES_WALKING_HISTORY.md](FEATURES_WALKING_HISTORY.md)** for details of the new features and **[TESTING.md](TESTING.md)** for full details and for the **manual live Mapbox validation steps** required before presenting. GitHub Actions' `PinkMap checks` workflow runs Python/Node/browser tests on pushes and pull requests. A passing mocked browser test is **not** proof that real Mapbox routing, device GPS, or every one of 50 routes works live.

## Deploy to GitHub Pages

Publish the updated files, including `model/`, without replacing a newer historical CSV. For local testing from an extracted folder, prefer `python -m http.server 8000` and `http://localhost:8000/PinkMap_App.html` if your browser blocks `file://` access. Configure **Settings → Pages** to deploy the selected branch's root directory (if Pages is not already configured). The browser loads `model/traffic_model.js`, `model/predict.js`, and `model/route_history.js` relative to `PinkMap_App.html`; do **not** upload only the HTML file. Visit the live demo and hard-refresh after deploying. See **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## Data limitations and privacy

The underlying times are **Mapbox API estimates**; the team has not measured actual GPS drive duration. The dataset combines samples from a limited set of fixed routes and has gaps in time-of-day coverage. Additional routes 16–50 initially have no samples. It should not be presented as a validated citywide traffic forecast. The live demo does not save personal GPS travel histories to the historical CSV. The new optional route-search history is saved in browser `localStorage`, **not** the public traffic dataset. It includes custom addresses from searches, which may be sensitive, but never stores live GPS coordinates. It can be exported or cleared by the user; avoid running in shared browsers if you do not want your recent searches visible to the next person. Browser-saved personal addresses stay in local browser storage when `API_URL` is empty, but the origin/destination coordinates selected for directions (including GPS, if chosen) **are sent to Mapbox** to calculate routes. The public Mapbox browser token is visible in HTML by design; consider restricting its allowed origins and usage in the Mapbox dashboard.

## Course deliverables

Use [WEEKS_11_13_STATUS.md](WEEKS_11_13_STATUS.md), [TESTING.md](TESTING.md), and [DEMO_GUIDE.md](DEMO_GUIDE.md). See [TEST_REPORT.md](TEST_REPORT.md) and [RELEASE_NOTES.md](RELEASE_NOTES.md) for the local test outcomes and safe update instructions. The team must still run the real deployed build, capture test evidence, and gather teammate/user feedback; these cannot be proved by a code archive alone.
