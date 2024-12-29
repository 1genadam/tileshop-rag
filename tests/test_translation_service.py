import unittest
import requests
from unittest.mock import patch

class TestTranslationService(unittest.TestCase):
    BASE_URL = "https://genadam-translate.herokuapp.com"

    def setUp(self):
        self.session = requests.Session()

    def test_health_check(self):
        response = self.session.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_translation_endpoint(self):
        response = self.session.get(f"{self.BASE_URL}/translate")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "translation")

if __name__ == '__main__':
    unittest.main()
