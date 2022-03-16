from playerstars_interactors.utils.pagination_utils import PartialPagination


def test_partial_pagination_to_json():
    partial_pagination = PartialPagination(1, 5, 50, 'duel')
    partial_pagination_json = partial_pagination.to_json()
    assert partial_pagination_json == {
        'initial': 1,
        'final': 5,
        'total': 50,
        'unit': 'duel'}
