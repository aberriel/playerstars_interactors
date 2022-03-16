from playerstars_interactors import GetPlanListInteractor


def make_plan_list():
    return [
        {
            'code': 'red1month',
            'amount': 1990,
            'period': 1
        },
        {
            'code': 'red3month',
            'amount': 5670,
            'period': 3
        },
        {
            'code': 'red6month',
            'amount': 10745,
            'period': 6
        },
        {
            'code': 'red1year',
            'amount': 20298,
            'period': 12
        }
    ]


def test_get_plan_list():
    interactor = GetPlanListInteractor()
    plan_list = interactor.run()
    assert plan_list == make_plan_list()
