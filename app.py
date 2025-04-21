from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
users_by_id = {}

# Detect if we're running tests so we don't change the JSON file
IS_TEST_MODE = os.environ.get("TEST_MODE") == "1"

# Validate Israeli ID
def is_valid_id(id):
    if not id.isdigit():
        return False
    id = id.zfill(9)
    total = 0
    for i in range(len(id)):
        digit = int(id[i])
        if i % 2 == 0:
            num = digit
        else:
            num = digit * 2
            if num > 9:
                num -= 9
        total += num
    return total % 10 == 0

# Validate phone number 
def is_valid_phone(phone_number):
    if len(phone_number) != 10:
        return False
    if not phone_number.startswith("05"):
        return False
    if not phone_number.isdigit():
        return False
    return True

# Load users from JSON file into memory
def load_users():
    global users_by_id

    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print("users.json not found")
        return
    except json.JSONDecodeError:
        print("users.json is not valid JSON")
        return

    for user in users:
        if not is_valid_id(user["id"]):
            print(f"Invalid ID for user: {user['name']} (ID: {user['id']})")
        elif not is_valid_phone(user["phone_number"]):
            print(f"Invalid phone number for user: {user['name']} (Phone: {user['phone_number']})")
        else:
            users_by_id[user["id"]] = user

load_users()

# GET – Return a list of all user names
@app.route("/users", methods=["GET"])
def get_all_usernames():
    names = [user["name"] for user in users_by_id.values()]
    return jsonify(names)

# GET – Return a user by name
@app.route("/users/<name>", methods=["GET"])
def get_user_by_name(name):
    for user in users_by_id.values():
        if user["name"].lower() == name.lower():
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# GET - Return a user by ID
@app.route("/users/id/<id>", methods=["GET"])
def get_user_by_id(id):
    user = users_by_id.get(id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# POST – Create a new user
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    required_fields = {"id", "name", "phone_number", "address"}
    
    if not required_fields.issubset(data):
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_id(data["id"]):
        return jsonify({"error": "Invalid Israeli ID"}), 400
    if not is_valid_phone(data["phone_number"]):
        return jsonify({"error": "Invalid phone number"}), 400
    if data["id"] in users_by_id:
        return jsonify({"error": "User with this ID already exists"}), 400
    
    users_by_id[data["id"]] = data
    
    if not IS_TEST_MODE:
        with open("users.json", "w") as f:
            json.dump(list(users_by_id.values()), f, indent=2)
            
    return jsonify({"message": "User created successfully"}), 201

# DELETE - Delete a user by ID
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    if id not in users_by_id:
        return jsonify({"error": "User not found"}), 404

    deleted_user = users_by_id.pop(id)

    if not IS_TEST_MODE:
        with open("users.json", "w") as f:
            json.dump(list(users_by_id.values()), f, indent=2)

    return jsonify({"message": f"User {deleted_user['name']} deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
