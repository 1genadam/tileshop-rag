import unittest
import requests
from unittest.mock import patch

class TestScriptureService(unittest.TestCase):
    BASE_URL = "https://genadam-scripture.herokuapp.com"

    def setUp(self):
        self.session = requests.Session()

    def test_health_check(self):
        response = self.session.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_scripture_endpoint(self):
        response = self.session.get(f"{self.BASE_URL}/scripture")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "scripture")

if __name__ == '__main__':
    unittest.main()
