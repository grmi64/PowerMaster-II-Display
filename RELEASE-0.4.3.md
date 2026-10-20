# PowerMaster II Display 0.4.3 / 8

Meter UI and telemetry freshness allow five seconds between frames rather than
two. Retains 0.4.2 nonblocking-read fixes. Five tests pass, covering normal
three-second gaps and blanking six-second-old data. Signed, notarized (Apple ID
50901dfa-fee4-4f3d-9d33-11fa9d73e8fc), stapled, Gatekeeper accepted and locally
installed. Previous 0.4.2 app retained in the DXWatcher outputs backup directory.

Physical verification still found a roughly twelve-second gap with no advancing
frame sequence, then normal updates resumed. This release reduces premature
stale indications but does NOT establish that the underlying intermittent USB
stream has been fixed. Meter USB/device reset and further capture are required.
Do not publish this as a verified fix for all live/stale cycling. Current beta
website packages remain at 0.4.0. DX Caliber's existing feed freshness policy is
unchanged in its installed 0.6.59 app.
