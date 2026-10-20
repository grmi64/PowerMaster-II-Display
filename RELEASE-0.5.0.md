PowerMaster II Display 0.5.0 (build 13)

Display settings now offers Modern, Console and Daylight appearance profiles.
Console uses horizontal graduated color bars inspired by the reference display.
Profiles share the same live readings and connection configuration.

Peak hold: Off, 2/5/10 seconds, or Until reset. Reset peak immediately starts from
the current live sample. Stale data clears peaks and measurements. These are
sample peaks, not true PEP measurements. Existing SWR thresholds remain editable.

Independent forward/reflected scales support Auto and fixed 5–10,000 W ranges.
Auto expands immediately with headroom and waits five seconds before shrinking.
Scale clipping never changes numeric readings or telemetry values.

Compact resizes the existing native window; Expand restores the previous full
frame. Stay on top uses the macOS floating window level. Preferences persist
locally. Neither mode opens another USB reader or creates radio/CAT traffic.

Validation: display-model tests cover timed/latched/off peak, reset, stale data,
no-RF SWR, fixed scales and Auto hysteresis. Twelve Python regressions passed
(one skipped), including telemetry opt-in and single-reader protection. Native
Compact/Expand, Console selection and On top verified; exactly one process owned
the meter port afterward. Ten final telemetry samples were LIVE (max 9.3 ms).
Local app launched in compact Console mode with On top enabled. Prior 0.4.7 app
and source preserved in release/before-0.5.0. Applications and published DMGs are
unchanged; this local build is not a newly notarized release.
