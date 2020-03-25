"""
Test cases for Suppliers Model

"""
import logging
import unittest
import os
from service.models import Suppliers, Products, DataValidationError, db
from service import app
from tests.factories import SupplierFactory, ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  S U P P L I E R S   M O D E L   T E S T   C A S E S
######################################################################
class TestSuppliers(unittest.TestCase):
    """ Test Cases for Suppliers Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Suppliers.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_supplier(self, products=[]):
        """ Creates a supplier from a Factory """
        fake_supplier = SupplierFactory()
        supplier = Suppliers(
            name=fake_supplier.name, 
            category = fake_supplier.category,
            address = fake_supplier.address,
            email=fake_supplier.email, 
            phone_number=fake_supplier.phone_number, 
            products = products
        )
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
        return supplier

    def _create_product(self):
        """ Creates fake product from factory """
        fake_product = ProductFactory()
        product = Products(
            name=fake_product.name,
            desc=fake_product.desc,
            wholesale_price=fake_product.wholesale_price,
            quantity=fake_product.quantity
        )
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        return product

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_create_a_supplier(self):
        """ Create a Supplier and assert that it exists """
        fake_supplier = SupplierFactory()
        supplier = Suppliers(
            name=fake_supplier.name, 
            category = fake_supplier.category,
            address = fake_supplier.address,
            email=fake_supplier.email, 
            phone_number=fake_supplier.phone_number, 
            
        )
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, fake_supplier.name)
        self.assertEqual(supplier.address, fake_supplier.address)
        self.assertEqual(supplier.email, fake_supplier.email)
        self.assertEqual(supplier.phone_number, fake_supplier.phone_number)
        

    def test_add_a_supplier(self):
        """ Create a Supplier and add it to the database """
        suppliers = Suppliers.all()
        self.assertEqual(suppliers, [])
        supplier = self._create_supplier()
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)
        suppliers = Suppliers.all()
        self.assertEqual(len(suppliers), 1)

    def test_add_supplier_product(self):
        """ Create a Supplier with a product and add it to the database """
        suppliers = Suppliers.all()
        self.assertEqual(suppliers, [])
        supplier = self._create_supplier()
        product = self._create_product()
        supplier.products.append(product)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)
        suppliers = Suppliers.all()
        self.assertEqual(len(suppliers), 1)

        new_supplier = Suppliers.find(supplier.id)
        self.assertEqual(supplier.products[0].name, product.name)

        product2 = self._create_product()
        supplier.products.append(product2)
        supplier.save()

        new_supplier = Suppliers.find(supplier.id)
        self.assertEqual(len(supplier.products), 2)
        self.assertEqual(supplier.products[1].name, product2.name)
    

    def test_update_a_supplier(self):
        """ Update a Supplier """
        supplier = SupplierFactory()
        logging.debug(supplier)
        supplier.create()
        logging.debug(supplier)
        self.assertEqual(supplier.id, 1)
        # Change it an save it
        supplier.category = "suppliers"
        original_id = supplier.id
        supplier.save()
        self.assertEqual(supplier.id, original_id)
        self.assertEqual(supplier.category, "suppliers")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        suppliers = Suppliers.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].id, 1)
        self.assertEqual(suppliers[0].category, "suppliers")

    def test_delete_a_supplier(self):
        """ Delete a Supplier """
        supplier = SupplierFactory()
        supplier.create()
        self.assertEqual(len(Suppliers.all()), 1)
        # delete the supplier and make sure it isn't in the database
        supplier.delete()
        self.assertEqual(len(Suppliers.all()), 0)