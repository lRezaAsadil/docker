from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_swagger import swagger

app = Flask(__name__)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient('mongodb://mongo:27017/')
product_db = client['products']
products_collection = product_db['products']

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@user_service/user_db'
db = SQLAlchemy(app)

# Models (User and CartItem for SQLAlchemy)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.String(24), nullable=False)  # MongoDB ObjectId as a string
    quantity = db.Column(db.Integer, nullable=False)

# Swagger specification endpoint
@app.route('/spec')
def spec():
    swag = swagger(app)
    swag['info']['title'] = "Cart Service API"
    swag['info']['description'] = "API documentation for Cart Service"
    swag['info']['version'] = "1.0.0"
    return jsonify(swag)

@app.route('/cart', methods=['GET'])
@jwt_required()
def view_cart():
    """
    View the items in the cart
    ---
    tags:
      - Cart
    security:
      - JWT: []
    responses:
      200:
        description: Successfully retrieved cart items
        schema:
          type: array
          items:
            type: object
            properties:
              product_id:
                type: string
                description: The ID of the product in the cart
              quantity:
                type: integer
                description: The quantity of the product in the cart
              product_details:
                type: object
                properties:
                  name:
                    type: string
                    description: The name of the product
                  price:
                    type: number
                    format: float
                    description: The price of the product
                  description:
                    type: string
                    description: The description of the product
      404:
        description: User not found
      401:
        description: Invalid or missing JWT token
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    cart_items = CartItem.query.filter_by(user_id=user.id).all()
    items = []

    for item in cart_items:
        product = products_collection.find_one({'_id': ObjectId(item.product_id)})
        if product:
            item_info = {
                'product_id': item.product_id,
                'quantity': item.quantity,
                'product_details': {
                    'name': product['name'],
                    'price': product['price'],
                    'description': product.get('description', '')
                }
            }
            items.append(item_info)

    return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
