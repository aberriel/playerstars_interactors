from playerstars_interactors import GetAllProductsInteractor
from playerstars_domain import Product
from playerstars_adapters import ProductAdapter
from unittest.mock import patch


product1 = Product.from_json({
    "entity_id": "58466b43-d840-47ac-8577-0518ff80d5f7",
    "star_value": 600,
    "star_type": "red",
    "price": 18000,
    "description": "6 meses red star",
    "duration": 3
})
product2 = Product.from_json({
    "entity_id": "162d56b3-a970-4808-89da-5acce327afba",
    "star_value": 20,
    "star_type": "gold",
    "price": 10000,
    "description": "20 stars gold",
    "duration": 0
})

product3 = Product.from_json({
    "entity_id": "36500f04-2291-4ca5-8af9-24cc2b687b96",
    "star_value": 70,
    "star_type": "gold",
    "price": 30000,
    "description": "70 stars gold",
    "duration": 0
})
product4 = Product.from_json({
    "entity_id": "6b1a2404-77ec-494d-97f8-dee7ad7c54b6",
    "star_value": 130,
    "star_type": "gold",
    "price": 50000,
    "description": "130 stars gold",
    "duration": 0
})
product5 = Product.from_json({
    "entity_id": "b8ed84a3-a5ee-430f-86dc-33344a78ed3b",
    "star_value": 300,
    "star_type": "red",
    "price": 12000,
    "description": "3 meses red star",
    "duration": 3
})
list_products = [product1, product2, product3, product4, product5]

expected_response = {
    'red': [product1.to_json(), product5.to_json()],
    'gold': [product2.to_json(), product3.to_json(), product4.to_json()]
}


@patch.object(ProductAdapter, 'list_all', return_value=list_products)
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_all_product(resource, table, list_all):
    adapter = ProductAdapter('product-test', 'localhost-test')
    interactor = GetAllProductsInteractor(adapter)
    response = interactor.run()
    assert response == expected_response
