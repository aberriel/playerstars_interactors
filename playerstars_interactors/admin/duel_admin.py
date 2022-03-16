from clapy_basic_classes import BasicEntity
from playerstars_domain import DuelMemberType
from typing import List
from playerstars_interactors.utils.pagination_utils import \
    get_page_list, get_partial_range


class GetAllDuelAdminRequestModel:
    def __init__(self, params):
        self.player_id = params.get('player_id')
        self.pagination_page = int(params.get('pagination_page', 1))
        self.pagination_per_page = int(params.get('pagination_per_page', 10))
        self.sort_field = params.get('sort_field')
        self.sort_order = params.get('sort_order')


class GetAllDuelAdminResponseModel:
    def __init__(self, entities: List[BasicEntity], range_data):
        self.entities: List[BasicEntity] = entities
        self.range_data = range_data

    def __call__(self):
        if self.range_data:
            return [x.to_json() for x in self.entities], self.range_data
        return [x.to_json() for x in self.entities]


class GetAllDuelAdminInteractor:
    def __init__(
            self, duel_adapter, request, duel_type,
            paginate=False, sort=False):
        self.duel_adapter = duel_adapter
        self.request = request
        self.duel_type = duel_type
        self.paginate = paginate
        self.sort = sort

    def paginate_entity(self, entity_list):
        page_list = get_page_list(
            self.request.pagination_page, self.request.pagination_per_page,
            entity_list)
        range_data = get_partial_range(
            entity_list, self.request.pagination_page,
            self.request.pagination_per_page, 'duel')
        return GetAllDuelAdminResponseModel(page_list, range_data)

    def sort_list(self, _list):
        return sorted(
            _list,
            key=lambda x: getattr(x, self.request.sort_field),
            reverse=self.request.sort_order == 'DESC')

    def filter_duel_list(self, entity_list):
        duel_type = DuelMemberType.PLAYER if self.duel_type == 'individual' \
            else DuelMemberType.TEAM
        filtered_duel_list = [x for x in entity_list if
                              x.member_type == duel_type]
        return filtered_duel_list

    def run(self):
        entity_list = self.duel_adapter.filter(
            challenger__eq=self.request.player_id,
            challenged__eq=self.request.player_id)
        duel_list = self.filter_duel_list(entity_list)
        if self.sort and self.request.sort_field and self.request.sort_order:
            duel_list = self.sort_list(duel_list)
        if self.paginate:
            response = self.paginate_entity(duel_list)
            return response()

        response = GetAllDuelAdminResponseModel(duel_list, None)
        return response()
