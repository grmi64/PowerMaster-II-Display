import pathlib,sys,threading,unittest
from unittest.mock import Mock,patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'Sources'))
from meter_reader import Reader

class ReaderRecoveryTests(unittest.TestCase):
 def test_temporary_empty_read_keeps_port_open_and_accepts_next_frame(self):
  events=Mock();reader=Reader('/dev/cu.test',events);reader.stop_event=threading.Event()
  link=Mock(fd=9);parser=Mock(bad=0,crc_bad=0)
  parser.feed.return_value=[((0,0,0),'flags','crc','frame')]
  calls=0
  def ready(*args):
   nonlocal calls
   calls+=1
   if calls==4:reader.stop_event.set();return [],[],[]
   return [9],[],[]
  with patch('meter_reader.Link',return_value=link),patch('meter_reader.Parser',return_value=parser),patch('meter_reader.select.select',side_effect=ready),patch('os.read',side_effect=[BlockingIOError(35,'Resource temporarily unavailable'),b'',b'frame']):
   reader.run()
  link.connect.assert_called_once()
  self.assertTrue(any(call.args[0][0]=='reading' for call in events.put.call_args_list))
  self.assertFalse(any(call.args==(('status','Reconnecting'),) for call in events.put.call_args_list))
