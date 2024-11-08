from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_swagger import swagger

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure value
jwt = JWTManager(app)

# MongoDB connection for products
client = MongoClient('mongodb://localhost:27017/')
product_db = client['products']
products_collection = product_db['products']

# Swagger route for API documentation
@app.route('/swagger.json')
def spec():
    return jsonify(swagger(app))

# Get All Products
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """
    Get All Products
    ---
    responses:
      200:
        description: A list of products
    """
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products)

# Create a product (admin only)
@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    """
    Create a Product (Admin Only)
    ---
    parameters:
      - name: product
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
    responses:
      201:
        description: Product created
    """
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'error': 'Access forbidden Admins only'}), 403

    product_data = request.json
    products_collection.insert_one(product_data)
    return jsonify(product_data), 201

# Update a product (admin only)
@app.route('/products/<id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    """
    Update a Product (Admin Only)
    ---
    parameters:
      - name: id
        description: Product ID
        required: true
        type: string
      - name: product
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
    responses:
      200:
        description: Product updated
      403:
        description: Access forbidden Admins only
      404:
        description: Product not found
    """
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'error': 'Access forbidden Admins only'}), 403
    
    product_data = request.json
    result = products_collection.update_one({'_id': ObjectId(id)}, {'$set': product_data})
    if result.matched_count > 0:
        updated_product = products_collection.find_one({'_id': ObjectId(id)})
        updated_product['_id'] = str(updated_product['_id'])
        return jsonify(updated_product)
    return jsonify({'error': 'Product not found'}), 404

# Delete a product (admin only)
@app.route('/products/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    """
    Delete a Product (Admin Only)
    ---
    parameters:
      - name: id
        description: Product ID
        required: true
        type: string
    responses:
      200:
        description: Product deleted
      403:
        description: Access forbidden Admins only
      404:
        description: Product not found
    """
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'error': 'Access forbidden Admins only'}), 403
    
    result = products_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({'message': 'Product deleted'})
    return jsonify({'error': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run the product service on a different port
