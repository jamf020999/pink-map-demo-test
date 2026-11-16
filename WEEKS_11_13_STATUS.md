# PinkMap — Weeks 11–13 completion status (release candidate)

**Basis:** source archive `PinkMap-main (4).zip` and changes prepared in this release. **An updated ZIP is not the same as a GitHub commit or a successful external deployment.**

| Week | Objective | Status after release preparation | Evidence / remaining action |
|---|---|---|---|
| 11 | User interface | Implemented in code | Searchable 518 places, Mapbox routing/cards, responsive layout; recheck deployed site |
| 11 | API development if needed | Existing external API integrated | Mapbox Directions/Geocoding; **no custom API required** for static demo |
| 11 | Backend system setup | Implemented for data collection | GitHub Actions collector configured; no persistent prediction backend, browser-side ML instead |
| 11 | Database | **Deferred at user's request** | CSV historical data + browser localStorage; not a shared production database |
| 11 | Component development | Implemented in code | UI, 50-route collector, data pipeline, trained model, browser predictor; recheck deployed site |
| 12 | Integrate components | Implemented for demo in code | Model is consumed by the HTML UI; separate collector saves CSV; live deploy unverified |
| 12 | Unit testing | Implemented, local checks passed | `tests/test_collector.py`, `tests/test_model.py` and JS predictor tests |
| 12 | Integration/system testing | Mock browser test passed locally | Browser test with **mocked** Mapbox and production model; **live** Mapbox/test of all routes still required |
| 12 | Performance optimization | Partially addressed | Static ~94KB model, no prediction server call; timed real-world profiling still required |
| 12 | Bug fixing | Several preventative fixes implemented | Corrected schedule, retry/error/partial-batch protection, coherent timestamps, run-based splits; manual regression required |
| 12 | User testing if applicable | Not performed by assistant | Team to run 2–3 users through demo and document feedback |
| 13 | Deployment environment | Existing GitHub Pages site; updated code prepared | Upload new release, verify two model JS assets deployed and Pages success |
| 13 | Documentation | Implemented in release | README, DEPLOYMENT, TESTING, DEMO_GUIDE, current status file |
| 13 | Prepare demonstration | Guide prepared | Team must rehearse and capture actual demo screenshots |
| 13 | Complete testing | Partial | Local tests passed; GitHub CI, live Mapbox, GPS, schedule and classroom computer tests outstanding |
| 13 | Package deliverables | Prepared | ZIP includes source, preserved CSV, notebooks, model, tests, workflows and docs |
| 11–13 | Class activities | Cannot validate from code | Team notes for development sessions, consultations, progress, troubleshooting and collaboration |

## Important validation limits

- `collect.py` and Notebook 1 define exactly 50 fixed routes, but `data/auto_collected.csv` in the provided archive has **2,595 observations from routes 1–15** only. That old file was preserved as-is.
- `7 */2 * * *` requests collections **every two hours UTC**, not necessarily precisely on time. Successful actual runs still require the team's GitHub environment and Mapbox token.
- The deployed AI module is a **historical experimental model**, not the source of real-time route suggestions. Test MAE **52.00 sec** versus no-delay baseline **65.65 sec**, on historical held-out runs from the original 15 routes. There is no validation for new route IDs or arbitrary location pairs.
- The **database is deliberately deferred** and remains not implemented as a shared server database.

## New pedestrian/personalization additions (local-release status)

- **Week 11:** Travel-mode UI, Mapbox pedestrian API, local-only saved route history, and usage-pattern destination predictions are implemented without a database.
- **Week 12:** New JS unit tests and mocked browser tests exercise the walking profile, keeping the AI predictions off pedestrian cards, saved route history, replay and frequency-based suggestions. Actual live pedestrian suitability, accessibility and GPS/device reliability still require manual checks.
- **Week 13:** README, deployment, testing, release notes and demo guide were extended. New release must be pushed to GitHub Pages and validated there before making completed-deployment claims.
- **Scope distinction:** GitHub Actions collects 50 fixed **driving** routes every two hours; the walking tab requests paths interactively and is not part of the automated driving dataset. User search frequency is local browser state, not synchronized or a feature of the shared traffic model.
