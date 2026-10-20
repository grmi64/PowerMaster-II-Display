# PowerMaster II Display 0.3.0

Build 4; Apple Silicon macOS app. Git tag: `0.3.0`.

## Included

- Native standalone window, single-instance activation, LED power/SWR display, sampled peak hold.
- Saved serial port and baud rate; Connect/Disconnect, automatic USB recovery, stale-reading blanking.
- Bundled Python reader/runtime; no separate Python installation required.

## Verification — October 19, 2026

Automated: captured-frame parser/CRC checks, simulated empty-read recovery, connection control and persistence checks, invalid baud and unauthorized request rejection, frozen reader running without Python on PATH, signature verification.

Operator confirmed: accurate live power/SWR against meter, sustained connection, USB unplug/replug recovery, saved settings after relaunch, existing window activated on repeated launch, clean-Mac test, and live transmit readings from the final notarized app.

Apple notarization submission `c33eabd7-7e6e-492b-9a76-593be76dba11` returned **Accepted**. Operator supplied successful staple/validate output and Gatekeeper assessment: `accepted`, `source=Notarized Developer ID`. Acceptance is also recorded in the local submission result.

## Limitations

Python 3.9.6 runtime should be upgraded before broad distribution. Intel compatibility is not verified. True PEP, extra meter status fields, stop-stream command, DX Caliber integration, and combined/meter-only DMG packaging remain future work. CRC parameters are inferred from hardware captures rather than manufacturer documentation.

Release archive: `PowerMaster-II-Display-0.3.0-notarized.zip`. Generated app/ZIP and Keychain credentials are excluded from Git.
