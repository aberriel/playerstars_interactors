from clapy_basic_classes import BasicEntity
from playerstars_interactors.utils.pagination_utils import \
    get_page_list, get_partial_range
from typing import List
import json


class BasicGetAllRequestModel:
    def __init__(self, params):
        self.pagination_page = int(params.get('pagination_page', 1))
        self.pagination_per_page = int(params.get('pagination_per_page', 10))
        self.sort_field = params.get('sort_field')
        self.sort_order = params.get('sort_order')
        self.filter_param = params.get('param', None)


class BasicGetAllResponseModel:
    def __init__(self, entities: List[BasicEntity], range_data=None):
        self.entities: List[BasicEntity] = entities
        self.range_data = range_data

    def __call__(self):
        if self.range_data:
            return [x.to_json() for x in self.entities], self.range_data
        return [x.to_json() for x in self.entities]


class BasicGetAllInteractor:
    def __init__(self, adapter_instance, request, paginate=False, sort=False):
        self.adapter_instance = adapter_instance
        self.paginate = paginate
        self.request = request
        self.sort = sort

    def filter_entity(self):
        kwargs = json.loads(self.request.filter_param)
        entity_list = self.adapter_instance.filter(**kwargs)
        if self.paginate:
            return self.paginate_entity(entity_list)
        return BasicGetAllResponseModel(entity_list, None)

    def paginate_entity(self, entity_list):
        page_list = get_page_list(
            self.request.pagination_page, self.request.pagination_per_page,
            entity_list)
        range_data = get_partial_range(
            entity_list, self.request.pagination_page,
            self.request.pagination_per_page, 'ranking')
        return BasicGetAllResponseModel(page_list, range_data)

    def sort_list(self, _list):
        return sorted(
            _list,
            key=lambda x: getattr(x, self.request.sort_field),
            reverse=self.request.sort_order == 'DESC')

    def run(self):
        if self.request and self.request.filter_param:
            response = self.filter_entity()
            return response()

        entity_list: List[BasicEntity] = self.adapter_instance.list_all()

        if self.sort:
            entity_list = self.sort_list(entity_list)
        if self.paginate:
            response = self.paginate_entity(entity_list)
            return response()

        response = BasicGetAllResponseModel(entity_list, None)
        return response()
