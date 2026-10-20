# PowerMaster II Display

Independent macOS station meter app. Bundle identifier: `com.grmi64.PowerMasterIIDisplay`.

## Local prototype 0.3.0 — build 4

Native macOS window containing the LED display, with a local Python USB reader.
Quit the earlier Terminal reader before launching the app. Quit this app with Command-Q or close its window; the child reader exits with it. Reopening the app activates the existing window. A process lock also prevents concurrent instances from opening the meter.

**Build 4 bundles its Python reader and runtime; users do not need Python or Command Line Tools. Clean-Mac verification is still pending.** It has an ad-hoc signature, not Developer ID signing or notarization. No installer or DX Caliber integration is included yet.

## Build

Install PyInstaller 6.22.3 in a Python build environment, then set `PM_BUILD_PYTHON` to that environment's Python and run `bash scripts/build.sh` on macOS with Swift Command Line Tools. Output: `dist/PowerMaster II Display.app`. The build targets the compiling Mac's architecture. `Contents/MacOS/PowerMasterIIDisplay --demo` runs with simulated measurements.

## Connection

Use Meter connection to select a USB serial port and 9600, 19200, or 38400 baud. Refresh rescans ports; Connect / Apply saves settings and restarts the reader. Disconnect releases the port. Saved settings are restored on launch; on first launch a sole detected port is selected automatically. Automatic reconnect and stale-data blanking. The browser reader also accepts `--port` for other serial paths; the same connection controls are available in the native window. Local HTTP binds only to 127.0.0.1, port 51879 in the native app, with a random URL token per run.

Verified stream command: `02 44 33 03 31 33 0D`. CRC inferred from captured hardware frames: MSB-first polynomial B1, init 00, xor FF, payload only. Extra status fields and stop-stream command remain unverified. Peak hold is sampled maximum, not true PEP.

## GitHub preparation

Source is organized separately from the DX Caliber application and website. No remote or publishing has been configured. Recommended next step: a separate private repository. Select a license before public distribution.

## Release work remaining

Test clean Macs; migrate the bundled Python 3.9.6 runtime to a supported Python release before broad distribution; build Apple Silicon/Intel artifacts; Developer ID sign and notarize; add optional DX Caliber launch/data integration.

## First working baseline

Tag: `v0.1.0-baseline`. Hardware verification on October 19, 2026: user confirmed native app remains connected and resumes live measurements after USB unplug/replug. Forward/reflected watts and SWR were compared with the meter front panel earlier in this session.

Build 2 corrects handling of empty nonblocking serial reads and sets VMIN to 1. Parser/CRC checks and a simulated alternating-empty-read regression check passed. Native single-instance activation and clean-Mac distribution remain unverified.

Build 3 validation: simulated connection control, persistence across restart, invalid baud and unauthorized control requests, parser/CRC checks passed. GUI layout inspected in demo mode. Hardware connection controls and native second-launch activation still require operator verification.

Operator verified build 3 on October 19, 2026: selected port and connected, quit/relaunched with settings restored and rapid reconnect, second launch brought existing window forward without another instance.

Build 4: frozen reader and Python runtime bundled with PyInstaller. Demo page/data/shutdown verified with PATH excluding Python. Ad-hoc signature verified. Developer ID signing attempt failed to obtain Apple trusted timestamp; notarization was not submitted. Distribution remains pending.
