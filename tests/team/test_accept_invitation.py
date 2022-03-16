from playerstars_adapters import TeamAdapter
from playerstars_domain import Team
from playerstars_interactors import (
    AcceptTeamInvitationInteractor, AcceptTeamInvitationException,
    AcceptTeamInvitationRequestModel
)
from unittest.mock import patch
import pytest
from tests.util_tests import team_json


request = AcceptTeamInvitationRequestModel({
    'player_id': 'idplayer12345',
    'team_id': 'idduel123',
    'accept_invite': True
})


team = Team.from_json(team_json)


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch.object(TeamAdapter, 'save', side_effect=Exception('oops'))
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id', return_value=team)
@patch('boto3.resource')
@patch('boto3.client')
def test_enter_team_raises(
        client, resource, get_by_id, createtable, save):
    team_adapter = TeamAdapter('duel-table', 'localhost')
    interactor = AcceptTeamInvitationInteractor(request, team_adapter)
    with pytest.raises(AcceptTeamInvitationException) as excinfo:
        interactor.run()
    assert "Error when modifying the invitation status of player" \
           in str(excinfo.value)


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch.object(TeamAdapter, 'save', autospec=True)
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.team_adapter.TeamAdapter.get_by_id',
       return_value=team)
@patch('boto3.resource')
@patch('boto3.client')
def test_enter_team(
        boto_client, boto_resource, team_data, create_table_team, save_team):
    team_adapter = TeamAdapter('duel-table', 'localhost')
    request = AcceptTeamInvitationRequestModel({
        'player_id': '9b8c1e9c-a872-46f8-8c72-ed5677f0374c',
        'team_id': 'idduel123',
        'accept_invite': True
    })
    interactor = AcceptTeamInvitationInteractor(
        request=request,
        team_adapter=team_adapter)
    interactor.run()
    assert boto_resource.call_count == 1
    save_team.assert_called_once()
