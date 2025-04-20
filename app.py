from flask import Flask, request, jsonify
import json
import re
import os

app = Flask(__name__)
users_by_id = {}

# Detect test mode via environment variable
IS_TEST_MODE = os.environ.get("TEST_MODE") == "1"

# Validate Israeli ID
def is_valid_israeli_id(id_str):
    if not id_str.isdigit():
        return False
    id_str = id_str.zfill(9)
    total = 0
    for i, digit in enumerate(id_str):
        num = int(digit) * (1 if i % 2 == 0 else 2)
        if num > 9:
            num -= 9
        total += num
    return total % 10 == 0

# Validate phone number (must be 10 digits starting with 05)
def is_valid_phone(phone_number):
    return re.fullmatch(r"05\d{8}", phone_number) is not None

# Load users from JSON file into memory
def load_users():
    global users_by_id
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            for user in data:
                if is_valid_israeli_id(user["id"]) and is_valid_phone(user["phone_number"]):
                    users_by_id[user["id"]] = user
                else:
                    print(f"Invalid user: {user['name']} – ID or phone is invalid.")
    except FileNotFoundError:
        print("Warning: users.json not found. Starting with empty user list.")
        return
    except json.JSONDecodeError:
        print("Error: users.json is not valid JSON. Starting with empty user list.")
        return

load_users()

# GET /users – Return a list of all user names
@app.route("/users", methods=["GET"])
def get_all_usernames():
    return jsonify([user["name"] for user in users_by_id.values()])

# GET /users/<name> – Return a user by name
@app.route("/users/<name>", methods=["GET"])
def get_user_by_name(name):
    for user in users_by_id.values():
        if user["name"].lower() == name.lower():
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# GET /users/id/<id> - Return a user by ID
@app.route("/users/id/<id>", methods=["GET"])
def get_user_by_id(id):
    user = users_by_id.get(id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# POST /users – Create a new user
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    required_fields = {"id", "name", "phone_number", "address"}
    if not required_fields.issubset(data):
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_israeli_id(data["id"]):
        return jsonify({"error": "Invalid Israeli ID"}), 400
    if not is_valid_phone(data["phone_number"]):
        return jsonify({"error": "Invalid phone number"}), 400
    if data["id"] in users_by_id:
        return jsonify({"error": "User with this ID already exists"}), 400
    users_by_id[data["id"]] = data
    if not IS_TEST_MODE:
        with open("users.json", "w") as f:
            json.dump(list(users_by_id.values()), f, indent=2)
    # with open("users.json", "w") as f:
    #     json.dump(list(users_by_id.values()), f, indent=2)
    return jsonify({"message": "User created successfully"}), 201
    
 
# PUT /users/<id> - Update an existing user   
@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    if id not in users_by_id:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user = users_by_id[id]

    for field in ["name", "phone_number", "address"]:
        if field in data:
            user[field] = data[field]

    if "phone_number" in data and not is_valid_phone(user["phone_number"]):
        return jsonify({"error": "Invalid phone number"}), 400

    # with open("users.json", "w") as f:
    #     json.dump(list(users_by_id.values()), f, indent=2)
    if not IS_TEST_MODE:
        with open("users.json", "w") as f:
            json.dump(list(users_by_id.values()), f, indent=2)

    return jsonify({"message": "User updated successfully"}), 200

# DELETE /users/<id> - Delete a user by ID
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    if id not in users_by_id:
        return jsonify({"error": "User not found"}), 404

    deleted_user = users_by_id.pop(id)

    # with open("users.json", "w") as f:
    #     json.dump(list(users_by_id.values()), f, indent=2)
    if not IS_TEST_MODE:
        with open("users.json", "w") as f:
            json.dump(list(users_by_id.values()), f, indent=2)

    return jsonify({"message": f"User {deleted_user['name']} deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
