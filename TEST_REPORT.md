# PinkMap — local verification report (release candidate)

**Source inspected:** `PinkMap_Weeks11-13_COMPLETE_Updated(1).zip` supplied for this update. Tests were executed on the prepared source tree in the current working environment using Python, Node and headless Chromium. **This is not a report of a live GitHub Pages deployment or Mapbox's production service.**

## Results

| Check | Result |
|---|---|
| `collect.py --check` | PASS: exactly 50 fixed routes with unique IDs 1–50 |
| `PinkMap_1_Collect_Data.ipynb` route definitions | PASS: identical 50 routes to `collect.py` |
| Historical dataset preservation | PASS: SHA-256 identical to CSV in uploaded ZIP |
| Python unit/data/integration tests | PASS: 14/14 |
| JS forecast parity vs Python reference predictions | PASS |
| Browser-local route-history JS unit tests | PASS: storage, frequency suggestions, separate walking/driving histories, deletion, corrupted storage and no retained GPS coordinates |
| Browser mocked integration test | PASS: driving route alternatives and historical AI cards, walking profile and steps with no traffic AI, frequent destination suggestions, saved route history repeat/delete/clear, empty walking response and no JS errors |
| Notebook 2 local execution | PASS: clean/split/EDA/baseline, saved processed CSVs |
| Notebook 3 local execution | PASS: training, independent test report and browser model export |
| Original built-in navigation locations | PASS: 518 retained in HTML |
| Walking Mapbox API verified on a live account | **NOT RUN**: requires live Mapbox request after deployment; mocked pedestrian response passed |
| Updated collection schedule in `collect.yml` | PASS: `7 */2 * * *` requests every two hours UTC |
| New historical observations for routes 16–50 | **NOT YET**: provided CSV has no records for these IDs |
| Actual 50-route Mapbox request test | **NOT RUN**: requires real GitHub token/Mapbox service |
| Real deployed website verification | **NOT RUN** for this new release: team must commit/upload and check GitHub Pages |
| New automated CI workflow on GitHub | **NOT YET RUN**: runs once updated files are committed |
| Manual user test, device GPS, mobile performance | **NOT RUN**: requires team participation and live devices |
| Shared application database | **DEFERRED BY REQUEST** |

## Data and model snapshot

| Metric | Result |
|---|---:|
| Historical observations | 2,595 |
| Historical routes represented | 15 |
| Configured collector routes | 50 |
| Inferred independent historical collection runs | 173 |
| Train / validation / test observations | 1,815 / 255 / 525 |
| Train / validation / test runs | 121 / 17 / 35 |
| Selected model | Random Forest, 100 trees, depth 6, minimum leaf 8 |
| Baseline (zero delay) test MAE | 65.65 seconds |
| Selected model test MAE | 52.00 seconds |
| Selected model test RMSE | 96.65 seconds |

These model statistics reflect the preserved historical dataset and **do not validate forecasting on newly configured routes 16–50**. The new interface displays the forecast as experimental, alongside a *separate* live Mapbox route estimate.

## Required team sign-off after uploading the release

1. Check that GitHub Actions **PinkMap checks** passes on the release commit.
2. Run **Collect traffic data** manually once. Confirm exactly **50 appended rows**, including IDs 16–50, with a shared timestamp, then confirm a subsequent scheduled run actually occurs.
3. Load the updated public **PinkMap_App.html** from GitHub Pages, calculate a real Mapbox route, and confirm the AI forecast is displayed independently.
4. Test on the presentation device/browser, including GPS refusal and API failure behavior, and capture screenshots.
5. Record at least one round of user/team testing and any bug fixes.

No one should claim a test passed until the corresponding GitHub log, data or screenshot proves it.

## New walking and route-history feature checks

The revised HTML preserves **518 embedded places** and adds a Mapbox `walking` profile switch. Its pedestrian route geometry is accepted only when supplied by a valid Mapbox Directions response, and a no-route result produces an error rather than a straight-line fallback. The trained historical Random Forest appears only on driving cards. The separate frequent-destination predictor uses repeated local search history and Houston time-of-day weighting; it is not a trained driving-time model and does not prove that users actually traveled those routes.

**To sign off after deployment:** test a real nearby walking route, test an unreachable pedestrian pair, confirm the AI card is absent in walking mode, repeat the same driving route twice to show a predicted destination, reload to confirm browser-local history, test Delete and Clear, verify JSON export and ensure GPS coordinates are never stored in route history.
