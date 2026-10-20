#!/usr/bin/env python3
"""Local graphical PowerMaster II prototype. Python 3; no packages required."""
import argparse
import json
import queue
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from meter_reader import Reader

from pathlib import Path
HTML = Path(__file__).with_name('powermaster_ui.html').read_text()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port',default='/dev/cu.usbserial-A400gmxx')
    ap.add_argument('--http-port',type=int,default=0)
    ap.add_argument('--demo',action='store_true')
    ap.add_argument('--no-browser',action='store_true')
    args=ap.parse_args()
    events=queue.Queue();worker=Reader(args.port,events,args.demo)
    state={'status':'Connecting','values':[0,0,0],'notice':'','frames':0,'crc_failures':0,'malformed':0,'port':args.port,'demo':args.demo,'checksum':'—','payload':'—','status_fields':'—'}
    last=None
    token=secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def do_GET(self):
            nonlocal last
            if self.path not in ('/'+token+'/', '/'+token+'/state'):
                self.send_error(404);return
            if self.path.endswith('/state'):
                for _ in range(500):
                    try:kind,data=events.get_nowait()
                    except queue.Empty:break
                    if kind=='reading':
                        values,flags,crc,raw,count,bad,crc_bad=data
                        state.update(status='Live',values=values,status_fields=flags,checksum=crc,payload=raw,frames=count,malformed=bad,crc_failures=crc_bad)
                        last=time.monotonic()
                    elif kind=='status':state['status']=data
                    elif kind=='notice':state['notice']=data
                    elif kind=='counts':state.update(malformed=data[0],crc_failures=data[1])
                age=None if last is None else time.monotonic()-last
                body=json.dumps(dict(state,age=age)).encode();mime='application/json'
            else:body=HTML.encode();mime='text/html; charset=utf-8'
            self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    # Single HTTP handler at a time preserves event ordering.
    from http.server import HTTPServer
    server=HTTPServer(('127.0.0.1',args.http_port),Handler)
    url=f'http://127.0.0.1:{server.server_port}/{token}/'
    worker.start()
    print('PowerMaster II graphical display:',url,flush=True)
    print('Press Control-C here to stop. USB reconnect is automatic.',flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        server.server_close();worker.stop_event.set();worker.join(timeout=2)
if __name__=='__main__':main()
