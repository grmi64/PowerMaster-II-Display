# PowerMaster II Display

Independent macOS station meter app. Bundle identifier: `com.grmi64.PowerMasterIIDisplay`.

## Version 0.3.0 — build 4

Native macOS window containing the LED display, with a local Python USB reader.
Quit the earlier Terminal reader before launching the app. Quit this app with Command-Q or close its window; the child reader exits with it. Reopening the app activates the existing window. A process lock also prevents concurrent instances from opening the meter.

**The release bundles its Python reader and runtime; users do not need Python or Command Line Tools.** The release copy is Developer ID signed, notarized, and stapled. The operator confirmed clean-Mac testing and live hardware operation of the notarized app. No DMG installer or DX Caliber integration is included yet.

## Build

Install PyInstaller 6.22.3 in a Python build environment, then set `PM_BUILD_PYTHON` to that environment's Python and run `bash scripts/build.sh` on macOS with Swift Command Line Tools. Output: `dist/PowerMaster II Display.app`. The build targets the compiling Mac's architecture. `Contents/MacOS/PowerMasterIIDisplay --demo` runs with simulated measurements.

## Connection

Use Meter connection to select a USB serial port and 9600, 19200, or 38400 baud. Refresh rescans ports; Connect / Apply saves settings and restarts the reader. Disconnect releases the port. Saved settings are restored on launch; on first launch a sole detected port is selected automatically. Automatic reconnect and stale-data blanking. The browser reader also accepts `--port` for other serial paths; the same connection controls are available in the native window. Local HTTP binds only to 127.0.0.1, port 51879 in the native app, with a random URL token per run.

Verified stream command: `02 44 33 03 31 33 0D`. CRC inferred from captured hardware frames: MSB-first polynomial B1, init 00, xor FF, payload only. Extra status fields and stop-stream command remain unverified. Peak hold is sampled maximum, not true PEP.

## Repository

Private repository: https://github.com/grmi64/PowerMaster-II-Display. Source is separate from the DX Caliber application and website. Select a license before public distribution.

## Release work remaining

Migrate the bundled Python 3.9.6 runtime to a supported Python release before broad distribution; broaden compatibility testing and build Intel artifacts; add optional DX Caliber launch/data integration.

## First working baseline

Tag: `v0.1.0-baseline`. Hardware verification on October 19, 2026: user confirmed native app remains connected and resumes live measurements after USB unplug/replug. Forward/reflected watts and SWR were compared with the meter front panel earlier in this session.

Build 2 corrects handling of empty nonblocking serial reads and sets VMIN to 1. Parser/CRC checks and a simulated alternating-empty-read regression check passed. These later passed operator checks as recorded below.

Build 3 validation: simulated connection control, persistence across restart, invalid baud and unauthorized control requests, parser/CRC checks passed. GUI layout inspected in demo mode. Hardware checks subsequently passed as recorded below.

Operator verified build 3 on October 19, 2026: selected port and connected, quit/relaunched with settings restored and rapid reconnect, second launch brought existing window forward without another instance.

Build 4: frozen reader and Python runtime bundled with PyInstaller. Demo page/data/shutdown verified with PATH excluding Python. Operator confirmed clean-Mac operation, then completed signing/notarization in Terminal and verified the notarized app against live hardware. See RELEASE-0.3.0.md.

## Sign and notarize

After building, run `bash scripts/notarize.sh` in a Terminal with access to the configured Developer ID private key and the `DXCaliber-notary` Keychain profile. The script signs a release copy inside out, submits to Apple, requires Accepted status, staples and validates the ticket, and verifies the signature and Gatekeeper assessment. Output: `release/PowerMaster-II-Display-0.3.0-notarized.zip`. Credentials and generated release artifacts are not committed.

## 0.4.0 integration preview

Meter connection includes **Share readings with DX Caliber on this Mac**, off by default and saved with connection settings. DX Caliber must separately enable reception. A versioned read-only loopback feed provides meter readings with original sample age; stale/disconnected values are null. Closing DX Caliber does not stop the meter.

Run `bash scripts/package_station_suite.sh` to sign/notarize the built meter and sibling DX Caliber DEV app, then create both combined and meter-only DMGs. An optional app path overrides the default sibling. `--preview` builds ad-hoc development DMGs without Apple submission. This session's DiskManagement restrictions prevented image creation; use normal Terminal with the existing Developer ID and DXCaliber-notary profile.

Integration demo tests passed; live hardware feed and final combined DMGs need operator verification. The 0.3.0 notarized release and tag remain unchanged.

## Display profiles and compact mode (0.5.0)

Choose **Display settings** for Modern, Console (horizontal color bars), or
Daylight. Set the forward/reflected scales independently to Auto or a fixed watt
range; choose timed peak hold or Until reset. **Reset peak** clears the held peak
back to the current live reading. These display controls do not change the meter.

**Compact** shrinks the same window; **Expand** restores it. **Stay on top** keeps
it visible above other applications. It works in the Mac app. Appearance, scales,
peak options and compact/top choices save automatically. All views use one reader
and the same shared telemetry; DX Caliber/CAT timing is independent.

## PowerMaster II 0.5.1 beta

New instrument icon with blue horizontal power bar and waveform, plus appearance profiles, peak hold/reset, adjustable scales and compact stay-on-top view. Separate signed/notarized meter-only DMG is published in the beta area. The combined DX Caliber installer remains on meter 0.4.4. See RELEASE-0.5.1.md for checksums, notarization and validation.
