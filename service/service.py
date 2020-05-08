"""

Supplliers Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /suppliers - Returns a list all of the Suppliers
GET /suppliers/{id} - Returns the Supplier with a given id number
POST /suppliers - creates a new Supplier record in the database
PUT /suppliers/{id} - updates a Supplier record in the database
DELETE /suppliers/{id} - deletes a Supplier record in the database
"""

import os
import sys
import uuid
import logging
from functools import wraps
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs
from werkzeug.utils import cached_property

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Supplier, DataValidationError, Product, DatabaseConnectionError

# Import Flask application
from . import app

# Document the type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Supplier Demo REST API Service',
          description='This is a sample server Supplier store server.',
          default='suppliers',
          default_label='Supplier shop operations',
          doc='/', # default also could use doc='/apidocs/'
          authorizations=authorizations
          # prefix='/api'
         )

# Define the model so that the docs reflect what can be sent
supplier_model = api.model('Supplier', {
    '_id': fields.String(readOnly=True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'category': fields.String(required=True,
                              description='The category of Supplier (e.g., dog, cat, fish, etc.)'),
    'preferred': fields.Boolean(required=True,
                                description='Is the Supplier preferred for purchase?')
})

create_model = api.model('Supplier', {
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'category': fields.String(required=True,
                              description='The category of Supplier (e.g., dog, cat, fish, etc.)'),
    'preferred': fields.Boolean(required=True,
                                description='Is the Supplier preferred for purchase?')
})

# query string arguments
supplier_args = reqparse.RequestParser()
supplier_args.add_argument('name', type=str, required=False, help='List Suppliers by name')
supplier_args.add_argument('category', type=str, required=False, help='List Suppliers by category')
supplier_args.add_argument('preferred', type=inputs.boolean, required=False, help='List Suppliers by availability')

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE

######################################################################
# Authorization Decorator
######################################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Api-Key' in request.headers:
            token = request.headers['X-Api-Key']

        if app.config.get('API_KEY') and app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid or missing token'}, 401
    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return uuid.uuid4().hex
    
######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

######################################################################
#  PATH: /suppliers/{id}
######################################################################
@api.route('/suppliers/<supplier_id>')
@api.param('supplier_id', 'The Supplier identifier')
class SupplierResource(Resource):
    """
    SupplierResource class

    Allows the manipulation of a single Supplier
    GET /supplier{id} - Returns a Supplier with the id
    PUT /supplier{id} - Update a Supplier with the id
    DELETE /supplier{id} -  Deletes a Supplier with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A SUPPLIER
    #------------------------------------------------------------------@app.route("/suppliers/<int:supplier_id>", methods=["GET"])
    @api.doc('get_suppliers')
    @api.response(404, 'Supplier not found')
    @api.marshal_with(supplier_model)
    
    def get_suppliers(supplier_id):
        """
        Retrieve a single Supplier
        This endpoint will return a Supplier based on it's id
        """
        app.logger.info("Request for Supplier with id: %s", supplier_id)
        supplier = Supplier.find_or_404(supplier_id)
        return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

    #------------------------------------------------------------------
    # UPDATE AN EXISTING SUPPLIER
    #------------------------------------------------------------------
    @api.doc('update_suppliers', security='apikey')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'The posted Supplier data was not valid')
    @api.expect(supplier_model)
    @api.marshal_with(supplier_model)
    @token_required
    @app.route("/suppliers/<int:supplier_id>", methods=["PUT"])
    def update_suppliers(supplier_id):
        """
        Update a Supplier
        This endpoint will update a Supplier based the body that is posted
        """
        app.logger.info("Request to update supplier with id: %s", supplier_id)
        check_content_type("application/json")
        supplier = Supplier.find(supplier_id)
        if not supplier:
            raise NotFound("Supplier with id '{}' was not found.".format(supplier_id))
        supplier.deserialize(request.get_json())
        supplier.id = supplier_id
        supplier.save()
        return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

    #------------------------------------------------------------------
    # DELETE A SUPPLIER
    #------------------------------------------------------------------
    @api.doc('delete_suppliers', security='apikey')
    @api.response(204, 'Supplier deleted')
    @token_required
    @app.route("/suppliers/<int:supplier_id>", methods=["DELETE"])
    
    def delete_suppliers(supplier_id):
        """
        Delete a Supplier
        This endpoint will delete a Supplier based the id specified in the path
        """
        app.logger.info("Request to delete supplier with id: %s", supplier_id)
        suppliers = Supplier.find(supplier_id)
        if suppliers:
            suppliers.delete()
        return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  PATH: /suppliers
######################################################################
@api.route('/suppliers', strict_slashes=False)
class SupplierCollection(Resource):
    """ Handles all interactions with collections of Suppliers """

    #------------------------------------------------------------------
    # LIST ALL SUPPLIERS
    #------------------------------------------------------------------
    @api.doc('list_suppliers')
    @api.expect(supplier_args, validate=True)
    @api.marshal_list_with(supplier_model)
    @app.route("/suppliers", methods=["GET"])
    def list_suppliers():
        """ Returns all of the suppliers """
        app.logger.info("Request for Supplier list")
        suppliers = []
        name = request.args.get("name")
        category = request.args.get("category")
        
        if name:
            suppliers = Supplier.find_by_name(name)
        elif category: 
            suppliers = Supplier.find_by_category(category)
        else:
            suppliers = Supplier.all()

        results = [supplier.serialize() for supplier in suppliers]
        return make_response(jsonify(results), status.HTTP_200_OK)

    #------------------------------------------------------------------
    # ADD A NEW SUPPLIER
    #------------------------------------------------------------------
    @api.doc('create_suppliers', security='apikey')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Supplier created successfully')
    @api.marshal_with(supplier_model, code=201)
    @token_required
    @app.route("/suppliers", methods=["POST"])
    def create_suppliers():
        """
        Creates a Supplier
        This endpoint will create a Supplier based the data in the body that is posted
        """
        app.logger.info("Request to create a Supplier")
        check_content_type("application/json")
        supplier = Supplier()
        supplier.deserialize(request.get_json())
        supplier.create()
        message = supplier.serialize()
        location_url = url_for("get_suppliers", supplier_id=supplier.id, _external=True)
        return make_response(
            jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
        )

######################################################################
#  PATH: /suppliers/{id}/purchase
######################################################################
@api.route('/suppliers/<supplier_id>/purchase')
@api.param('supplier_id', 'The Supplier identifier')
class PurchaseResource(Resource):
    """ Purchase actions on a Supplier """
    @api.doc('purchase_suppliers')
    @api.response(404, 'Supplier not found')
    @api.response(409, 'The Supplier is not available for purchase')

    @app.route('/suppliers/<int:supplier_id>/preferred', methods=['PUT'])
    def preferred_suppliers(supplier_id):
        """ Marking a supplier preferred """
        supplier = Supplier.find(supplier_id)
        if not supplier:
            abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id)) 
        supplier.preferred = "true"
        supplier.save()
        return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE ALL SUPPLIER DATA (for testing only)
######################################################################
@app.route("/suppliers/reset", methods=["DELETE"])
def delete_all_suppliers():
    """ Returns IDs of the Suppliers """
    app.logger.info("Request for Supplier list")
    suppliers = []
    id = request.args.get("id")
    if id:
        suppliers = Supplier.find(id)
    else:
        suppliers = Supplier.all()

    results = [supplier.delete() for supplier in suppliers]
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    #return (
    #    jsonify(
    #        name="Suppliers REST API Service",
    #        version="1.0",
    #        paths=url_for("list_suppliers", _external=True),
    #    ),
    #    status.HTTP_200_OK,
    #)
    return app.send_static_file('index.html')



######################################################################
# RETRIEVE A SUPPLIER'S PRODUCTS
######################################################################
@app.route("/suppliers/<int:supplier_id>/products" , methods=["GET"])  #subordinate call
def get_suppliers_products(supplier_id):
    """
    Retrieve a single Supplier's prpoducts
    This endpoint will return a Supplier's products based on Supplier's id
    """
    app.logger.info("Request for Supplier's products for id: %s", supplier_id)
    supplier = Supplier.find_or_404(supplier_id)
    results = supplier.products
    products = [product.serialize() for product in results]
    return make_response(jsonify(products), status.HTTP_200_OK)









#---------------------------------------------------------------------
#                P R O D U C T S   M E T H O D S
#---------------------------------------------------------------------

######################################################################
# ADD AN ADDRESS TO AN ACCOUNT
######################################################################
@app.route('/suppliers/<int:supplier_id>/products', methods=['POST'])
def create_products(supplier_id):
    """
    Create a Product on a Supplier

    This endpoint will add a product to a supplier
    """
    app.logger.info("Request to add an product to an supplier")
    check_content_type("application/json")
    supplier = Supplier.find_or_404(supplier_id)
    product = Product()
    product.deserialize(request.get_json())
    supplier.products.append(product)
    supplier.save()
    message = product.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)

#####################################################################
# RETRIEVE A PRODUCT FROM SUPPLIER
######################################################################
@app.route('/suppliers/<int:supplier_id>/products/<int:product_id>', methods=['GET'])
def get_products(supplier_id, product_id):
    """
    Get a Product

    This endpoint returns just a product
    """
    app.logger.info("Request to get a product with id: %s", product_id)
    product = Product.find_or_404(product_id)
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/suppliers/<int:supplier_id>/products/<int:product_id>", methods=["PUT"])
def update_products(supplier_id, product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update product with id: %s", product_id)
    check_content_type("application/json")
    product = Product.find_or_404(product_id)
    product.deserialize(request.get_json())
    product.id = product_id
    product.save()
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
@app.before_first_request
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Supplier.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))

# load sample data
def data_load(payload):
    """ Loads a Supplier into the database """
    supplier = Supplier(payload['name'], payload['category'], payload['available'])
    supplier.save()

def data_reset():
    """ Removes all Suppliers from the database """
    Supplier.remove_all()
