# PinkMap classroom demo — Week 13

## Presentation goal

Show a navigable Houston map, live driving and walking Mapbox comparisons, route-history personalization, the automatic 50-route historical collection pipeline, and an **experimental historical ML traffic-delay prediction**. Explain what has been implemented, tested, and deferred.

## Live walkthrough (suggested order)

1. **Opening — UI / map:** Open https://phunguyenm.github.io/PinkMap/PinkMap_App.html. Point out the searchable **518 built-in places** and the From/To boxes.
2. **Live driving route search:** Choose **Houston City College → Rice University**, select **Driving**, and click **Show routes**. Explain the highlighted path and alternate choices.
3. **Mapbox vs. typical time:** Read the actual Mapbox current duration, usual duration and signed difference. Positive seconds mean slower than typical; negative seconds mean faster than typical. These numbers are Mapbox **estimates**, not measured driving times.
4. **AI component:** Point to the **AI predicted travel time (experimental)** line, and explain it comes from a trained Random Forest using historic trip length, normal duration and Houston time. It is **not** the current-traffic Mapbox figure. The existing test accuracy covers the old 15 historical routes only; the 35 new monitored routes have not yet been validated.
5. **Pedestrian routing:** Switch to **Walking** and search between nearby locations (e.g., Rice University → Hermann Park). Show the pedestrian-only path, estimated walking duration, and any returned turn-by-turn instructions. Note that the driving-trained model is intentionally hidden.
6. **Saved route history and frequent-route predictions:** Repeat one exact origin→destination search **twice in Driving mode**. Show the on-device **Predicted destination** suggestion, then **Recent routes** with the **Repeat** button. Demonstrate deleting an entry or clearing/exporting history. Explain that this is a usage-frequency statistical recommendation, *separate* from the historical driving Random Forest.
7. **Data collection:** Open `collect.py` on GitHub and show route IDs **1–50**. Show `collect.yml` with `7 */2 * * *` (**every two hours, UTC, best effort**). Open a **successful recent Actions run** and the last 50 CSV rows, if and only if those are present after deployment.
8. **Model evaluation:** Open `model/metrics.json` or the training notebook. Historical dataset: **2,595 samples**, **173 runs**, **15 routes**. Train/validation/test: **1815/255/525 rows** (121/17/35 runs). Test MAE: baseline **65.65 sec**, selected model **52.00 sec**. Explain that lower error does not imply shorter trips.
9. **Testing and deployment:** Open the **PinkMap checks** GitHub Actions results. Explain unit, data, prediction parity and mocked-browser tests, then briefly mention real-world/manual testing. Show GitHub Pages deployment status.
10. **Limitations / future:** State clearly that the project currently has no shared database (deferred), real-world route coverage is limited, and actual GPS driving times were not recorded. Describe how the group plans to collect data for routes 16–50, retrain, validate, and later add persistence if needed.

## Backup if the internet or token fails during class

- Prepare screenshots of the successful live route cards, AI estimate, the Actions collector results, the 50-route list, and `model/metrics.json` **after** the new release has been deployed.
- Keep the downloaded ZIP on the classroom computer. Local HTML can load the model from its `model/` directory, but live Mapbox routing still requires the network and a working token.
- Display previously generated result screenshots only as **previous recorded examples**, never imply that an offline screenshot is a current traffic reading.

## Evidence the team should capture before building slides

- A current repository commit containing all **50 route definitions**, both collectors, and the corrected two-hour cron.
- A real GitHub Actions log showing **“Saved 50 complete observations”** and a CSV screenshot containing route IDs 16–50.
- Green automated test workflow result + manual live UI screenshots.
- `model/metrics.json` values and the note that the experimental model is trained only on the original 15 historical routes.
- README/DEPLOYMENT/TESTING documents and the final release ZIP.
- Team development/troubleshooting notes and user feedback (if required).

## Important distinction for reviewers

The 50 fixed monitored routes are **driving traffic collection routes**, not the total number of pedestrian routes. Walking routes are requested live for the selected origin/destination and accepted only when Mapbox returns usable geometry. The repeated-use suggestion estimates **likely destination selection from search frequency and Houston time of day**; it is not a claim that the Random Forest model has learned from private user history. Custom saved addresses and route history remain in the viewer's browser unless deliberately exported.
