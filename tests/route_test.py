import unittest


from routes import dbSession
from impact import impact
class TestDBSessionFlow(unittest.TestCase):
    #default testing helmet ID is 1
    def setUp(self):
        self.helmet_id = 1

    def test_full_session_flow(self):
        session = dbSession(self.helmet_id)
        result_start = session.start_session()
        self.assertTrue(result_start, "Failed to start session")

        test_impact = impact(
            x=10,
            y=10,
            z=10,
            gx=10,
            gy=10,
            gz=10
        )
        
        # Add impact data
        result_impact = session.add_impact_data(test_impact)
        self.assertTrue(result_impact, "Failed to add impact data")

        # End session
        result_end = session.end_session()
        self.assertTrue(result_end, "Failed to end session")

    def test_impact_no_session(self):
        session = dbSession(self.helmet_id)

        test_impact = impact(
            x=10,
            y=10,
            z=10,
            gx=10,
            gy=10,
            gz=10
        )
        result_impact = session.add_impact_data(test_impact)

        self.assertFalse(result_impact, "Impact data sent with no session")

    def test_end_no_session(self):
        session = dbSession(self.helmet_id)
        result_terminate = session.end_session()

        self.assertFalse(result_terminate, "Ended non existant session")

if __name__ == '__main__':
    unittest.main()
