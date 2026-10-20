#!/usr/bin/env python3
"""PowerMaster II live Terminal diagnostic. Python 3, macOS; no dependencies.
Run: python3 powermaster_diagnostic.py
Optional: --port /dev/cu.usbserial-... --demo --self-test
Only transmits the hardware-tested D3 stream command. No settings writes.
Checksums validated using CRC inferred from captured frames. Hardware streaming may continue
when this program exits; a stop command has not yet been verified.
"""
import argparse
import curses
import math
import os
import select
import termios
import time

START = bytes.fromhex('02 44 33 03 31 33 0D')

def crc8(payload):
    """Inferred from captured hardware frames: MSB-first B1, init 00, xor FF."""
    crc = 0
    for byte in payload:
        crc ^= byte
        for _ in range(8):
            crc = (((crc << 1) ^ 0xB1) if crc & 0x80 else crc << 1) & 255
    return crc ^ 255


class Link:
    def __init__(self, port, baud=38400):
        self.port, self.fd, self.old = port, None, None
        self.baud = baud

    def close(self):
        if self.fd is not None:
            try:
                if self.old is not None:
                    termios.tcsetattr(self.fd, termios.TCSANOW, self.old)
            except (OSError, termios.error):
                pass
            finally:
                os.close(self.fd)
                self.fd, self.old = None, None

    def connect(self):
        self.fd = os.open(self.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            self.old = termios.tcgetattr(self.fd)
            a = termios.tcgetattr(self.fd)
            a[0] = a[1] = a[3] = 0
            a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
            a[4] = a[5] = {9600:termios.B9600,19200:termios.B19200,38400:termios.B38400}[self.baud]
            a[6][termios.VMIN] = 1
            a[6][termios.VTIME] = 0
            termios.tcsetattr(self.fd, termios.TCSANOW, a)
            termios.tcflush(self.fd, termios.TCIFLUSH)
            os.write(self.fd, START)
            termios.tcdrain(self.fd)
        except Exception:
            self.close()
            raise


class Parser:
    def __init__(self):
        self.buffer = bytearray()
        self.bad = 0
        self.crc_bad = 0

    def feed(self, data):
        self.buffer.extend(data)
        results = []
        while True:
            start = self.buffer.find(b'\x02')
            if start < 0:
                self.buffer.clear()
                break
            del self.buffer[:start]
            end = self.buffer.find(b'\r\n')
            if end < 0:
                if len(self.buffer) > 4096:
                    self.buffer.clear()
                    self.bad += 1
                break
            frame = bytes(self.buffer[:end])
            del self.buffer[:end + 2]
            try:
                # Recover if a truncated frame preceded this complete frame.
                frame = frame[frame.rfind(b'\x02'):]
                payload, checksum = frame[1:].split(b'\x03')
                if len(checksum) != 2:
                    raise ValueError('checksum length')
                if crc8(payload) != int(checksum, 16):
                    self.crc_bad += 1
                    continue
                text = payload.decode('ascii')
                if text.startswith('D,'):
                    fields = text.split(',')
                    if len(fields) != 5:
                        raise ValueError('field count')
                    values = tuple(float(x) for x in fields[1:4])
                    if not all(math.isfinite(x) and x >= 0 for x in values):
                        raise ValueError('invalid measurement')
                    results.append((values, fields[4], checksum.decode(), text))
                elif text != 'A':
                    results.append((None, '', checksum.decode(), text))
            except (ValueError, UnicodeError):
                self.bad += 1
        return results


def screen(win, args, link):
    curses.curs_set(0)
    win.nodelay(True)
    parser = Parser()
    latest = None
    last = None
    count = 0
    began = time.monotonic()
    raw = 'Waiting for a measurement frame'
    checksum = '--'
    flags = '--'
    error = ''
    notice = ''
    retry_at = 0
    connected_at = 0
    while True:
        now = time.monotonic()
        if args.demo:
            time.sleep(.05)
            if last is None or now - last >= .2:
                active = int(now - began) % 12 < 8
                latest = (24.8, .15, 1.17) if active else (0., 0., 0.)
                last = now
                count += 1
                raw = 'SIMULATED readings; no hardware connection'
        else:
            if link.fd is None and now >= retry_at:
                try:
                    link.connect()
                    parser.buffer.clear()
                    connected_at = now
                    last = None
                    error = ''
                except (OSError, termios.error) as exc:
                    error = 'Reconnecting: ' + str(exc)
                    retry_at = now + 2
            if link.fd is not None:
                try:
                    ready, _, _ = select.select([link.fd], [], [], .05)
                    if ready:
                        data = os.read(link.fd, 4096)
                        if not data:
                            raise OSError('Device closed connection')
                        for values, flags_in, crc, text in parser.feed(data):
                            raw = text
                            if values is not None:
                                latest, flags, checksum = values, flags_in, crc
                                last = time.monotonic()
                                count += 1
                            else:
                                notice = 'Unidentified meter message: ' + text
                    if time.monotonic() - (last or connected_at) > 3:
                        raise OSError('No valid measurement frames for 3 seconds')
                except (OSError, termios.error) as exc:
                    error = 'Reconnecting: ' + str(exc)
                    link.close()
                    retry_at = time.monotonic() + 2
            else:
                time.sleep(.05)
        age = None if last is None else time.monotonic() - last
        status = 'WAITING' if age is None else ('STALE' if age > 2 else 'LIVE')
        if error:
            status = 'RECONNECTING'
        rows = [
            'POWERMASTER II — LIVE DIAGNOSTIC' + (' [DEMO]' if args.demo else ''),
            '',
            f'Port: {args.port}     38400 8N1',
            f'Status: {status}' + (f'    Last reading: {age:.1f}s ago' if age is not None else ''),
            '',
        ]
        if latest is None or status != 'LIVE':
            rows += ['FORWARD       -- W', 'REFLECTED     -- W', 'SWR           --']
        else:
            fwd, ref, swr = latest
            rows += [f'FORWARD       {fwd:10.2f} W', f'REFLECTED     {ref:10.2f} W',
                     f'SWR           {swr:10.2f} : 1' if fwd > 0 and swr >= 1 else 'SWR           -- (no valid RF reading)']
        rows += ['', f'Measurement frames: {count}   Average received: {count / max(.1, now-began):.1f}/s',
                 f'Malformed frames: {parser.bad}   CRC failures: {parser.crc_bad}',
                 f'Checksum: {checksum} — VALIDATED (inferred CRC-8/B1)'
                 if count and not args.demo else 'Checksum: --',
                 f'Unidentified status fields: {flags}', '', 'Latest payload:', raw,
                 '', error or notice, '', 'Q: quit     Automatic reconnect every 2 seconds.',
                 'Meter streaming may continue after exit; stop command unverified.']
        win.erase()
        h, w = win.getmaxyx()
        for y, line in enumerate(rows[:max(0, h-1)]):
            try:
                win.addnstr(y, 0, line, max(0,w-1), curses.A_BOLD if y in (0, 3, 5, 6, 7) else 0)
            except curses.error:
                pass
        win.refresh()
        if win.getch() in (ord('q'), ord('Q'), 27):
            break


def self_test():
    p = Parser()
    frame = b'\x02D,24.88,0.15,1.17,0;0;0;0;0\x0359\r\n'
    assert p.feed(b'\x00\x02A\x038F\r\n' + frame[:9]) == []
    rows = p.feed(frame[9:] + frame)
    assert len(rows) == 2 and rows[0][0] == (24.88, .15, 1.17)
    assert p.feed(b'\x02D,nan,0,0,0;0;0;0;0\x0300\r\n') == []
    assert p.crc_bad == 1
    assert p.feed(b'\x02partial' + frame)[0][0] == (24.88,.15,1.17)
    for payload, expected in [(b'A',0x8F),(b'D3',0x13),(b'D,0.00,0.00,0.00,0;0;0;0;0',0xB0),(b'D,24.81,0.15,1.17,0;0;0;0;0',0x43),(b'D,24.78,0.14,1.16,0;0;0;0;0',0x05),(b'D,24.76,0.15,1.17,0;0;0;0;0',0x0D),(b'D,24.71,0.15,1.17,0;0;0;0;0',0x94),(b'D,24.69,0.14,1.17,0;0;0;0;0',0x1C),(b'D,24.66,0.14,1.16,0;0;0;0;0',0x00),(b'D,24.61,0.14,1.17,0;0;0;0;0',0x35)]:
        assert crc8(payload) == expected, payload
    print('CRC captured-frame checks passed.')
    print('Parser checks passed: partial, repeated, corrupt, and recovered frames.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port', default='/dev/cu.usbserial-A400gmxx')
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    link = Link(args.port)
    try:
        curses.wrapper(screen, args, link)
    except KeyboardInterrupt:
        pass
    except (OSError, termios.error, curses.error) as exc:
        print('Unable to run diagnostic:', exc)
    finally:
        link.close()

if __name__ == '__main__':
    main()
