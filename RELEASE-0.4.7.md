PowerMaster II Display 0.4.7 (build 12)

Normal app shutdown marks termination intentional before stopping the reader,
removes its termination callback, and ignores already queued failure alerts.
Unexpected reader exits still report an error. The single-reader USB guard,
recovery limits, and radio/CAT separation are unchanged.

Validation: 12 Python tests passed (one skip); Swift app compiled. Native Quit
closed the app and reader with no error dialog or leftover processes. Relaunched
local dist build for testing; Applications and published installers unchanged.
