# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
import factory
from datetime import datetime
from factory.fuzzy import FuzzyChoice
from service.models import Supplier, Product


class ProductFactory(factory.Factory):
    """ Creates fake Product """

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
#    supplier_id = ???
    #use random faker providers (company, text, pyint) to generate product attributes
    name = factory.Faker("company")
    desc = factory.Faker("text")
    wholesale_price = factory.Faker("pyint")
    quantity = factory.Faker("pyint")

class SupplierFactory(factory.Factory):
    """ Creates fake Supplier """

    class Meta:
        model = Supplier

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    category = FuzzyChoice(choices=["apparel", "health & beauty", "home furnishings", "other"])
    address = factory.Faker("address")
    email = factory.Faker("email")
    phone_number = factory.Faker("phone_number")
    preferred = FuzzyChoice(choices=["True", "False"])
    