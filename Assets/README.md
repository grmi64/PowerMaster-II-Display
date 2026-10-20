# PowerMaster II Display icon

Companion to the KPA1500 Control instrument icon: graphite/navy machined casing, a dominant horizontal blue power bar with a blue RF waveform underneath. Distinct power-bar geometry and color make the meter recognizable beside the curved mint gauge and amber needle of KPA1500.

AppIcon-source.png is the transparent master artwork. AppIcon.icns is used by macOS through CFBundleIconFile. AppIcon.ico contains 16, 24, 32, 48, 64, 128 and 256px PNG-backed entries for future modern Windows packaging. No Windows executable is built yet.

Run `python3 scripts/build_icons.py` on macOS to recreate the ICNS and ICO containers using sips and iconutil. Build consumes the prebuilt ICNS.
