# PowerMaster II Display 0.5.1 / build 14 — local icon preview

October 20, 2026: custom graphite/navy instrument icon with a horizontal electric-blue power bar and blue RF waveform underneath. Matches KPA1500 Control's casing style while using a different meter silhouette and accent palette. Initial two-bar artwork retained under release/before-waveform-icon.

Assets includes the transparent master PNG, macOS ICNS and seven-size Windows ICO. Build sets CFBundleIconFile and copies the ICNS. Icon container entries, embedded resource equality, version and local ad-hoc signature verified. 64px artwork visually checked. Current local 0.5.0 display/profile work is preserved.

Local preview: release/icon-preview-0.5.1/PowerMaster II Display.app. Built in an isolated staging directory so the running meter app and USB reader were not replaced or restarted. No serial or CAT code changed for this icon update. The initial preview preceded the authorized signed installation below. Beta downloads remain unchanged.

## Notarized Applications installation

User explicitly authorized upload to Apple and replacement in Applications. Developer ID signed app accepted by Apple: 810670e2-20c1-4b5a-b11f-0dfadd112e68. Ticket stapled and validated; signature and Gatekeeper passed. Version 0.5.1 and AppIcon.icns verified in Applications after Finder replacement. Previous installed 0.4.6 retained under release/before-applications-0.5.1.

Regression checks: 12 Python tests (11 passed, one skipped) and display-model JavaScript checks passed. Launched /Applications/PowerMaster II Display.app and observed LIVE in Compact view. OS inspection confirmed one app/service/worker tree and exactly one USB reader owning the meter port. Existing settings retained; KPA1500 and radio CAT were not restarted. No new beta DMG publication requested.
