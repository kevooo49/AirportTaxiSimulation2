import unittest
from src.model import AirportModel

class TestAirportModel(unittest.TestCase):

    def setUp(self):
        self.model = AirportModel()

    def test_initial_conditions(self):
        self.assertEqual(len(self.model.schedule.agents), 0)

    def test_step_function(self):
        initial_airplanes = len(self.model.schedule.agents)
        self.model.step()
        self.assertEqual(len(self.model.schedule.agents), initial_airplanes)

    def test_schedule_airplanes(self):
        self.model.schedule_airplanes(5)
        self.assertEqual(len(self.model.schedule.agents), 5)

    def test_airplane_landing(self):
        self.model.schedule_airplanes(1)
        airplane = self.model.schedule.agents[0]
        self.model.land_airplane(airplane)
        self.assertTrue(airplane.landed)

if __name__ == '__main__':
    unittest.main()