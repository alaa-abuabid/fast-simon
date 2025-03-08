import unittest
from unittest.mock import patch
from main import app, related

class RelatedQueriesUnitTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('main.get_related_queries')
    def test_non_existing_query(self, mock_get_related_queries):
        mock_get_related_queries.return_value = []
        with app.test_request_context('/related?query=nonexistentquery'):
            response = related()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    @patch('main.get_related_queries')
    def test_very_popular_query(self, mock_get_related_queries):
        mock_get_related_queries.return_value = ["long dress", "cocktail dress", "shoes"]
        with app.test_request_context('/related?query=dress'):
            response = related()
            self.assertEqual(response.status_code, 200)
            self.assertIn("long dress", response.json)
            self.assertIn("cocktail dress", response.json)
            self.assertIn("shoes", response.json)

    @patch('main.get_related_queries')
    def test_not_very_popular_query(self, mock_get_related_queries):
        mock_get_related_queries.return_value = ["unique result"]
        with app.test_request_context('/related?query=uniquequery'):
            response = related()
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(response.json, list))
            self.assertEqual(len(response.json), 1)

if __name__ == '__main__':
    unittest.main()