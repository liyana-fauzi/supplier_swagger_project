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
from service.models import db, DataValidationError
from service.service import app, init_db
from tests.factories import SupplierFactory, ProductFactory
from urllib.parse import quote_plus


DATABASE_URI = os.getenv("DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres")
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

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
        self.assertEqual(new_supplier["products"], supplier.products, "Product does not match")

        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_supplier = resp.get_json()
        self.assertEqual(new_supplier["name"], supplier.name, "Names does not match")
        self.assertEqual(new_supplier["category"], supplier.category, "Category does not match")
        self.assertEqual(new_supplier["address"], supplier.address, "Address does not match")
        self.assertEqual(new_supplier["email"], supplier.email, "Email does not match")
        self.assertEqual(new_supplier["phone_number"], supplier.phone_number, "Phone does not match")
        self.assertEqual(new_supplier["products"], (supplier.products), "Product does not match")

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


    def test_mark_supplier_preference(self):
        """ Mark a Preferred Supplier (action test) """
        supplier = SupplierFactory.create_batch(1)
        supplier[0].name="Erlich Bachman"
        supplier[0].preferred="False"
        supplier[0].create()
        
        resp = self.app.get('/suppliers/{}'.format(supplier[0].id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        #Ensure that preferred flag is false prior to action
        self.assertEqual(data["preferred"], "False")

        resp = self.app.put('/suppliers/{}/preferred'.format(supplier[0].id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/suppliers/{}'.format(supplier[0].id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        #Ensure that preferred flag is set to True after action
        self.assertEqual(data["preferred"], "True")

######################################################################
#  P R O D U C T S   T E S T   C A S E S
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

    def test_get_supplier_products(self):
        """ Get all products from a supplier """
        supplier = self._create_suppliers(1)[0]
        products = ProductFactory.create_batch(3)
        for product in products:
            resp = self.app.post(
                "/suppliers/{}/products".format(supplier.id), 
                json=product.serialize(), 
                content_type="application/json"
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        #get products back
        resp = self.app.get(
            "/suppliers/{}/products".format(supplier.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(len(data), 3)
   
    
######################################################################
#  FIND  T E S T   C A S E S
######################################################################
    def test_query_supplier_list_by_category(self):
        """ Query Supplier by Category """
        suppliers = self._create_suppliers(10)
        test_category = suppliers[0].category
        category_suppliers = [supplier for supplier in suppliers if supplier.category == test_category]
        resp = self.app.get("/suppliers", query_string="category={}".format(quote_plus(test_category)))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(category_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier["category"], test_category)

    @patch('service.models.Supplier.find_by_name')
    def test_bad_request(self, bad_request_mock):
        """ Test a Bad Request error from Find By Name """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/suppliers', query_string='name=Aikeeya')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('service.models.Supplier.find_by_name')
    def test_mock_search_data(self, supplier_find_mock):
        """ Test showing how to mock data """
        supplier_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'Aikeeya'})]
        resp = self.app.get('/suppliers', query_string='name=fido')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

