# User Management REST API – Python Flask

This project implements a RESTful web server using Python and Flask that allows basic user management operations such as retrieving, creating, updating, and deleting users.

### Technologies
- Python 3.9
- Flask
- unittest (for testing)
- JSON file for data storage

## Files

| File             | Description                           |
|------------------|---------------------------------------|
| `app.py`         | Main Flask application                |
| `users.json`     | Data file storing the users           |
| `test_app.py`    | Unit tests using Python's unittest    |

## Features

- Load user data from a JSON file on server startup
- Save users in a dictionary (key = ID)
- RESTful endpoints for:
  - Retrieving all usernames
  - Retrieving user by name or ID
  - Creating new users
  - Updating users
  - Deleting users
- Input validation:
  - Israeli ID (checksum algorithm)
  - Phone number format: must start with 05 and be 10 digits
- Invalid users from the JSON file are skipped with error messages
- Changes (create/update/delete) are saved back to `users.json`

## How to Run the Server (Linux/macOS)

1. Clone or download the project folder  
2. Make sure you have Python 3 installed:

   ```bash
   python3 --version

3. Install Flask if you haven't:

    ```bash
    pip install flask

4. Run the server:

    ```bash
    python3 app.py

5. The server will run on http://127.0.0.1:5000
6. Open Postman or browser and test the following endpoints.

## How to Run the Tests

Make sure you’re in the project directory. Then run:

```bash
python3 -m unittest test_app.py
