class GetPlanListInteractor:
    def __init__(self):
        pass

    def run(self):
        plan_list = [
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
        return plan_list
