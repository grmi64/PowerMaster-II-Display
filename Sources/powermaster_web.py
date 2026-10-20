#!/usr/bin/env python3
"""Local PowerMaster II display and connection controller."""
import argparse
import glob
import json
import queue
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from meter_reader import Reader
HTML = Path(__file__).with_name('powermaster_ui.html').read_text()
BAUDS = (9600,19200,38400)

def ports():
    return sorted(set(glob.glob('/dev/cu.usbserial*')+glob.glob('/dev/cu.usbmodem*')))

class Controller:
    def __init__(self, settings, demo=False, port=None, baud=None):
        self.settings, self.demo, self.worker = settings, demo, None
        saved = {}
        try:saved=json.loads(settings.read_text())
        except (OSError,ValueError):pass
        available=ports()
        self.port=port if port is not None else saved.get('port',available[0] if len(available)==1 else '')
        self.baud=baud or saved.get('baud',38400)
        if self.baud not in BAUDS:self.baud=38400
        self.reset()
        if self.port or self.demo:self.connect(self.port,self.baud,save=False)

    def reset(self):
        self.events=queue.Queue();self.last=None
        self.state=dict(status='Disconnected',values=[0,0,0],notice='',frames=0,crc_failures=0,malformed=0,port=self.port,baud=self.baud,demo=self.demo,checksum='—',payload='—',status_fields='—')

    def disconnect(self):
        if self.worker:
            self.worker.stop_event.set();self.worker.join(timeout=2)
            if self.worker.is_alive():raise RuntimeError('Reader is still closing; try again shortly.')
            self.worker=None
        self.reset()

    def connect(self,port,baud,save=True):
        if baud not in BAUDS:raise ValueError('Select a supported baud rate.')
        if not self.demo and (not isinstance(port,str) or not port.startswith('/dev/cu.') or '/' in port[8:]):
            raise ValueError('Select a valid /dev/cu. serial port.')
        self.disconnect()
        self.port,self.baud=port,baud;self.reset()
        if save:
            self.settings.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.settings.with_suffix('.tmp')
            tmp.write_text(json.dumps(dict(port=port,baud=baud)))
            tmp.replace(self.settings)
        self.worker=Reader(port,self.events,self.demo,baud)
        self.state['status']='Connecting';self.worker.start()

    def snapshot(self):
        for _ in range(1000):
            try:kind,data=self.events.get_nowait()
            except queue.Empty:break
            if kind=='reading':
                values,flags,crc,raw,count,bad,crc_bad=data
                self.state.update(status='Live',values=values,status_fields=flags,checksum=crc,payload=raw,frames=count,malformed=bad,crc_failures=crc_bad)
                self.last=time.monotonic()
            elif kind=='status':self.state['status']=data
            elif kind=='notice':self.state['notice']=data
            elif kind=='counts':self.state.update(malformed=data[0],crc_failures=data[1])
        return dict(self.state,age=None if self.last is None else time.monotonic()-self.last,ports=ports(),connected=self.worker is not None)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port');ap.add_argument('--baud',type=int,choices=BAUDS)
    ap.add_argument('--settings',type=Path,default=Path.home()/'Library'/'Application Support'/'com.grmi64.PowerMasterIIDisplay'/'connection.json')
    ap.add_argument('--http-port',type=int,default=0)
    ap.add_argument('--demo',action='store_true');ap.add_argument('--no-browser',action='store_true')
    args=ap.parse_args()
    controller=Controller(args.settings,args.demo,args.port,args.baud)
    token=secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def reply(self,body,status=200,mime='application/json'):
            if not isinstance(body,bytes):body=json.dumps(body).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path=='/'+token+'/':self.reply(HTML.encode(),mime='text/html; charset=utf-8')
            elif self.path=='/'+token+'/state':self.reply(controller.snapshot())
            else:self.send_error(404)
        def do_POST(self):
            if self.path!='/'+token+'/connection' or self.headers.get('X-Meter-Token')!=token:
                self.send_error(403);return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<4096:raise ValueError('Invalid request size')
                data=json.loads(self.rfile.read(length))
                if data.get('action')=='disconnect':controller.disconnect()
                elif data.get('action')=='connect':controller.connect(data.get('port'),int(data.get('baud',0)))
                else:raise ValueError('Unknown connection action')
                self.reply(controller.snapshot())
            except (ValueError,TypeError,OSError,RuntimeError) as exc:self.reply(dict(error=str(exc)),400)
    server=HTTPServer(('127.0.0.1',args.http_port),Handler)
    url=f'http://127.0.0.1:{server.server_port}/{token}/'
    print('PowerMaster II graphical display:',url,flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();controller.disconnect()
if __name__=='__main__':main()
