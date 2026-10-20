# PowerMaster II Display 0.4.1 / 6

Fixes a blank window when a saved USB port blocks in the macOS serial driver.
The reader now runs in an isolated process with a multiprocessing queue/event;
a blocked serial call cannot hold the display server's Python interpreter lock.
Disconnect waits two seconds, then terminates a stalled worker with a bounded
join. Frozen builds enable multiprocessing freeze support. No radio/CAT changes.

Three telemetry/startup tests pass, including a simulated stalled USB worker.
Frozen demo executable served its interface successfully. Installed signed app
opened its controls with the actual saved USB configuration; device remains
Connecting, so live meter readings are not verified and the USB device may need
reconnecting. Settings/sharing were preserved; prior installed app backed up.

Apple submission 4f3cfba7-20a9-41b6-9554-343079b6e77f accepted. App ticket stapled
and validated; Gatekeeper accepted. Installed in /Applications for local testing.
Published beta DMGs still contain 0.4.0 until a new release is requested.
