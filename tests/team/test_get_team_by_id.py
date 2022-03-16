from playerstars_interactors import GetTeamInteractor, GetTeamRequestModel
from unittest.mock import MagicMock
from tests.util_tests import team_1, player_1, make_console_data
from datetime import datetime


team_1.creation_datetime = datetime(
    2019, 10, 11, 16, 50, 9, 956180)
team_adapter = MagicMock(get_by_id=MagicMock(return_value=team_1))
player_adapter = MagicMock(get_by_id=MagicMock(return_value=player_1))
console_adapter = MagicMock(get_by_id=MagicMock(
    return_value=make_console_data()))


def test_get_team():
    request = GetTeamRequestModel('team_id')
    interactor = GetTeamInteractor(
        request, team_adapter, player_adapter, console_adapter)
    response = interactor.run()
    assert response == {
        "victories": 0,
        "name": "brazucas1",
        "elo_rating": 1500.0,
        "entity_id": "fe5c6aea-6928-4008-a08d-f90440983dd4",
        "members": [{
            "player_id": "8f547626-d1f7-49a3-ba2e-eb7a7504ad22",
            "bet_amount": 100,
            "association_date": "2019-10-11T16:50:09.937668+00:00",
            "last_status_change_datetime": "2019-10-11T17:12:21.123456+00:00",
            "status": "ACCEPTED",
            "member_type": "CAPTAIN",
            "player_photo": None,
            "player_nickname": "Zyzukab",
        }, {
            "player_id": "7e436515-d1f7-49a3-ba2e-e43a7504ad22",
            "bet_amount": 100,
            "association_date": "2019-10-11T16:50:09.956180+00:00",
            "last_status_change_datetime": "2019-10-11T17:02:45.123456+00:00",
            "status": "ACCEPTED",
            "member_type": "MEMBER",
            "player_photo": None,
            "player_nickname": "Zyzukab"
        }],
        "creation_datetime": "2019-10-11T16:50:09.956180",
        "logo_path": None,
        "description": "TESTE TES TESTES",
        "captain": {
            "player_id": "8f547626-d1f7-49a3-ba2e-eb7a7504ad22",
            "bet_amount": 100,
            "association_date": "2019-10-11T16:50:09.937668+00:00",
            "last_status_change_datetime": "2019-10-11T17:12:21.123456+00:00",
            "status": "ACCEPTED",
            "member_type": "CAPTAIN"
        },
        "console_id": "531f6ee2-dfef-458e-b918-ebf12793fe37",
        "console_name": "Playstation 4",
        "game_id": "0e3bd0f7-e95c-4168-9083-f1859fa73902",
        "game_name": "Fifa 19",
        "status": "ACTIVE",
        "elo_rating": 1500.0
    }
