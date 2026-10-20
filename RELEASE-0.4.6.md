# PowerMaster II Display 0.4.6 / 11

Single-reader protection: shared per-user port lock with tty/cu alias
normalization, preflight and post-lock ownership checks for older readers, and
macOS TIOCEXCL serial-port exclusivity. Conflicts refuse to read/configure the
meter and report another reader/PID. Lock descriptors are held for the connection
lifetime and released at close/process exit; persistent lock files are not deleted
so inode races cannot bypass the guard. No radio/CAT code changes.

Tests: 12 run, 11 passed and one skipped because macOS pseudo-terminals do not
enforce TIOCEXCL. Actual FTDI meter-port check passed: an uncooperative second
os.open failed with EBUSY (16), cooperative duplicate failed on the shared lock,
and lsof showed exactly one USB owner. Installed app remained LIVE at 0.1 s age.
Legacy loose powermaster_diagnostic.py in the parent prototype directory also
uses this guard; its prior source is backed up in DXWatcher outputs.

Apple submission 86300a2b-9b79-446c-9b49-40c8d1841fea accepted; signed app stapled,
validated and Gatekeeper accepted. Installed locally in Applications, preserving
0.4.5 backup. Website beta installers remain 0.4.4 pending a new release request.
