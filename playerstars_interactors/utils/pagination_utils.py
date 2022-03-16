def get_page_list(page, per_page, response):
    if len(response) > per_page:
        initial = (page - 1) * per_page
        final = initial + per_page
        response = response[initial:final]
        return response
    return response


class PartialPagination:
    def __init__(self, initial, final, total, unit):
        self.initial = initial
        self.final = final
        self.total = total
        self.unit = unit

    def to_json(self):
        return {
            'initial': self.initial,
            'final': self.final,
            'total': self.total,
            'unit': self.unit}


def get_partial_range(full_list, page, per_page, unit):
    if not full_list:
        return PartialPagination(0, 0, 0, unit)
    total = len(full_list)
    initial = (page - 1) * per_page
    final = initial + per_page
    if final > total:
        final = total
    return PartialPagination(initial, final, total, unit)
