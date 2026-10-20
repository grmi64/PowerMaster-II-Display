# PowerMaster II Display 0.4.2 / 7

Handle EAGAIN/EWOULDBLOCK and interrupted nonblocking reads as temporary, with a
short paced retry, preserving the open USB descriptor. Empty reads also retain
the connection. Do not close/reopen a healthy USB connection solely because no
valid frame arrived within three seconds; UI/feed still blank stale values using
the existing two-second freshness limit. Real device I/O errors still reconnect.

Live 0.4.1 diagnostics showed valid zero-power frames, zero CRC/malformed errors,
then errno 35 and repeated stale state. Four tests pass including a regression
that injects EAGAIN, then an empty read, then a valid frame and verifies only one
connection attempt. Physical USB verification follows local installation.
