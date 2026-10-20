import errno,fcntl,os,pathlib,sys,tempfile,termios,unittest
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'Sources'))
from port_lock import PortLock,exclusive

class PortLockTests(unittest.TestCase):
 def test_duplicate_rejected_and_lock_released(self):
  with tempfile.TemporaryDirectory() as d,patch('port_lock.Path.home',return_value=pathlib.Path(d)),patch('port_lock.subprocess.run',return_value=SimpleNamespace(returncode=1,stdout='')):
   first=PortLock('/dev/cu.test');second=PortLock('/dev/tty.test')
   first.acquire()
   try:
    with self.assertRaisesRegex(OSError,'already in use'):second.acquire()
   finally:first.release()
   second.acquire();second.release()
 def test_existing_legacy_owner_blocks_connection(self):
  with tempfile.TemporaryDirectory() as d,patch('port_lock.Path.home',return_value=pathlib.Path(d)),patch('port_lock.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='12345\n')):
   lock=PortLock('/dev/cu.test')
   with self.assertRaisesRegex(OSError,'12345'):lock.acquire()
   self.assertIsNone(lock.fd)
 def test_kernel_exclusivity_blocks_noncooperating_open(self):
  master,slave=os.openpty();path=os.ttyname(slave)
  try:
   exclusive(slave)
   try:fd=os.open(path,os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY)
   except OSError as error:self.assertEqual(error.errno,errno.EBUSY)
   else:
    os.close(fd);self.skipTest('macOS pseudo-terminal driver does not enforce TIOCEXCL; verify actual serial driver separately')
   fcntl.ioctl(slave,termios.TIOCNXCL)
   fd=os.open(path,os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY);os.close(fd)
  finally:os.close(slave);os.close(master)
