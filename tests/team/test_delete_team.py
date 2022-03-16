from datetime import date, datetime, timezone
from playerstars_domain import (
    GamePoints, MemberStatus, MemberType, Player, PlayerConsoles,
    PlayerStatus, Team, TeamMember, User)
from playerstars_interactors.team.delete_team import (
    DeleteTeamException, DeleteTeamInteractor, DeleteTeamRequestModel)
from unittest.mock import MagicMock, patch
import pytest


def make_player_console_list():
    game_points_1 = GamePoints(
        game_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        victories=0)
    player_console_1 = PlayerConsoles(
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        game_points=game_points_1,
        tag_name='tag#01')
    player_console_2 = PlayerConsoles(
        console_id='7a5e1697-1e7d-4967-a437-ffc6ce5159cb',
        game_points=game_points_1,
        tag_name='tag#02')
    return [player_console_1, player_console_2]


def make_team_member_1(member_type, member_status):
    user_data = User(
        name='Felipe Duarte',
        email='felipe.duarte@stormsec.com.br',
        date_birth=date(1990, 6, 5),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='25520-012',
        phone_number='(21) 98144-1317',
        cpf='123.456.789-01',
        nickname='aabbcc')
    player_data = Player(
        entity_id='f930959f-63ec-4478-89d6-7d84bb748b37',
        user=user_data,
        consoles=make_player_console_list(),
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 10))
    return team_member_data


def make_team_member_2(member_type, member_status):
    user_data = User(
        name='Luan Garcia',
        email='luan.garcia@stormsec.com.br',
        date_birth=date(1988, 12, 25),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='23335-115',
        phone_number='(21) 99155-2323',
        cpf='123.456.789-01',
        nickname='ddeeff')
    player_data = Player(
        entity_id='af1bf976-b212-42a9-af2a-fc20ed4688de',
        user=user_data,
        consoles=make_player_console_list(),
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 2, 9, 21, 17, 45),
        last_status_change_datetime=datetime(2019, 2, 9, 21, 17, 46))
    return team_member_data


def make_team():
    team_data = Team(
        entity_id='02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        name='Brazucas',
        captain=make_team_member_2(MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_1(MemberType.MEMBER, MemberStatus.ACCEPTED)
        ],
        creation_datetime=datetime(2020, 1, 15, 18, 1, 13, 123456,
                                   tzinfo=timezone.utc))
    return team_data


valid_request_json = {
    'player_id': 'af1bf976-b212-42a9-af2a-fc20ed4688de',
    'team_id': '02c8a4b5-33cf-4b28-b618-0e7cb9d6707e'}


team_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    delete=MagicMock(return_value='02c8a4b5-33cf-4b28-b618-0e7cb9d6707e'),
    get_by_id=MagicMock(return_value=make_team()))


@patch('boto3.resource')
@patch('boto3.client')
def test_delete_team(boto_client, boto_resource):
    request = DeleteTeamRequestModel(valid_request_json)
    interactor = DeleteTeamInteractor(
        request=request, team_adapter=team_adapter_mock)
    delete_result = interactor.run()
    team_adapter_mock.save.assert_called_once()
    assert delete_result == '02c8a4b5-33cf-4b28-b618-0e7cb9d6707e'


@patch('boto3.resource')
@patch('boto3.client')
def test_try_delete_not_captain(boto_client, boto_resource):
    request_json = {
        'player_id': 'af1bf976',
        'team_id': '02c8a4b5-33cf-4b28-b618-0e7cb9d6707e'}
    request = DeleteTeamRequestModel(request_json)
    interactor = DeleteTeamInteractor(
        request=request, team_adapter=team_adapter_mock)
    with pytest.raises(DeleteTeamException) as exc:
        interactor.run()
    assert "You aren't the team's captain" in str(exc.value)


team_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(side_effect=DeleteTeamException('oops')),
    get_by_id=MagicMock(return_value=make_team()))


@patch('boto3.resource')
@patch('boto3.client')
def test_delete_team_raises(boto_client, boto_resource):
    request = DeleteTeamRequestModel(valid_request_json)
    interactor = DeleteTeamInteractor(
        request=request, team_adapter=team_adapter_mock_raises)
    with pytest.raises(DeleteTeamException) as exc:
        interactor.run()
    assert 'oops' in str(exc.value)
