# Performance observations

These are local observations, not service-level promises or benchmark comparisons.

The saved-run profile in [results/profile.txt](results/profile.txt) recorded 546,692 calls in approximately **0.354 seconds**. Forecast evaluation accounted for approximately **0.224 seconds** cumulative. The workload includes offline replay assertions and excludes fresh market-data and Gemini network calls. The small difference between profiler total and the replay row (0.355 seconds) is reporting precision. This is one sample, without repeated-run confidence bounds or concurrency testing.

The final AAPL HTTP analysis took approximately **4.990 seconds**, including the provider path and local request work, as recorded in [live verification](results/live_verification.json). It is a different workload and cannot be compared directly with the offline profile to claim a speedup.

Current practical bounds include a 32-entry, 900-second market-history cache, ten-second history request timeout with two attempts, a 20-second optional Gemini request timeout, and four concurrent analysis slots per process. Cached values are copied. Provider history may be cached before downstream quality rejection, so invalid data may remain cached until expiry. These controls are not load-test evidence.

Frontend production output is approximately 234.27 kB JavaScript for the main bundle and 408.83 kB for the chart chunk (gzip 73.18 and 118.39 kB respectively), plus 10.29 kB CSS. The successful build took 13.53 seconds on this machine. Network transfer, hydration and device performance were not benchmarked.

To reproduce the offline profile after creating a local AAPL example:

```powershell
.\.venv\Scripts\python.exe scripts\profile_snapshot.py
```

Before optimizing, collect representative repeated requests, separate provider latency from computation, and measure memory/concurrency. Prioritize validated cache invalidation and broader forecast evaluation over unsupported throughput claims.
