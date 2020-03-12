"""
Models for Supplier

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Products(db.Model):
    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    desc = db.Column(db.String(256))
    wholesale_price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    supplier_id = db.Column(db.Integer, db.ForeignKey('Suppliers.id'), nullable = False)
    
 
    def __repr__(self):
        return "<product %r id=[%s]>" % (self.name, self.id)


class Suppliers(db.Model):
    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    __tablename__ = 'Suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
    address = db.Column(db.String(128))
    email = db.Column(db.String(63))
    phone_number = db.Column(db.String(12))
    product_list = relationship('Products', order_by = Products.id, backref=db.backref('supplier_id'))


    def __repr__(self):
        return "<supplier %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Supplier to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Supplier to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Supplier from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Supplier into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "address":self.address,
            "email":self.email,
            "phone_number":self.phone_number,
            "product_list":self.product_list
        }

    def deserialize(self, data):
        """
        Deserializes a Supplier from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.category = data["category"]
            self.address = data["address"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.product_list = data["product_list"]
        except KeyError as error:
            raise DataValidationError("Invalid Supplier: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Supplier: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Suppliers in the database """
        logger.info("Processing all Suppliers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Supplier by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Supplier by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all Suppliers with the given name

        Args:
            name (string): the name of the Suppliers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    #whoever is doing the query story should create more query model
