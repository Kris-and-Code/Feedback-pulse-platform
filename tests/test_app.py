import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.security import clamp_top_k, is_amazon_url, is_safe_http_url, resolve_project_csv_path, validate_text_input


class SecurityTests(unittest.TestCase):
    def test_blocks_localhost(self):
        self.assertFalse(is_safe_http_url("http://127.0.0.1/admin"))

    def test_blocks_private_ip(self):
        self.assertFalse(is_safe_http_url("http://192.168.1.1/"))

    def test_allows_public_https(self):
        self.assertTrue(is_safe_http_url("https://example.com/reviews"))

    def test_amazon_host(self):
        self.assertTrue(is_amazon_url("https://www.amazon.com/dp/B012345678"))

    def test_top_k_clamped(self):
        self.assertEqual(clamp_top_k(100), 20)

    def test_text_length(self):
        with self.assertRaises(ValueError):
            validate_text_input("x" * 20000)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_analyze_text_simple(self):
        response = self.client.post("/analyze-text", json={"text": "I love this product", "mode": "simple"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("sentiment", payload)
        self.assertIn("emotion", payload)

    def test_scrape_review_blocks_internal_url(self):
        response = self.client.post("/scrape-review", json={"url": "http://127.0.0.1/"})
        self.assertEqual(response.status_code, 400)

    def test_legacy_status(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)

    def test_feedback_create(self):
        response = self.client.post(
            "/feedback",
            json={"review_text": "Great product", "rating": 5, "mode": "simple"},
        )
        self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
