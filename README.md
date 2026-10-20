# PowerMaster II Display

Independent macOS station meter app. Bundle identifier: `com.grmi64.PowerMasterIIDisplay`.

## Local prototype 0.1.0 — build 2

Native macOS window containing the LED display, with a local Python USB reader.
Quit the earlier Terminal reader before launching the app. Quit this app with Command-Q or close its window; the child reader exits with it. Reopening the app activates the existing window. A process lock also prevents concurrent instances from opening the meter.

**This build requires `/usr/bin/python3` and Apple Command Line Tools on the Mac. It is not yet a self-contained release for testers.** It has an ad-hoc signature, not Developer ID signing or notarization. No installer or DX Caliber integration is included yet.

## Build

Run `bash scripts/build.sh` on macOS with Swift Command Line Tools. Output: `dist/PowerMaster II Display.app`. The build targets the compiling Mac's architecture. `Contents/MacOS/PowerMasterIIDisplay --demo` runs with simulated measurements.

## Connection

Default USB port: `/dev/cu.usbserial-A400gmxx`, 38400 8N1. Automatic reconnect and stale-data blanking. The browser reader also accepts `--port` for other serial paths; a native connection-settings screen remains to be added. Local HTTP binds only to 127.0.0.1, port 51879 in the native app, with a random URL token per run.

Verified stream command: `02 44 33 03 31 33 0D`. CRC inferred from captured hardware frames: MSB-first polynomial B1, init 00, xor FF, payload only. Extra status fields and stop-stream command remain unverified. Peak hold is sampled maximum, not true PEP.

## GitHub preparation

Source is organized separately from the DX Caliber application and website. No remote or publishing has been configured. Recommended next step: a separate private repository. Select a license before public distribution.

## Release work remaining

Bundle a supported Python runtime or implement the reader natively; add port settings; test clean Macs; build Apple Silicon/Intel artifacts; Developer ID sign and notarize; add optional DX Caliber launch/data integration.

## First working baseline

Tag: `v0.1.0-baseline`. Hardware verification on October 19, 2026: user confirmed native app remains connected and resumes live measurements after USB unplug/replug. Forward/reflected watts and SWR were compared with the meter front panel earlier in this session.

Build 2 corrects handling of empty nonblocking serial reads and sets VMIN to 1. Parser/CRC checks and a simulated alternating-empty-read regression check passed. Native single-instance activation and clean-Mac distribution remain unverified.
