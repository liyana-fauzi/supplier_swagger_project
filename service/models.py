"""
Models for Suppliers

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Suppliers(db.Model):
    """
    Class that represents a Suppliers
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    address = db.Column(db.String(130))
    phone_number = db.Column(db.String(12))
    #remember to make phone_number optional

    def __repr__(self):
        return "<Suppliers %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Suppliers to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Suppliers to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Suppliers from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Suppliers into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "phone_number": self.phone_number,
        }

    def deserialize(self, data):
        """
        Deserializes a Suppliers from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.address = data["address"]
            self.phone_number = data.get("phone_number")
        except KeyError as error:
            raise DataValidationError("Invalid Suppliers: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Suppliers: body of request contained" "bad or no data"
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
        """ Returns all of the Supplierss in the database """
        logger.info("Processing all Supplierss")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Suppliers by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Suppliers by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all Supplierss with the given name

        Args:
            name (string): the name of the Supplierss you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    #whoever is doing the query story should create more query model
