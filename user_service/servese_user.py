from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_swagger import swagger

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/user_db'

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False)


@app.route('/spec')
def spec():
    swag = swagger(app)
    swag['info']['title'] = "User Authentication API"
    swag['info']['description'] = "API documentation for User Authentication endpoints"
    swag['info']['version'] = "1.0.0"
    return jsonify(swag)


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: User
          required:
            - username
            - password
            - email
          properties:
            username:
              type: string
              description: Username for the new user
            password:
              type: string
              description: Password for the new user
            email:
              type: string
              description: Email for the new user
    responses:
      201:
        description: User created
      400:
        description: User already exists
    """
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed_password, email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201


@app.route('/login', methods=['POST'])
def login():
    """
    Login a user
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Login
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Username for login
            password:
              type: string
              description: Password for login
    responses:
      200:
        description: Login successful, returns JWT token
      401:
        description: Invalid credentials
    """
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'error': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
