# PowerMaster II Display 0.5.1 / build 14

October 20, 2026: custom graphite/navy instrument icon with a horizontal electric-blue power bar and blue RF waveform underneath. Matches KPA1500 Control's casing style while using a different meter silhouette and accent palette. Initial two-bar artwork retained under release/before-waveform-icon.

Assets includes the transparent master PNG, macOS ICNS and seven-size Windows ICO. Build sets CFBundleIconFile and copies the ICNS. Icon container entries, embedded resource equality, version and local ad-hoc signature verified. 64px artwork visually checked. Current local 0.5.0 display/profile work is preserved.

Local preview: release/icon-preview-0.5.1/PowerMaster II Display.app. Built in an isolated staging directory so the running meter app and USB reader were not replaced or restarted. No serial or CAT code changed for this icon update. The initial preview preceded the authorized signed installation below. Beta downloads remain unchanged.

## Notarized Applications installation

User explicitly authorized upload to Apple and replacement in Applications. Developer ID signed app accepted by Apple: 810670e2-20c1-4b5a-b11f-0dfadd112e68. Ticket stapled and validated; signature and Gatekeeper passed. Version 0.5.1 and AppIcon.icns verified in Applications after Finder replacement. Previous installed 0.4.6 retained under release/before-applications-0.5.1.

Regression checks: 12 Python tests (11 passed, one skipped) and display-model JavaScript checks passed. Launched /Applications/PowerMaster II Display.app and observed LIVE in Compact view. OS inspection confirmed one app/service/worker tree and exactly one USB reader owning the meter port. Existing settings retained; KPA1500 and radio CAT were not restarted. The local installation preceded the separate beta release below.

## Standalone signed beta DMG

Released October 20, 2026 from clean commit 213eaf1 on feature/dxcaliber-telemetry. Includes the blue power-bar/waveform icon and existing appearance profiles, peak hold/reset, adjustable scales, compact/stay-on-top and meter-feed fixes.

Clean app notarization: f7ab5dd1-3757-43d9-aeba-cb2c07644746. DMG notarization: 13a886b6-8ce1-4059-abab-21589f75f67e. Developer ID signed; Apple accepted both. Tickets stapled and validated, app/DMG signatures and Gatekeeper passed. Mounted installer version, icon equality and Applications shortcut verified.

Filename: PowerMaster-II-Display-0.5.1-arm64.dmg

Size: 7,017,981 bytes

SHA-256: 5d2e3101c6cfb536aee0bc69671126ecaf352aa045e2d43ec550495f231738fd

Private R2 and approved-tester Safari downloads matched the final notarized original. Downloaded DMG ticket/Gatekeeper checks passed. All 48 beta service tests passed; anonymous GET, HEAD, Range and forged-token requests blocked. Published at https://dxcaliber.com/beta/download-meter . Deployment: a31e5cb2-3067-4d51-a707-90b21ca4d249.

KPA1500 release and combined installer are unchanged. Combined DX Caliber installer still bundles meter 0.4.4; the website records its meter version separately from the newer standalone release. Prior meter DMG retained in private storage for rollback. Running station applications were not restarted for packaging.
