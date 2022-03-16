from datetime import date, datetime, timezone
from playerstars_adapters import TeamAdapter
from playerstars_domain import (
    GamePoints, MemberStatus, MemberType, Player, PlayerConsoles,
    PlayerStatus, Team, TeamMember, User)
from playerstars_interactors.team.leave_team import (
    LeaveTeamInteractor, LeaveTeamRequestModel, LeaveTeamException)
from pytest import raises
from unittest.mock import MagicMock, patch


team_creation_datetime = datetime(2020, 1, 15, 18, 1, 13, 123456,
                                  tzinfo=timezone.utc)


def make_player_console():
    game_points_1 = GamePoints(
        game_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        victories=0)
    player_console = PlayerConsoles(
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        game_points=[game_points_1],
        tag_name='tag#1')
    return player_console


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
        consoles=[make_player_console()],
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
        consoles=[make_player_console()],
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


def make_team_member_3(member_type, member_status):
    user_data = User(
        name='Rogério da Silva',
        email='rogerio.silva@stormsec.com.br',
        date_birth=date(1994, 12, 12),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='22666-171',
        phone_number='98666-0171',
        cpf='123.456.789-01',
        nickname='gghhii')
    player_data = Player(
        entity_id='556c0fa8-69c1-4759-b9aa-948b61a595df',
        user=user_data,
        consoles=[make_player_console()],
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        association_date=datetime(2019, 5, 30, 19, 45, 11),
        last_status_change_datetime=datetime(2019, 5, 30, 19, 45, 12),
        member_type=member_type,
        status=member_status)
    return team_member_data


def make_team_1():
    team_data = Team(
        entity_id='6d3cbd57-974c-4559-a363-eee8d88ba17e',
        name='Vascuuu',
        captain=make_team_member_3(MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_1(MemberType.MEMBER, MemberStatus.ACCEPTED)
        ],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_2():
    team_data = Team(
        entity_id='626fba87-e226-453a-974f-83af60d43dcb',
        name='Vascuuu',
        captain=make_team_member_3(MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_1(MemberType.MEMBER, MemberStatus.INVITED),
            make_team_member_2(MemberType.MEMBER, MemberStatus.ACCEPTED),
        ],
        creation_datetime=team_creation_datetime)
    return team_data


@patch.object(TeamAdapter, 'save', autospec=True,
              return_value='6d3cbd57-974c-4559-a363-eee8d88ba17e')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.team_adapter.TeamAdapter.get_by_id',
       return_value=make_team_1())
@patch('boto3.resource')
@patch('boto3.client')
def test_leave_team_with_1_member(
        boto_client, boto_resource, team_data, create_table_team,
        save_team):
    team_adapter = TeamAdapter('team-table', 'localhost')
    request_json = {
        'player_id': 'f930959f-63ec-4478-89d6-7d84bb748b37',
        'team_id': '6d3cbd57-974c-4559-a363-eee8d88ba17e'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter)
    response = interactor.run()

    save_team.assert_called_once()
    assert response == '6d3cbd57-974c-4559-a363-eee8d88ba17e'
    assert len(interactor.team.members) == 1
    assert interactor.team.captain.player_id == \
        interactor.team.members[0].player_id


team_adapter_mock_1 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    delete=MagicMock(return_value=make_team_1().entity_id),
    get_by_id=MagicMock(return_value=make_team_1()),
    save=MagicMock(return_value=make_team_1().entity_id))
team_adapter_mock_2 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_team_2()),
    save=MagicMock(return_value=make_team_2().entity_id))
team_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_team_1()),
    save=MagicMock(side_effect=Exception('oops')))


@patch('boto3.resource')
@patch('boto3.client')
def test_leave_team_with_2_members(boto_client, boto_resource):
    request_json = {
        'player_id': 'af1bf976-b212-42a9-af2a-fc20ed4688de',
        'team_id': '626fba87-e226-453a-974f-83af60d43dcb'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter_mock_2)
    response = interactor.run()

    team_adapter_mock_2.save.assert_called_once()
    assert response == '626fba87-e226-453a-974f-83af60d43dcb'
    assert len(interactor.team.members) == 2

    member_found = \
        next((
            x for x in interactor.team.members
            if x.player_id == 'af1bf976-b212-42a9-af2a-fc20ed4688de'),
            None)
    assert not member_found


@patch('boto3.resource')
def test_leave_team_captain(boto_resource):
    request_json = {
        'player_id': '556c0fa8-69c1-4759-b9aa-948b61a595df',
        'team_id': '6d3cbd57-974c-4559-a363-eee8d88ba17e'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter_mock_1)
    response = interactor.run()
    team_adapter_mock_1.delete.assert_called_once()
    assert response == '6d3cbd57-974c-4559-a363-eee8d88ba17e'


@patch('boto3.resource')
def test_leave_team_not_member(boto_resource):
    request_json = {
        'player_id': '123abc',
        'team_id': '6d3cbd57-974c-4559-a363-eee8d88ba17e'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter_mock_1)
    with raises(LeaveTeamException) as exc:
        interactor.run()
    assert "Error during leave team: The player isn't member of this team" \
           in str(exc.value)


@patch('boto3.resource')
def test_leave_team_invited(boto_resource):
    request_json = {
        'player_id': 'f930959f-63ec-4478-89d6-7d84bb748b37',
        'team_id': '626fba87-e226-453a-974f-83af60d43dcb'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter_mock_2)
    with raises(LeaveTeamException) as exc:
        interactor.run()
    assert "Error during leave team: The member cannot leave " \
           "because your status is INVITED" in str(exc.value)


@patch('boto3.resource')
def test_leave_team_raises(boto_resource):
    request_json = {
        'player_id': 'f930959f-63ec-4478-89d6-7d84bb748b37',
        'team_id': '6d3cbd57-974c-4559-a363-eee8d88ba17e'}
    request = LeaveTeamRequestModel(request_json)
    interactor = LeaveTeamInteractor(request, team_adapter_mock_raises)
    with raises(LeaveTeamException) as exc:
        interactor.run()
    assert "Error during leave team: oops" in str(exc.value)
