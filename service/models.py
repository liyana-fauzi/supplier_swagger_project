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

class DatabaseConnectionError(Exception):
    """ Custom Exception when database connection fails """
    pass

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase():
    """ Base class added persistent methods """

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
        """ Returns all of the Supplier in the database """
        logger.info("Processing all Supplier")
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


######################################################################
#  P R O D U C T S   M O D E L
######################################################################

class Product(db.Model, PersistentBase):
    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    desc = db.Column(db.String(256))
    wholesale_price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    supplier_id = db.Column(db.Integer, db.ForeignKey('Supplier.id'), nullable = False)
    
 
    def __repr__(self):
        return "<product %r id=[%s]>" % (self.name, self.id)

    def __str__(self):
        return "%s: %s, %s, %s %s" % (self.name, self.street, self.city, self.state, self.postalcode)

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "name": self.name,
            "desc": self.desc,
            "wholesale_price": self.wholesale_price,
            "quantity": self.quantity,
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.supplier_id = data["supplier_id"]
            self.name = data["name"]
            self.desc = data["desc"]
            self.wholesale_price = data["wholesale_price"]
            self.quantity = data["quantity"]
            
        except KeyError as error:
            raise DataValidationError("Invalid Product: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained" "bad or no data"
            )
        return self


#####################################################################
#  S U P P L I E R S   M O D E L
######################################################################


class Supplier(db.Model, PersistentBase):

    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    __tablename__ = 'Supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
    address = db.Column(db.String(128))
    email = db.Column(db.String(63))
    phone_number = db.Column(db.String(32))
    preferred = db.Column(db.String(32))
    products = relationship('Product', order_by = Product.id, backref=db.backref('Supplier'), lazy=True)


    def __repr__(self):
        return "<supplier %r id=[%s]>" % (self.name, self.id)

    def serialize(self):
        """ Serializes a Supplier into a dictionary """
        supplier = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "address":self.address,
            "email":self.email,
            "phone_number":self.phone_number,
            "preferred":self.preferred,
            "products": []
        }
        for product in self.products:
            supplier['products'].append(product.serialize())
        return supplier

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
            self.preferred = data.get("preferred")
            #handle inner list of products
            product_list = data["products"]
            for json_product in product_list:
                product = Product()
                product.deserialize(json_product)
                self.products.append(product)

            
        except KeyError as error:
            raise DataValidationError("Invalid Supplier: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Supplier: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def find_by_name(cls, name):
        """ Returns all Supplier with the given name

        Args:
            name (string): the name of the Supplier you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    #whoever is doing the query story should create more query model

    @classmethod
    def find_by_category(cls, category):
        """ Returns all Suppliers with the given category

        Args:
            category (string): the category of the Suppliers you want to match
        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def find_by_address(cls, address):
        """ Returns all Suppliers with the given address

        Args:
            address (string): the address of the Suppliers you want to match
        """
        logger.info("Processing address query for %s ...", address)
        return cls.query.filter(cls.address == address)

    @classmethod
    def find_by_email(cls, email):
        """ Returns all Suppliers with the given email

        Args:
            email (string): the email of the Suppliers you want to match
        """
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_phone_number(cls, phone_number):
        """ Returns all Suppliers with the given phone_number

        Args:
            phone_number (string): the phone_number of the Suppliers you want to match
        """
        logger.info("Processing phone_number query for %s ...", phone_number)
        return cls.query.filter(cls.phone_number == phone_number) 

    @classmethod
    def find_by_preferred(cls, preferred):
        """ Returns all Suppliers with the preferred flag set

        Args:
            preferred (boolean): the preferred flag of the Suppliers you want to match
        """
        logger.info("Processing preferred flag query for %s ...", preferred)
        return cls.query.filter(cls.preferred == preferred) 