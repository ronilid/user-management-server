import unittest
import json
import os

# Activate test mode before importing the app
os.environ["TEST_MODE"] = "1"

from app import app, is_valid_israeli_id, is_valid_phone, users_by_id

class UserServerTests(unittest.TestCase):

    def setUp(self):
        # Create test client
        app.testing = True
        self.client = app.test_client()
        
        # Save the original users for restoration later
        self.original_users = users_by_id.copy()
        
        # Create test user to be added during the test
        self.test_user = {
            "id": "123456782",  # Valid Israeli ID
            "name": "Test User",
            "phone_number": "0501112222",
            "address": "Test Address"
        }

    def tearDown(self):
        # Restore the original users after each test
        users_by_id.clear()
        users_by_id.update(self.original_users)

    def test_validator_functions(self):
        """Test the ID and phone validator functions"""
        # Valid cases
        self.assertTrue(is_valid_israeli_id("123456782"))
        self.assertTrue(is_valid_phone("0501234567"))
        
        # Invalid cases
        self.assertFalse(is_valid_israeli_id("123456789"))  # Invalid checksum
        self.assertFalse(is_valid_phone("1234567890"))      # Not starting with 05
        self.assertFalse(is_valid_phone("050123"))          # Too short

    def test_get_all_users(self):
        """Test retrieving all usernames"""
        # Add a test user directly to the dictionary
        users_by_id[self.test_user["id"]] = self.test_user
        
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(self.test_user["name"], data)

    def test_get_user_by_name(self):
        """Test retrieving a user by name"""
        # Add a test user directly to the dictionary
        users_by_id[self.test_user["id"]] = self.test_user
        
        # Test getting the user by name
        response = self.client.get(f"/users/{self.test_user['name']}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], self.test_user["id"])
        self.assertEqual(data["phone_number"], self.test_user["phone_number"])

    def test_user_not_found(self):
        """Test behavior when user doesn't exist"""
        response = self.client.get("/users/UserThatShouldNotExist12345")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_create_valid_user(self):
        """Test creating a new valid user"""
        # Make sure the user doesn't already exist
        if self.test_user["id"] in users_by_id:
            del users_by_id[self.test_user["id"]]
            
        response = self.client.post(
            "/users",
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify the user was added
        self.assertIn(self.test_user["id"], users_by_id)
        
        # Check if we can get the newly created user
        get_response = self.client.get(f"/users/{self.test_user['name']}")
        self.assertEqual(get_response.status_code, 200)

    def test_create_invalid_user(self):
        """Test validation when creating users"""
        # Test with invalid ID
        invalid_id_user = self.test_user.copy()
        invalid_id_user["id"] = "123456789"  # Invalid ID
        response = self.client.post(
            "/users",
            data=json.dumps(invalid_id_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Israeli ID", response.get_json()["error"])
        
        # Test with invalid phone
        invalid_phone_user = self.test_user.copy()
        invalid_phone_user["id"] = "123456782"
        invalid_phone_user["phone_number"] = "1234567890"  # Invalid phone
        response = self.client.post(
            "/users",
            data=json.dumps(invalid_phone_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid phone number", response.get_json()["error"])
        
    def test_update_user(self):
        """Test updating a user"""
        users_by_id[self.test_user["id"]] = self.test_user

        update_data = {
            "address": "New Address"
        }

        response = self.client.put(
            f"/users/{self.test_user['id']}",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(users_by_id[self.test_user["id"]]["address"], "New Address")
    
    def test_delete_user(self):
        """Test deleting a user"""
        users_by_id[self.test_user["id"]] = self.test_user

        response = self.client.delete(f"/users/{self.test_user['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.test_user["id"], users_by_id)

if __name__ == "__main__":
    unittest.main()