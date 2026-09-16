# Vercel deployment

Production: **https://finquant-ai.vercel.app**

Verified on **2026-09-16**. Project `finquant-ai` belongs to `krivedi1402-7983s-projects` on the existing Hobby plan. This is the existing application; quantitative formulas, model evaluation, selection and recommendation logic were not redesigned. The old reference project was not modified.

## Configuration

The repository-root [vercel.json](../vercel.json) defines two Vercel Services on one domain:

| Service | Root | Framework / entrypoint | Build |
| --- | --- | --- | --- |
| web | frontend | Vite, React 19, TypeScript | `npm ci --ignore-scripts`; `npm run build`; output `dist` |
| api | backend | FastAPI, **app.main:app** | Python **3.14** from backend/.python-version; locked runtime requirements from backend/requirements.txt |

The API entrypoint resolves to `backend/app/main.py` with `backend` as the service root, so the existing `app.*` imports work. The previous repository-root `backend.app.main:app` setting was removed from pyproject.toml; it did not establish that import root. No wrapper or application rewrite is required.

The Python function has a configured **180-second maximum duration** and excludes backend tests from its bundle. Vercel optimized the scientific-Python bundle during the build. The frontend is served as static assets.

Top-level rewrites send `/api/...`, `/docs/...`, `/redoc` and `/openapi.json` to FastAPI, preserving the original path. `/` explicitly selects the web service's `/index.html`; other paths reach the web service for asset delivery. The explicit index destination is required by the observed Services routing behavior. Frontend fetch calls already use relative `/api/...` URLs and remain unchanged. The local Vite proxy's localhost URL is development-only and is not used by the production browser. Browser resource inspection found zero localhost requests.

Reference: [Vercel Services configuration](https://vercel.com/docs/services/config-reference), [service routing](https://vercel.com/docs/services/routing), [Python runtime](https://vercel.com/docs/functions/runtimes/python).

## Environment variables

No manually supplied variable is required for the deployed quantitative application. Production currently has no Gemini secret configured. Vercel provides `VERCEL=1`, which the settings model recognizes automatically.

| Variable | Purpose | What to do |
| --- | --- | --- |
| GEMINI_API_KEY | Optional server-side Gemini authentication | Add a real key in Vercel Project Settings → Environment Variables → Production to enable AI; redeploy afterward |
| GEMINI_MODEL | Optional model override | Leave unset to use gemini-2.5-flash, or configure a model available to your account |
| FINQUANT_CORS_ORIGINS | Optional comma-separated cross-origin allowlist | Unneeded for this same-origin deployment; use only if a separate frontend must call the API |
| FINQUANT_DATA_DIR | Local runtime data directory | Honored locally; overridden to temporary storage on Vercel |
| FINQUANT_PERSISTENCE_ENABLED | Enable/disable local SQLite saving | Defaults true locally; always forced false on Vercel |

Never prefix the Gemini key with `VITE_` or commit it. `.env`, `.env.local` and `.vercel` are ignored. Vercel CLI's locally generated OIDC file was not committed or uploaded. Configure secrets through Vercel's dashboard or interactive `vercel env add`, then redeploy. No live authenticated Gemini output is claimed.

## Filesystem and persistence

Yahoo's cookie/timezone cache writes under the operating system's temporary directory (`/tmp/finquant-ai` on the hosted runtime). The deployment filesystem is not used for writes. These caches and the in-process history cache are disposable and may vanish between instances or deployments.

Hosted SQLite snapshot creation and retrieval are deliberately disabled. `/api/analyze` still returns the complete quantitative response and an explicit warning. Its `snapshot_saved` field is false. The frontend keeps the result in memory, allows JSON download, and does not add a misleading saved-analysis query parameter. Reloading loses the displayed result. `/api/analysis/{uuid}` returns a structured **503 persistence_disabled** response. This is a documented feature limitation, not a persistence guarantee based on temporary disk.

Local SQLite behavior is retained. Successful local saves set `snapshot_saved=true`; save failures set it false and preserve the result with a warning. A new serverless API regression test confirms complete calculations and missing-key handling without initializing a disk database.

## Verification

Detailed live results: [vercel_verification.json](results/vercel_verification.json). Full provider responses are kept only in ignored local `data/deployment/`.

| Check | Result |
| --- | --- |
| Backend suite | **63 passed**, two existing dependency deprecation warnings |
| Corrected service-root import tests | **3 passed** after changing the deployment entrypoint |
| Frontend tests | **3 passed** |
| TypeScript / Vite build | Passed locally and on Vercel |
| Ruff / credential scan | Passed |
| `/` | 200 HTML; actual React UI renders |
| `/api/health` | 200 JSON; ai_configured=false, persistence_enabled=false |
| `/api/models`, `/api/methodology`, `/openapi.json`, `/docs` | 200 |
| AAPL | 200; 502 history rows; complete returns/risk/statistics/forecast/recommendation |
| RELIANCE.NS | 200; 501 history rows; complete quantitative result |
| Missing Gemini key with include_ai=true | Both analyses succeed with interpretation.status=unconfigured |
| Invalid ticker, empty input, invalid horizon | 422 with structured error details |
| Hosted snapshot retrieval | Expected 503 persistence_disabled |
| Browser → API → charts | AAPL seven chart surfaces; Reliance six because its benchmark is unavailable |
| Mobile 390×844 | Reliance charts render, no document horizontal overflow or invalid numbers |
| Invalid-input UI | Readable alert, loading cleared, action enabled, prior result retained |

Reliance's stock history now passes validation; the earlier September 15 failure was provider-data dependent. Its NIFTY benchmark still fails quality validation and is omitted with a warning. No financial observations were silently repaired. Current model selections differ from the older documented snapshots because the live histories and chronological windows changed; the selection rules are unchanged.

Real production screenshots: [AAPL desktop](screenshots/vercel-aapl.png), [Reliance mobile](screenshots/vercel-mobile.png).

## Deployment fixes and limitations

The first upload excluded `backend/app/data` because of an unanchored ignore rule. `.vercelignore` now anchors runtime data to `/data/`. Frontend and backend use separate service roots, and the homepage explicitly selects `/index.html`. These deployment failures were corrected before the successful end-to-end checks.

No remaining application startup or production API routing failure was observed after those fixes. The production alias is publicly accessible; unique deployment URLs may retain Vercel authentication protection. Do not disable that protection just to inspect them; authenticated CLI access is available.

Remaining limitations are ephemeral caches, disabled hosted saved runs, cold starts, the function duration and plan quotas, public-provider availability/revisions, and no verified authenticated Gemini call. The four-request semaphore is per instance, not a global abuse-control system. No external monitoring drain was configured. This remains a research prototype with the limitations in the original methodology documents.

Vercel's npm install reported two moderate advisories in the existing **Vitest / @vitest/mocker development test-tool chain**. The suggested fix is a major Vitest upgrade, which was not included in this deployment-only change. Those tools are not the served static frontend or Python API. No high/critical advisory was reported by this npm audit; this is not a comprehensive security audit.

## Redeploy

The Vercel project is linked to the existing GitHub repository. Source updates can deploy through that integration. For an explicit deployment from the repository root:

```powershell
npx --yes vercel@59.19.0 link --yes --project finquant-ai --scope krivedi1402-7983s-projects
npx --yes vercel@59.19.0 deploy --prod --yes --scope krivedi1402-7983s-projects
```

Run the backend tests and frontend production build before deploying. Production build files are generated by Vercel; local databases, downloaded provider data, caches and secrets must remain excluded.
