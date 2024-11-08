from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from pymongo import MongoClient
from flask_swagger import swagger
import requests  # For communicating with other services

app = Flask(__name__)

# JWT and Database configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@user_service/user_db'

# MongoDB connection
client = MongoClient('mongodb://mongo:27017/')
product_db = client['products']
products_collection = product_db['products']

# Swagger specification endpoint
@app.route('/spec')
def spec():
    swag = swagger(app)
    swag['info']['title'] = "Main Service API"
    swag['info']['description'] = "API documentation for the Main Service"
    swag['info']['version'] = "1.0.0"
    return jsonify(swag)

@app.route('/')
def home():
    """
    Home endpoint
    ---
    tags:
      - Main
    responses:
      200:
        description: Welcome message from the Main Service
    """
    return "Hello from Main Service!"

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user information from the user service by user_id
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        description: The ID of the user to retrieve
        schema:
          type: string
    responses:
      200:
        description: User data returned successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                  description: The user ID
                username:
                  type: string
                  description: The username of the user
                email:
                  type: string
                  description: The email of the user
      404:
        description: User not found
      500:
        description: Error connecting to the user service
    """
    user_service_url = f"http://user_service:5001/user/{user_id}"
    try:
        response = requests.get(user_service_url)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
