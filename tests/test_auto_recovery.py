import pathlib,sys,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'Sources'))
from powermaster_web import Controller

class AutoRecoveryTests(unittest.TestCase):
 def test_three_paced_retries_then_stop_and_manual_reset(self):
  with tempfile.TemporaryDirectory() as d:
   c=Controller(pathlib.Path(d)/'settings.json');now=[100.]
   worker=Mock();worker.is_alive.return_value=False
   c.worker=worker;c.attempt_started=90
   with patch('powermaster_web.time',SimpleNamespace(time=lambda:now[0])),patch('powermaster_web.Reader',return_value=worker) as reader:
    for attempt,delay in enumerate((2,5,10)):
     c.recover_if_needed();self.assertEqual(c.state['status'],'Reconnecting')
     self.assertEqual(c.recovery_due,now[0]+delay)
     c.recover_if_needed();self.assertEqual(reader.call_count,attempt)
     now[0]+=delay;c.recover_if_needed();self.assertEqual(reader.call_count,attempt+1)
     now[0]+=9
    c.recover_if_needed();self.assertEqual(c.state['status'],'Recovery stopped')
    now[0]+=100;c.recover_if_needed();self.assertEqual(reader.call_count,3)
    c.connect('/dev/cu.test',38400,save=False);self.assertEqual(c.recovery_attempts,0)
   c.worker=None
 def test_fresh_zero_power_does_not_retry_and_requires_stable_reset(self):
  with tempfile.TemporaryDirectory() as d:
   c=Controller(pathlib.Path(d)/'settings.json');c.worker=Mock();c.recovery_attempts=2
   c.state.update(status='Live',values=[0,0,0]);now=[100.];c.last=100.
   with patch('powermaster_web.time',SimpleNamespace(time=lambda:now[0])),patch('powermaster_web.Reader') as reader:
    c.recover_if_needed();self.assertEqual(c.recovery_attempts,2)
    now[0]=131;c.last=131;c.recover_if_needed();self.assertEqual(c.recovery_attempts,0);reader.assert_not_called()
   c.worker=None
 def test_hung_worker_is_not_reopened_concurrently(self):
  with tempfile.TemporaryDirectory() as d:
   c=Controller(pathlib.Path(d)/'settings.json');c.worker=Mock();c.worker.is_alive.return_value=True
   c.attempt_started=0;c.recovery_due=1
   with patch('powermaster_web.Reader') as reader:
    c.recover_if_needed();reader.assert_not_called();self.assertEqual(c.state['status'],'Recovery stopped')
   c.worker=None
