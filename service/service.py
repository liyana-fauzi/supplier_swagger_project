"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Supplier, DataValidationError, Product

# Import Flask application
from . import app

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

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Suppliers REST API Service",
            version="1.0",
            paths=url_for("list_suppliers", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL suppliers
######################################################################
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

######################################################################
# RETRIEVE A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["GET"])
def get_suppliers(supplier_id):
    """
    Retrieve a single Supplier
    This endpoint will return a Supplier based on it's id
    """
    app.logger.info("Request for Supplier with id: %s", supplier_id)
    supplier = Supplier.find_or_404(supplier_id)
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

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

######################################################################
# CREATE A NEW SUPPLIER
######################################################################
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
# UPDATE AN EXISTING SUPPLIER
######################################################################
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

######################################################################
# DELETE A SUPPLIER
######################################################################
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
# MARK A PREFERRED SUPPLIER
######################################################################
@app.route('/suppliers/<int:supplier_id>/preferred', methods=['PUT'])
def preferred_suppliers(supplier_id):
    """ Marking a supplier preferred """
    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id)) 
    supplier.preferred = "True"
    supplier.save()
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

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
