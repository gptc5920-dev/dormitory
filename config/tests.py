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


class FrontendCorsTests(SimpleTestCase):
    def preflight(self, origin):
        return self.client.options(
            "/api/auth/login/",
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
        )

    def test_deployed_frontend_can_preflight_login(self):
        origin = "https://dormitorykc.online"
        response = self.preflight(origin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], origin)
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])
        self.assertIn("authorization", response.headers["Access-Control-Allow-Headers"])

    def test_unrelated_origin_is_not_allowed(self):
        response = self.preflight("http://unrelated.example")
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
