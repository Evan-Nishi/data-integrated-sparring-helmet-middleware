import unittest

from routes import dbSession

class TestDBSessionFlow(unittest.TestCase):
    #default testing helmet ID is 1
    def setUp(self):
        self.helmet_id = 1

    def test_full_session_flow(self):
        session = dbSession(self.helmet_id)
        result_start = session.start_session()
        self.assertTrue(result_start, "Failed to start session")

        # Add impact data
        content = {
            'x': 10,
            'y': 10,
            'z': 10
        }
        result_impact = session.add_impact_data(content=content)
        self.assertTrue(result_impact, "Failed to add impact data")

        # End session
        result_end = session.end_session()
        self.assertTrue(result_end, "Failed to end session")

    def test_impact_no_session(self):
        session = dbSession(self.helmet_id)

        content = {
            'x': 10,
            'y': 10,
            'z': 10
        }

        result_impact = session.add_impact_data(content=content)

        self.assertFalse(result_impact, "Impact data sent with no session")

    def test_end_no_session(self):
        session = dbSession(self.helmet_id)
        result_terminate = session.end_session()

        self.assertFalse(result_terminate, "Ended non existant session")

if __name__ == '__main__':
    unittest.main()
