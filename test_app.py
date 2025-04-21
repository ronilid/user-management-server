import unittest
import json
from app import app, users_by_id

class UserServerTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        self.original_users = users_by_id.copy()

        self.test_user = {
            "id": "123456782",  # Valid Israeli ID
            "name": "Test User",
            "phone_number": "0501112222",
            "address": "Test Address"
        }

    def restore(self):
        # Restore original data after each test
        users_by_id.clear()
        users_by_id.update(self.original_users)

    def test_create_valid_user(self):
        if self.test_user["id"] in users_by_id:
            del users_by_id[self.test_user["id"]]

        response = self.client.post(
            "/users",
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn(self.test_user["id"], users_by_id)

    def test_create_invalid_user(self):
        # Invalid ID
        invalid_user = self.test_user.copy()
        invalid_user["id"] = "123456789"  # invalid checksum

        res = self.client.post("/users", data=json.dumps(invalid_user), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid Israeli ID", res.get_json()["error"])

        # Invalid phone
        invalid_user["id"] = "123456782"
        invalid_user["phone_number"] = "1234567890"

        res = self.client.post("/users", data=json.dumps(invalid_user), content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid phone number", res.get_json()["error"])

    def test_get_user_by_name(self):
        users_by_id[self.test_user["id"]] = self.test_user

        res = self.client.get(f"/users/{self.test_user['name']}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["id"], self.test_user["id"])

    def test_user_not_found(self):
        res = self.client.get("/users/NoSuchUser")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())

if __name__ == "__main__":
    unittest.main()
