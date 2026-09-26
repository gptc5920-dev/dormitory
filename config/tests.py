from django.test import SimpleTestCase


class BackendIndexTests(SimpleTestCase):
    def test_index_is_public_and_does_not_require_a_database(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "service": "Smart Dormitory API",
            "api": "/api/",
            "health": "/api/health/",
            "admin": "/admin/",
        })

    def test_index_supports_head_and_rejects_writes(self):
        self.assertEqual(self.client.head("/").status_code, 200)
        self.assertEqual(self.client.post("/").status_code, 405)
