"""
Supplier Service with Swagger

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
import logging
#from functools import wraps
from flask import Flask, jsonify, request, url_for, make_response, abort, render_template
from flask_api import status  # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Supplier, DataValidationError, Product

# Import Flask application
from . import app

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
         version='1.0.0',
         title='Supplier Demo REST API Service',
         description='This is the API documentation for the Suppliers Resource.',
         default='Suppliers',
         default_label='Everything About Suppliers',
         doc='/apidocs', # default also could use doc='/apidocs/'
          #authorizations=authorizations,
         prefix='/api'
        )

#Define the model so that the docs reflect what can be sent
supplier_model = api.model('Supplier', {
    '_id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'category': fields.String(required=True,
                              description='The category of Supplier (e.g., furnishing, home & beauty etc.)'),
    'preferred': fields.Boolean(required=True,
                                description='Is the Supplier preferred?')
})

create_model = api.model('Supplier', {
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'category': fields.String(required=True,
                              description='The category of Supplier (e.g., furnishing, home & beauty etc.)'),
    'preferred': fields.Boolean(required=True,
                                description='Is the Supplier preferred?')
})

# # query string arguments
supplier_args = reqparse.RequestParser()
supplier_args.add_argument('name', type=str, required=False, help='List Suppliers by name')
supplier_args.add_argument('category', type=str, required=False, help='List Suppliers by category')
supplier_args.add_argument('preferred', type=inputs.boolean, required=False, help='List Suppliers by preferred')


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
    #------------------------------------------------------------------
    @api.doc('get_suppliers')
    @api.response(404, 'Supplier not found')
    @api.marshal_with(supplier_model)
    def get(self, supplier_id):
        """
        Retrieve a single Supplier

        This endpoint will return a Supplier based on it's id
        """
        app.logger.info("Request to Retrieve a supplier with id [%s]", supplier_id)
        supplier = Supplier.find(supplier_id)
        if not supplier:
            api.abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id))
        return supplier.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A SUPPLIER
    #------------------------------------------------------------------
    @api.doc('delete_suppliers')#, security='apikey')
    @api.response(204, 'Supplier deleted')
    #@token_required
    def delete(self, supplier_id):
        """
        Delete a Supplier

        This endpoint will delete a Supplier based the id specified in the path
        """
        app.logger.info('Request to Delete a supplier with id [%s]', supplier_id)
        supplier = Supplier.find(supplier_id)
        if supplier:
            supplier.delete()
        return '', status.HTTP_204_NO_CONTENT

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
    def get(self):
        """ Returns all of the Suppliers """
        app.logger.info('Request to list Suppliers...')
        suppliers = []
        args = supplier_args.parse_args()
        if args['category']:
            app.logger.info('Filtering by category: %s', args['category'])
            suppliers = Supplier.find_by_category(args['category'])
        elif args['name']:
            app.logger.info('Filtering by name: %s', args['name'])
            suppliers = Supplier.find_by_name(args['name'])
        elif args['preferred'] is not None:
            app.logger.info('Filtering by preferred: %s', args['preferred'])
            suppliers = Supplier.find_by_preferred(args['preferred'])
        else:
            suppliers = Supplier.all()

        app.logger.info('[%s] Suppliers returned', len(suppliers))
        results = [supplier.serialize() for supplier in suppliers]
        return results, status.HTTP_200_OK


    #------------------------------------------------------------------
    # ADD A NEW SUPPLIER
    #------------------------------------------------------------------
    @api.doc('create_suppliers')#, security='apikey')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Supplier created successfully')
    @api.marshal_with(supplier_model, code=201)
    #@token_required
    def post(self):
        """
        Creates a Supplier
        This endpoint will create a Supplier based the data in the body that is posted
        """
        app.logger.info('Request to Create a Supplier')
        supplier = Supplier()
        app.logger.debug('Payload = %s', api.payload)
        supplier.deserialize(api.payload)
        supplier.create()
        app.logger.info('Supplier with new id [%s] saved!', supplier.id)
        location_url = api.url_for(SupplierResource, supplier_id=supplier.id, _external=True)
        return supplier.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /suppliers/{id}/preferred
######################################################################
@api.route('/suppliers/<supplier_id>/preferred')
@api.param('supplier_id', 'The Supplier identifier')
class PreferredResource(Resource):
    """ Preferred actions on a Supplier """
    @api.doc('preferred_suppliers')
    @api.response(404, 'Supplier not found')
    @api.response(409, 'The Supplier is not preferred')
    def put(self, supplier_id):
        """
        Preferred a Supplier

        This endpoint will make the Supplier a preferred supplier
        """
        app.logger.info('Request to Preferred a Supplier')
        supplier = Supplier.find(supplier_id)
        if not supplier:
            api.abort(status.HTTP_404_NOT_FOUND, 'Supplier with id [{}] was not found.'.format(supplier_id))
        if not supplier.preferred:
            api.abort(status.HTTP_409_CONFLICT, 'Supplier with id [{}] is not preferred.'.format(supplier_id))
        supplier.preferred = False
        supplier.save()
        app.logger.info('Supplier with id [%s] has been preferredd!', supplier.id)
        return supplier.serialize(), status.HTTP_200_OK

######################################################################
# DELETE ALL SUPPLIER DATA (for testing only)
######################################################################
@app.route('/suppliers/reset', methods=['DELETE'])
def suppliers_reset():
    """ Removes all suppliers from the database """
    Supplier.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

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
    supplier = Supplier(payload['name'], payload['category'], payload['preferred'])
    supplier.save()

def data_reset():
    """ Removes all Suppliers from the database """
    Supplier.remove_all()