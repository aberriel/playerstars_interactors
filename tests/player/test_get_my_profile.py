from playerstars_interactors import (
    GetProfileInteractor, GetProfileRequestModel)
from tests.player.profile_utils import expected_profile_json_response
from tests.util_tests import player_1, duel_list, team_list, console_by_id
from unittest.mock import patch, MagicMock


player_adapter = MagicMock(get_by_id=MagicMock(return_value=player_1))
duel_adapter = MagicMock(list_all=MagicMock(return_value=duel_list))
team_adapter = MagicMock(list_all=MagicMock(return_value=team_list))
console_adapter = MagicMock(get_by_id=MagicMock(return_value=console_by_id))


@patch('boto3.resource')
def test_get_my_profile(boto_resource):
    request = GetProfileRequestModel('8f547626-d1f7-49a3-ba2e-eb7a7504ad22')
    interactor = GetProfileInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter,
        duel_adapter=duel_adapter,
        console_adapter=console_adapter)
    result = interactor.run()
    assert result == expected_profile_json_response
