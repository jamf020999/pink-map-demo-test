# PinkMap testing and acceptance plan — Week 12

## Automated checks (implemented)

Local environment: Python 3.12 (or compatible), Node 22 and Chromium/Playwright for the browser test.

```bash
python -m pip install -r requirements-model.txt 'playwright>=1.40'
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_web_model.js
node tests/test_web_history.js
python -m playwright install chromium
python tests/browser_smoke.py
```

The `.github/workflows/tests.yml` workflow runs these checks on pushes and pull requests. The scheduled collection workflow runs the collector's standalone route validation and collector unit tests before calling Mapbox. The browser smoke test **mocks Mapbox** so it is deterministic and consumes no Mapbox API quota.

| Test area | Evidence exercised |
|---|---|
| Collector route validation | Exactly 50 unique numbered route IDs; valid Houston-area coordinates; no duplicate OD pairs |
| Collector ↔ Notebook 1 | The same 50 route definitions and coordinates in both collectors |
| API parser/retry | Valid synthetic Mapbox response parsed; invalid response retries once and reports failure |
| CSV integrity | A complete simulated batch appends 50 rows without deleting historical data; a failed batch appends zero |
| ML data cleaning | Empty/invalid samples removed; all three partitions are strictly separated by complete collection runs |
| ML feature leakage | Current traffic time, calculated delay, speed and route ID excluded from predictive feature inputs |
| ML model export | Python tree predictions and JavaScript tree predictions agree on saved reference inputs |
| Houston time zone | Browser AI uses `America/Chicago` rather than viewer's local machine time |
| Local route history | Valid entry storage, duplicate searches, time-aware ranking, driving/walking separation, delete and update, corrupt storage recovery, GPS coordinate redaction |
| Mocked web browser integration | 518 built-in places; driving and pedestrian Mapbox profiles; AI on driving only; history persistence; frequent-route prediction; saved-route replay; no JavaScript exceptions |
| HTML/JS syntax | Node JavaScript parser validates the static model, predictor, route-history module and inline application script |

**Limitation:** These tests do not prove any actual Mapbox route is driveable today, that GitHub Pages serves every file correctly, or that the team has run successful collection after adding route IDs 16–50.

## Manual system acceptance tests (complete after GitHub upload)

Use the actual **deployed URL**, preferably on the presentation computer. Record date, tester, result, screenshot link and issues for each row.

| ID | Test to run | Expected outcome | Evidence to collect |
|---|---|---|---|
| S01 | Open the live GitHub Pages URL | Map tiles, sidebar and searchable fields load | Screenshot of page and URL |
| S02 | Choose HCC → Rice University and click Show routes | One or more routes with distance and live time | Route card and map screenshot |
| S03 | Select a second route alternative (if available) | Highlight moves to chosen alternative | Before/after screenshots |
| S04 | Compare “Usually” to current travel time | Signed difference and faster/slower labels are consistent | Screenshot + manual arithmetic |
| S05 | Check experimental AI estimate in route card | Separate AI-predicted time displayed with limitations | Screenshot, `model/` fetch result |
| S06 | Select same starting and ending place | Clear message; no invalid API request | Screenshot |
| S07 | Deny GPS permission, then choose manual From/To | Interface remains usable | Screenshot |
| S08 | Use custom address search and save an address | Browser-local saved address appears; delete works | Screenshot |
| S09 | Simulate loss of internet or invalid Mapbox request | Error shown; page does not crash | Console + screenshot |
| S10 | On desktop and narrow/mobile viewport | Controls are usable, cards readable and no overlap | Screenshots |
| S11 | Run GitHub Actions “Collect traffic data” manually | Successful run saves 50 observations, all IDs 1–50 | Actions log/CSV screenshot |
| S12 | Wait for later scheduled collection | A second completed run appears about two hours after an earlier scheduled run (allow delays) | GitHub Actions timestamps |
| S13 | Open Actions “PinkMap checks” workflow | Unit, model, JS and mocked browser checks are green | Workflow screenshot |
| S14 | Run `python scripts/check_collection.py` on a fresh clone | Reports latest complete 50-route batch and historical counts | Command output screenshot |
| S15 | Test on instructor/classroom browser | Website, token, network and permissions work | Date/device/summary |

**Do not mark S11 or S12 as passed until actual GitHub Actions output confirms it.** Source code and screenshots of a different route do not establish those tests passed.

## Performance and user testing

- Measure how long opening the site and requesting two routes takes on a normal connection. Mapbox response time and device network may dominate; report observed results, not guessed latency.
- Try rapidly searching within the **518 built-in locations**; the dropdown limits textual matches to 50 at a time. Confirm no freezing or excessive scrolling.
- The static model requires **no server inference round-trip** and its JavaScript weights are ~94 KB in the current release. This minimizes added prediction latency; not a guarantee of end-to-end performance.
- Ask 2–3 teammates/classmates to attempt a route without instructions. Record whether they understand the difference between the live Mapbox estimate and the experimental AI estimate, and whether GPS permission or search was confusing.
- Record discovered bugs, fixes, GitHub commit references and a **retest** for each fix. Examples: missing `model/` folder, API error, location ambiguity or incorrect delay labels.

## Test log template (team to fill)

| Date | Tester | Test ID | Pass/Fail | Problem or observation | Fix/commit | Retested? |
|---|---|---|---|---|---|---|
| TBD | TBD | S01 | Not run | — | — | — |
| TBD | TBD | S11 | Not run | — | — | — |

**Class-activity evidence:** Keep short notes from development meetings, technical consultations, troubleshooting sessions, team problem-solving and progress updates. The project artifacts support these activities but cannot certify that they happened.

## Additional Week 12 tests for new features

| ID | Scenario | Expected result |
|---|---|---|
| S16 | Choose Walking, start/destination within a short distance | Request uses `mapbox/walking`; map shows Mapbox-returned pedestrian path with ETA and optional walking instructions; no driving AI prediction |
| S17 | Try a walking route for which Mapbox has no path | Error message and **no** invented straight-line connection or false walking ETA |
| S18 | Search the same route twice in Driving mode | A destination suggestion appears and shows repeat search count; clicking it calculates the route |
| S19 | Change to Walking after using Driving | Old route cards clear; walking suggestions only consider walking searches |
| S20 | Repeat a route from Recent routes | Reuses origin/destination and travel mode; reruns current routing (not cached traffic) |
| S21 | Delete history entry; then Clear history | Entry disappears; suggestions adapt; local storage becomes empty |
| S22 | Export route history | Local JSON download with searched places, travel mode and time; inspect before sharing |
| S23 | Search using My current location | History does not retain raw GPS coordinates; repeating asks current location again |
| S24 | Refresh the page using same browser profile | Recent routes persist, except in restricted/incognito browser sessions |

**Never claim these live tests have passed solely because mocked tests are green.** Do not claim walking routes are certified accessible or safe. Future improvement: optional consent-based backend sync and formal usability study.
