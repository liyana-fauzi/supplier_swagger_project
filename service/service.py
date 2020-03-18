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
from service.models import Suppliers, DataValidationError, Products

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return "Reminder: return some useful information in json format about the service here", status.HTTP_200_OK


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
    supplier = Suppliers()
    supplier.deserialize(request.get_json())
    supplier.create()
    message = supplier.serialize()
    #TODO: when get_suppliers (READ SUPPLIER) is implemented , remove the commented code below
    #location_url = url_for("get_suppliers", supplier_id=supplier.id, _external=True)
    location_url = "not implemented"
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Suppliers.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))
