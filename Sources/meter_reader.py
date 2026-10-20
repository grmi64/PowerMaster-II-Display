import queue, threading, time, math, select
from powermaster_diagnostic import Link, Parser

class Reader(threading.Thread):
    def __init__(self, port, events, demo=False):
        super().__init__(daemon=True)
        self.port, self.events, self.demo = port, events, demo
        self.stop_event = threading.Event()

    def emit(self, kind, value):
        self.events.put((kind, value))

    def run(self):
        link = Link(self.port)
        parser = Parser()
        count = 0
        started = time.monotonic()
        try:
            while not self.stop_event.is_set():
                if self.demo:
                    active = int(time.monotonic()-started) % 12 < 8
                    fwd = 25 + math.sin(time.monotonic()) if active else 0
                    self.emit('reading', ((fwd,.15,1.17) if active else (0,0,0), '0;0;0;0;0', '--', 'SIMULATION', count, 0, 0))
                    count += 1
                    self.stop_event.wait(.2)
                    continue
                try:
                    self.emit('status', 'Connecting')
                    link.connect()
                    parser.buffer.clear()
                    last = time.monotonic()
                    while not self.stop_event.is_set():
                        ready,_,_ = select.select([link.fd],[],[],.1)
                        if ready:
                            import os
                            data = os.read(link.fd,4096)
                            if not data:
                                # Empty nonblocking reads are not proof of USB removal.
                                if time.monotonic() - last > 3:
                                    raise OSError('No valid readings for 3 seconds')
                                self.stop_event.wait(.02)
                                continue
                            for values, flags, crc, raw in parser.feed(data):
                                if values is None:
                                    self.emit('notice',raw)
                                else:
                                    last = time.monotonic()
                                    count += 1
                                    self.emit('reading',(values,flags,crc,raw,count,parser.bad,parser.crc_bad))
                            self.emit('counts',(parser.bad,parser.crc_bad))
                        if time.monotonic()-last > 3:
                            raise OSError('No valid readings for 3 seconds')
                except Exception as exc:
                    self.emit('status','Reconnecting')
                    self.emit('notice',str(exc))
                finally:
                    link.close()
                self.stop_event.wait(2)
        finally:
            link.close()

