# PowerMaster II Display 0.4.5 / 10

Bounded meter-only automatic recovery: after eight seconds without valid frames
(or a dead worker), show Reconnecting and schedule up to three replacement-worker
attempts, with 2/5/10-second delays. Each new worker gets eight seconds to produce
frames. A worker that does not terminate within a bounded 0.1-second join is not
reopened concurrently; recovery stops with USB-reset guidance. After exhaustion,
manual Connect / Apply resets the budget. Thirty seconds of stable fresh samples
resets it automatically. Fresh zero-power frames do not trigger recovery. Stale
values remain blanked at two seconds, retaining 0.4.4's shared timestamps.

The reader no longer contains an independent unlimited reconnect loop. All meter
USB activity is in its process; DX Caliber radio/CAT code and timing are untouched.
Nine tests pass, including exhaustion, delay pacing, stable reset and hung-worker
handling. Physical RF-induced failure testing remains with the operator. Local
release only; published beta installers remain 0.4.4 until a release is requested.
