import unittest
from dotenv import load_dotenv
import os 
from bluepy.btle import Scanner, DefaultDelegate


class TestBlueTooth(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.target_mac = os.getenv('HELMET_MAC_ADDRESS')

        
    def test_discover_device(self):
        scanner = Scanner()
        devices = scanner.scan(10)

        found_device = False

        for dev in devices:
            if dev.addr.lower() == self.target_mac.lower():
                found_device = True

        self.assertTrue(found_device, "Device not reachable!")
        

        

if __name__ == '__main__':
    unittest.main()
