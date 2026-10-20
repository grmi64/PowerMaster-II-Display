# PowerMaster II Display 0.4.4 / 9

Correct cross-process timestamps: bundled Python 3.9 on macOS has process-local
monotonic origins. After isolating the USB worker, comparing its monotonic event
time with the parent clock caused large false ages (about 142 seconds after a
reconnect), even as sequences advanced. Transport observation times now use the
shared wall clock; in-process retry timers remain monotonic. Restore two-second
UI/feed freshness limits; preserve nonblocking read recovery and process isolation.

Six tests pass, including a different-monotonic-origin regression. Apple accepted
submission 7f8edda5-5b6c-4327-8147-29c968ed46d8; app stapled, validated and Gatekeeper
accepted. Installed in Applications with previous app backed up. Physical feed
check: initial startup stale sample then 24 consecutive LIVE samples over 24 s,
frame sequence 22 -> 125 (~4-5 frames/sec), ages usually below 0.2 s; dashboard
visibly LIVE with 0.1 s age. No transmit was commanded by the agent.

This supersedes the earlier diagnosis attributing all stale indications to USB
interruptions/slow normal cadence. Live RF transmit confirmation remains with the
operator. Existing beta website installers are unchanged (meter 0.4.0).

## Published beta packages

Published combined DX Caliber DEV 0.6.59 + PowerMaster II 0.4.4 and standalone
meter 0.4.4 at https://dxcaliber.com/beta/ (approved tester sign-in required).
Both DMGs signed, notarized, stapled, Gatekeeper verified and uploaded/downloaded
checksums matched. Previous packages retained. Installer SHA-256:
- Combined: cf13500fe933b070151bf7bdd2fb51a9d3ea6238b593d29e44e5c248eb56ce93
- Meter-only: e11a6fa4acd1fe4d32c2f2516317fe3f9ffaeaed09096cab4bce5e43080eb48e
Source fixes are checked into feature/dxcaliber-telemetry. This supersedes the
prior note that beta packages remained at 0.4.0.
