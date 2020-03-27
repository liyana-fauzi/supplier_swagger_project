"""
Supplier API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.models import db
from service.service import app, init_db
from tests.factories import SupplierFactory, ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ Supplier REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ Runs once before test suite """
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ Runs once after each test case """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_suppliers(self, count):
        """ Factory method to create suppliers in bulk """
        suppliers = []
        for _ in range(count):
            supplier = SupplierFactory()
            resp = self.app.post(
                "/suppliers", json=supplier.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Supplier"
            )
            new_supplier = resp.get_json()
            supplier.id = new_supplier["id"]
            suppliers.append(supplier)
        return suppliers

######################################################################
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_supplier_list(self):
        """ Get a list of suppliers """
        self._create_suppliers(5)
        resp = self.app.get("/suppliers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_supplier_by_name(self):
        """ Get a supplier by Name """
        suppliers = self._create_suppliers(3)
        resp = self.app.get("/suppliers?name={}".format(suppliers[1].name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], suppliers[1].name)

    def test_get_supplier(self):
        """ Get a single supplier """
        # get the id of an supplier
        supplier = self._create_suppliers(1)[0]
        resp = self.app.get(
            "/suppliers/{}".format(supplier.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], supplier.name)

    def test_get_supplier_not_found(self):
        """ Get an supplier that is not found """
        resp = self.app.get("/suppliers/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
       
    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_supplier(self):
        """ Create a new Supplier """
        supplier = SupplierFactory()
        resp = self.app.post(
            "/suppliers", 
            json=supplier.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        app.logger.debug(location)
        
        # Check the data is correct
        new_supplier = resp.get_json()
        self.assertEqual(new_supplier["name"], supplier.name, "Name does not match")
        self.assertEqual(new_supplier["category"], supplier.category, "Category does not match")
        self.assertEqual(new_supplier["address"], supplier.address, "Address does not match")
        self.assertEqual(new_supplier["email"], supplier.email, "Email does not match")
        self.assertEqual(new_supplier["phone_number"], supplier.phone_number, "Phone does not match")
        self.assertEqual(new_supplier["products"], supplier.products, "Products does not match")

        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_supplier = resp.get_json()
        self.assertEqual(new_supplier["name"], supplier.name, "Names does not match")
        self.assertEqual(new_supplier["category"], supplier.category, "Category does not match")
        self.assertEqual(new_supplier["address"], supplier.address, "Address does not match")
        self.assertEqual(new_supplier["email"], supplier.email, "Email does not match")
        self.assertEqual(new_supplier["phone_number"], supplier.phone_number, "Phone does not match")
        self.assertEqual(new_supplier["products"], (supplier.products), "Products does not match")

    def test_update_supplier(self):
        """ Update an existing Supplier """
        # create a supplier to update
        test_supplier = SupplierFactory()
        resp = self.app.post(
            "/suppliers", json=test_supplier.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the supplier
        new_supplier = resp.get_json()
        new_supplier["category"] = "unknown"
        resp = self.app.put(
            "/suppliers/{}".format(new_supplier["id"]),
            json=new_supplier,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_supplier = resp.get_json()
        self.assertEqual(updated_supplier["category"], "unknown")

    def test_delete_supplier(self):
        """ Delete a Supplier """
        test_supplier = self._create_suppliers(1)[0]
        resp = self.app.delete(
            "/suppliers/{}".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/suppliers/{}".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_request(self):
        """ Send wrong media type """
        supplier = SupplierFactory()
        resp = self.app.post(
            "/suppliers", 
            json={"name": "not enough data"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """ Send wrong media type """
        supplier = SupplierFactory()
        resp = self.app.post(
            "/suppliers", 
            json=supplier.serialize(), 
            content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """ Make an illegal method call """
        resp = self.app.put(
            "/suppliers", 
            json={"not": "today"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
######################################################################
#  A D D R E S S   T E S T   C A S E S
######################################################################

    def test_add_product(self):
        """ Add an product to a supplier """
        supplier = self._create_suppliers(1)[0]
        product = ProductFactory()
        resp = self.app.post(
            "/suppliers/{}/products".format(supplier.id), 
            json=product.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["supplier_id"], supplier.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["desc"], product.desc)
        self.assertEqual(data["wholesale_price"], product.wholesale_price)
        self.assertEqual(data["quantity"], product.quantity)
        
    
    def test_update_products(self):
        """ Update a product on a supplier """
        # create a known product
        supplier = self._create_suppliers(1)[0]
        product = ProductFactory()
        resp = self.app.post(
            "/suppliers/{}/products".format(supplier.id), 
            json=product.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        product_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.app.put(
            "/suppliers/{}/products/{}".format(supplier.id, product_id), 
            json=data, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.app.get(
            "/suppliers/{}/products/{}".format(supplier.id, product_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["supplier_id"], supplier.id)
        self.assertEqual(data["name"], "XXXX")
