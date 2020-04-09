"""
Test cases for Supplier Model

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Supplier, Product, DataValidationError, db
from service import app
from tests.factories import SupplierFactory, ProductFactory


DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

######################################################################
#  S U P P L I E R S   M O D E L   T E S T   C A S E S
######################################################################
class TestSupplier(unittest.TestCase):
    """ Test Cases for Supplier Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Supplier.init_db(app)

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
        supplier = Supplier(
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
        product = Product(
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
        supplier = Supplier(
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
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = self._create_supplier()
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

    def test_add_supplier_product(self):
        """ Create a Supplier with a product and add it to the database """
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = self._create_supplier()
        product = self._create_product()
        supplier.products.append(product)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

        new_supplier = Supplier.find(supplier.id)
        self.assertEqual(supplier.products[0].name, product.name)

        product2 = self._create_product()
        supplier.products.append(product2)
        supplier.save()

        new_supplier = Supplier.find(supplier.id)
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
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].id, 1)
        self.assertEqual(suppliers[0].category, "suppliers")

    def test_delete_a_supplier(self):
        """ Delete a Supplier """
        supplier = SupplierFactory()
        supplier.create()
        self.assertEqual(len(Supplier.all()), 1)
        # delete the supplier and make sure it isn't in the database
        supplier.delete()
        self.assertEqual(len(Supplier.all()), 0)

    def test_find_or_404(self):
        """ Find or throw 404 error """
        supplier = self._create_supplier()
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)

        # Fetch it back
        supplier = Supplier.find_or_404(supplier.id)
        self.assertEqual(supplier.id, 1)


    def test_update_supplier_product(self):
        """ Update an suppliers product """
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])

        product = self._create_product()
        supplier = self._create_supplier(products=[product])
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(supplier.id, 1)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

        # Fetch it back
        supplier = Supplier.find(supplier.id)
        old_product = supplier.products[0]
        self.assertEqual(old_product.desc, product.desc)

        old_product.desc = "XX"
        supplier.save()

        # Fetch it back again
        supplier = Supplier.find(supplier.id)
        product = supplier.products[0]
        self.assertEqual(product.desc, "XX")

    def test_find_supplier(self):
        """ Find a Supplier by ID """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        logging.debug(suppliers)
        # make sure they got saved
        self.assertEqual(len(Supplier.all()), 3)
        # find the 2nd supplier in the list
        supplier = Supplier.find(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)
        self.assertEqual(supplier.category, suppliers[1].category)
        self.assertEqual(supplier.email, suppliers[1].email)
        self.assertEqual(supplier.address, suppliers[1].address)
        self.assertEqual(supplier.phone_number, suppliers[1].phone_number)

    def test_find_by_category(self):
        """ Find Suppliers by Category """
        suppliers = SupplierFactory.create_batch(3)
        suppliers[0].category="home furnishings"
        suppliers[0].create()
        suppliers[1].category="health & beauty"
        suppliers[1].create()
        suppliers[2].category="health & beauty"
        suppliers[2].create()
        results = Supplier.find_by_category("health & beauty")
        logging.debug(results)
        self.assertNotEqual(results, [])   
        self.assertEqual(results[0].category, "health & beauty")


    def test_find_by_name(self):
        """ Find a Supplier by Name """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        results = Supplier.find_by_name(suppliers[0].name)
        self.assertNotEqual(results, [])        
        self.assertEqual(results[0].name, suppliers[0].name)
        
   
    def test_find_by_address(self):
        """ Find Suppliers by address """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        results = Supplier.find_by_address(suppliers[0].address)
        self.assertNotEqual(results, [])
        self.assertEqual(results[0].address, suppliers[0].address)


    def test_find_by_email(self):
        """ Find Suppliers by email """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        results = Supplier.find_by_email(suppliers[0].email)
        self.assertNotEqual(results, [])   
        self.assertEqual(results[0].email, suppliers[0].email)

    def test_find_by_phone_number(self):
        """ Find Suppliers by phone_number """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        results = Supplier.find_by_phone_number(suppliers[0].phone_number)
        self.assertNotEqual(results, [])   
        self.assertEqual(results[0].phone_number, suppliers[0].phone_number)

    def test_find_or_404_found(self):
        """ Find or return 404 found """
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()

        supplier = Supplier.find_or_404(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)
       
    def test_find_or_404_not_found(self):
        """ Find or return 404 NOT found """
        self.assertRaises(NotFound, Supplier.find_or_404, 0)
    

