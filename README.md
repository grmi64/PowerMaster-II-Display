# PowerMaster II Display

Standalone macOS display for the Array Solutions PowerMaster II meter, created by NY6C. DX Caliber is optional.

Source: https://github.com/grmi64/PowerMaster-II-Display

License: MIT. Python and PyInstaller retain their respective licenses.

## Download and install

The public release is 0.5.3 (build 16), for Apple Silicon Macs running macOS 12 or later. It includes its own Python 3.12 runtime; Python and developer tools are not needed to use the app.

Quit an older copy, open the DMG, and drag PowerMaster II Display to Applications. Connect the PowerMaster II by USB, choose its serial port and baud rate in Meter connection, and select Connect / Apply. Common baud rate: 38400; supported choices are 9600, 19200 and 38400. Close other software that is using the same meter USB port. A serial adapter may require its manufacturer's driver.

## Features

- Forward/reflected watts and SWR, stale-data blanking and paced reconnection.
- Modern, Console and Daylight display profiles.
- Adjustable scales, sampled peak hold/reset and SWR color thresholds.
- Compact view, Stay on top, optional callsign badge and window recovery.
- About menu with release version and NY6C attribution.
- Optional read-only sharing with DX Caliber on the same Mac, off by default. Only this app opens the meter USB port.

Peak hold is the maximum of received samples, not true PEP. Meter scales and warning colors are visual aids. This is an independent application and is not an official Array Solutions product.

## Build and test

Use an Apple Silicon Mac with Xcode Command Line Tools and a Python 3.12 virtual environment containing PyInstaller 6.22.3. Set `PM_BUILD_PYTHON` to its Python executable and run `bash scripts/build.sh`. Output: `dist/PowerMaster II Display.app`. The default local build is ad-hoc signed. Developer ID signing and Apple notarization require the publisher's own credentials.

Run `python -m unittest discover -s tests -v` and `node tests/test_display.cjs`. One serial-exclusivity test can skip when the macOS pseudo-terminal driver does not enforce the real USB driver's exclusivity behavior. Actual meter operation was verified during development; the refreshed runtime package has been verified in simulation but has not yet been retested on the live USB meter.

For isolated simulation, run the bundled meter-reader executable with `--demo --http-port 0 --settings /tmp/powermaster-demo.json`. This does not open a USB port. Do not launch a second native app instance to test alongside a running meter; single-instance protection activates the existing copy.

## Privacy and support

Meter readings stay local. Optional DX Caliber sharing uses a read-only loopback endpoint. No station preferences, captures, credentials or personal logs are included in the release. Report issues with the app version, Mac/macOS version and meter/adapter details; remove private information from diagnostics before sharing.

Python licensing is in ThirdParty/Python-LICENSE.txt. PyInstaller's bootloader redistribution license is in ThirdParty/PyInstaller-COPYING.txt.
