# Screenshot evidence and demo

All images below are unedited captures of the actual running React application, not mockups. Current captures were made on 2026-09-15 at desktop 1440×1000 and mobile 390×844. Existing earlier captures are retained but are not the evidence set linked here.

| Image | Content and provenance |
| --- | --- |
| [AAPL overview](screenshots/aapl-dashboard.png) | Current successful AAPL run, fetched 2026-09-15 04:48:44 UTC |
| [AAPL risk](screenshots/aapl-risk.png) | Actual risk and distribution sections |
| [AAPL forecast](screenshots/aapl-forecast.png) | Validation-selected naive and lower Ridge holdout error shown together |
| [AAPL recommendation](screenshots/aapl-recommendation.png) | Deterministic action, vote evidence and optional AI status |
| [Reliance overview](screenshots/reliance-dashboard.png) | Earlier successful snapshot fetched 2026-09-14 18:48:08 UTC; NOT a successful current refresh |
| [Data quality](screenshots/data-quality.png) | Earlier Reliance snapshot with expanded trailing-placeholder/benchmark warnings |
| [Mobile](screenshots/mobile-dashboard.png) | Earlier Reliance snapshot at 390-pixel width |

AAPL snapshot ID: `04a8d99e-3d14-4a1b-9296-3b3b294aead0`.

Reliance snapshot ID: `dcd63e78-cf0f-4e68-81da-4820e993638b`.

The final live Reliance request returned 422: the missing 2026-09-14 row became interior after a valid 2026-09-15 row appeared. Saved results preserve their original provenance. Do not describe the Reliance screenshots as evidence of a successful latest request.

## Reproduce captures locally

Start both servers as described in the [README](../README.md), install frontend dependencies (including agent-browser), and ensure a Playwright-compatible browser is installed. Create valid saved runs and use their returned IDs. On the verified machine, the above IDs are in local SQLite; a fresh clone will not contain that ignored runtime database.

```powershell
.\scripts\capture_screenshots.ps1 -AaplId '04a8d99e-3d14-4a1b-9296-3b3b294aead0' -RelianceId 'dcd63e78-cf0f-4e68-81da-4820e993638b'
```

The script loads actual saved analyses, scrolls each relevant section and copies viewport screenshots to the documented filenames. It overwrites those seven images; use new IDs only when their source and dates are also updated in the evidence. Browser startup may require network access/browser installation. Inspect captures visually after running.

## Suggested demonstration

Open the AAPL overview, explain raw versus adjusted prices, then inspect risk and forecast evidence. Point out why naive remains selected despite Ridge's later lower error. Inspect the recommendation factors and separate AI message. Open the saved Reliance analysis to show the explicit data-quality warning, explain the current rejected refresh, and finish at mobile width. If live Yahoo data is unavailable, label saved-run playback explicitly.
