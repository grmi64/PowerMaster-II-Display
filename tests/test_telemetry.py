from types import SimpleNamespace
import json,pathlib,subprocess,sys,tempfile,time,unittest,urllib.request,urllib.error,signal
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'Sources'))
from powermaster_web import Controller
from meter_reader import Reader
from unittest.mock import patch,Mock

class StalledReader(Reader):
 def run(self):time.sleep(60)

class TelemetryTests(unittest.TestCase):
 def test_disabled_and_saved_sharing_and_stale_samples(self):
  with tempfile.TemporaryDirectory() as directory:
   path=pathlib.Path(directory)/'settings.json';c=Controller(path)
   try:
    self.assertFalse(c.share_readings)
    c.set_sharing(True);self.assertTrue(json.loads(path.read_text())['share_readings'])
    c.events.put(('reading',((25,.15,1.17),'0;0;0;0;0','59','test',1,0,0,time.time()-10)))
    time.sleep(.05)
    self.assertEqual(c.telemetry()['status'],'disconnected')
    self.assertIsNone(c.telemetry()['forward_watts'])
    with self.assertRaises(ValueError):c.set_sharing('yes')
   finally:c.disconnect()
   c=Controller(path)
   try:self.assertTrue(c.share_readings)
   finally:c.disconnect()
 def test_shared_wall_clock_freshness_and_stale_expiry(self):
  with tempfile.TemporaryDirectory() as directory:
   c=Controller(pathlib.Path(directory)/'settings.json')
   try:
    c.worker=Mock();c.worker.is_alive.return_value=False
    c.state.update(status='Live',values=[0,0,0]);c.last=time.time()-.3
    self.assertEqual(c.telemetry()['status'],'live')
    c.last=time.time()-3
    self.assertEqual(c.telemetry()['status'],'stale')
    self.assertIsNone(c.telemetry()['forward_watts'])
   finally:c.disconnect()
 def test_reader_event_age_ignores_process_local_monotonic_origin(self):
  with tempfile.TemporaryDirectory() as directory:
   c=Controller(pathlib.Path(directory)/'settings.json')
   try:
    c.events.put(('reading',((0,0,0),'flags','crc','frame',1,0,0,time.time())))
    time.sleep(.05)
    with patch('powermaster_web.time',SimpleNamespace(time=time.time,monotonic=lambda:9999999)):
     data=c.telemetry()
    self.assertEqual(data['status'],'live');self.assertLess(data['age_seconds'],1)
   finally:c.disconnect()
 def test_stalled_usb_worker_does_not_block_display_state(self):
  with tempfile.TemporaryDirectory() as directory:
   with patch('powermaster_web.Reader',StalledReader):
    c=Controller(pathlib.Path(directory)/'settings.json',port='/dev/cu.test')
   try:
    started=time.monotonic();snapshot=c.snapshot()
    self.assertLess(time.monotonic()-started,.5)
    self.assertEqual(snapshot['status'],'Connecting')
   finally:c.disconnect()
 def test_http_feed_opt_in_and_independent_of_ui(self):
  with tempfile.TemporaryDirectory() as directory:
   source=pathlib.Path(__file__).resolve().parents[1]/'Sources'/'powermaster_web.py'
   p=subprocess.Popen([sys.executable,str(source),'--demo','--no-browser','--settings',directory+'/settings.json'],stdout=subprocess.PIPE,text=True)
   try:
    url=p.stdout.readline().strip().split('display: ')[1];base=url.rsplit('/',2)[0];token=url.strip('/').split('/')[-1]
    with urllib.request.urlopen(url+'display.js') as asset:
     self.assertIn('javascript',asset.headers['Content-Type']);self.assertIn('class DisplayModel',asset.read().decode())
    with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+'/api/v1/telemetry')
    self.assertEqual(error.exception.code,403)
    def share(enabled):
     request=urllib.request.Request(url+'connection',data=json.dumps({'action':'sharing','enabled':enabled}).encode(),headers={'Content-Type':'application/json','X-Meter-Token':token})
     return json.load(urllib.request.urlopen(request))
    share(True);time.sleep(.3)
    data=json.load(urllib.request.urlopen(base+'/api/v1/telemetry'))
    self.assertEqual(data['schema_version'],1);self.assertEqual(data['status'],'live');self.assertTrue(data['demo'])
    share(False)
    with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(base+'/api/v1/telemetry')
   finally:p.send_signal(signal.SIGINT);p.wait(timeout=5);p.stdout.close()
if __name__=='__main__':unittest.main()
