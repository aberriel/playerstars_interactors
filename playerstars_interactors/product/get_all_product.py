from playerstars_domain import Product
from typing import List


class GetAllProductsResponseModel:
    def __init__(self, products: List[Product]):
        self.products = products

    def __call__(self):
        gold_products = [product.to_json() for product in self.products if
                         product.star_type == 'gold']
        red_products = [product.to_json() for product in self.products if
                        product.star_type == 'red']
        return {
            'red': red_products,
            'gold': gold_products
        }


class GetAllProductsInteractor:
    def __init__(self, adapter_instance):
        self.adapter_instance = adapter_instance

    def run(self):
        product_list: List[Product] = self.adapter_instance.list_all()
        response = GetAllProductsResponseModel(product_list)
        return response()
