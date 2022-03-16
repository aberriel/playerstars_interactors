from datetime import date, datetime
from playerstars_domain import (
    CoinType,
    Console,
    Duel,
    DuelMemberType,
    DuelStatus,
    DuelType,
    Game,
    GamePoints,
    MemberStatus,
    MemberType,
    NotificationType,
    Player,
    PlayerConsoles,
    PlayerStatus,
    Team, TeamMember, User)
from playerstars_domain.utils.datetime_helper import aware_utc
from playerstars_interactors import (
    CreateDuelException,
    CreateDuelInteractor,
    CreateDuelRequestModel,
    CreateDuelResponseModel)
from playerstars_interactors.utils.domain_utils import EntityNotFoundException
from unittest.mock import MagicMock, Mock, patch

import pytest


datetime_now_mock = aware_utc(datetime(2020, 5, 21, 18, 0, 0))


prefix = 'playerstars_interactors.duel.create_duel'


def make_game_points():
    return GamePoints(
        game_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        victories=0)


def make_player_consoles():
    game_points_data = make_game_points()
    return PlayerConsoles(
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        game_points=game_points_data,
        tag_name='tag#1')


def make_request_player_json():
    return {
        'challenger': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'challenged': 'b2974336-b947-471a-a8fa-8e46260d8441',
        'challenged_accept': False,
        'console': {
            'entity_id': '531f6ee2-dfef-458e-b918-ebf12793fe37',
            'name': 'Playstation 4',
            'logo_path': '/images/ps4.png'
        },
        'game': {
            'name': 'Fifa 19',
            'logo_path': '/images/fifa19.png',
            'entity_id': '0e3bd0f7-e95c-4168-9083-f1859fa73902'
        },
        'bet_size': 15,
        'star_type': 'GOLDEN_STAR',
        'member_type': 'PLAYER',
        'duel_type': 'INDIVIDUAL'
    }


def make_request_team_json():
    return {
        'challenger': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'challenger_team': '02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        'challenged': '6d3cbd57-974c-4559-a363-eee8d88ba17e',
        'challenged_accept': False,
        'console': {
            'entity_id': '531f6ee2-dfef-458e-b918-ebf12793fe37',
            'name': 'Playstation 4',
            'logo_path': '/images/ps4.png'
        },
        'game': {
            'name': 'Fifa 19',
            'logo_path': '/images/fifa19.png',
            'entity_id': '0e3bd0f7-e95c-4168-9083-f1859fa73902'
        },
        'bet_size': 15,
        'star_type': 'GOLDEN_STAR',
        'member_type': 'TEAM',
        'duel_type': 'INDIVIDUAL'
    }


def make_request_team_json_conflict():
    return {
        'challenger': '02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        'challenged': '521dc268-42ea-4569-8316-005458a2457f',
        'challenged_accept': False,
        'console': {
            'entity_id': '531f6ee2-dfef-458e-b918-ebf12793fe37',
            'name': 'Playstation 4',
            'logo_path': '/images/ps4.png'
        },
        'game': {
            'name': 'Fifa 19',
            'logo_path': '/images/fifa19.png',
            'entity_id': '0e3bd0f7-e95c-4168-9083-f1859fa73902'
        },
        'bet_size': 15,
        'star_type': 'GOLDEN_STAR',
        'member_type': 'TEAM',
        'duel_type': 'INDIVIDUAL'
    }


def make_request_red_star():
    return {
        'challenger': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'challenged': 'b2974336-b947-471a-a8fa-8e46260d8441',
        'challenged_accept': False,
        'console': {
            'entity_id': '531f6ee2-dfef-458e-b918-ebf12793fe37',
            'name': 'Playstation 4',
            'logo_path': '/images/ps4.png'
        },
        'game': {
            'name': 'Fifa 19',
            'logo_path': '/images/fifa19.png',
            'entity_id': '0e3bd0f7-e95c-4168-9083-f1859fa73902'
        },
        'bet_size': 15,
        'star_type': 'RED_STAR',
        'member_type': 'PLAYER',
        'duel_type': 'INDIVIDUAL'
    }


def make_player_1():
    user = User(
        name='Pablinho',
        email='menoti@hotmail.com',
        date_birth=date(1987, 1, 1),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='90210',
        phone_number='5555-4321',
        nickname='zyzukab',
        cpf='123.456.789-01'
    )
    player_1 = Player(
        user=user,
        consoles=[make_player_consoles()],
        red_star_balance=321,
        golden_star_balance=987,
        entity_id='3ed57d64-aa2f-49f9-8d80-10fe7894e283')
    return player_1


def make_player_1_without_balance():
    player_data = make_player_1()
    player_data.red_star_balance = 0
    player_data.golden_star_balance = 0
    return player_data


def make_team_member_1(member_type):
    player_data = make_player_1()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_player_2():
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
        entity_id='b2974336-b947-471a-a8fa-8e46260d8441',
        user=user_data,
        consoles=[make_player_consoles()],
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    return player_data


def make_team_member_2(member_type):
    player_data = make_player_2()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_player_3():
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
        entity_id='043381c1-ea75-45ce-9104-7a6e6d205a65',
        user=user_data,
        consoles=[make_player_consoles()],
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    return player_data


def make_team_member_3(member_type):
    player_data = make_player_3()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_player_4():
    user_data = User(
        date_birth=date(1989, 11, 16),
        country="Brasil",
        street='Avenida Brasil',
        street_number='501',
        street_complement='apt 103',
        neighborhood='Acari',
        city="Rio de Janeiro",
        nickname="rebequinha",
        cpf="14217868231",
        name="Rebecca",
        phone_number="21991419377",
        state="RJ",
        postal_code="22770234",
        email="rebecca@stormsec.com.br")
    player_data = Player(
        entity_id="3a8b0e09-152a-48b7-8aab-60341b22f469",
        user=user_data,
        consoles=[make_player_consoles()],
        player_status=PlayerStatus.AVAILABLE,
        points=900,
        red_star_balance=130,
        golden_star_balance=275,
        terms=True,
        is_admin=False,
        is_blocked=False)
    return player_data


def make_team_member_4(member_type):
    player_data = make_player_4()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_team_1():
    team_data = Team(
        entity_id='02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        name='Brazucas',
        captain=make_team_member_1(MemberType.CAPTAIN),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[make_team_member_2(MemberType.MEMBER)])
    return team_data


def make_team_2():
    team_data = Team(
        entity_id='6d3cbd57-974c-4559-a363-eee8d88ba17e',
        name='Vascuuu',
        captain=make_team_member_3(MemberType.CAPTAIN),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[make_team_member_4(MemberType.MEMBER)])
    return team_data


def make_team_3():
    team_data = Team(
        entity_id='521dc268-42ea-4569-8316-005458a2457f',
        name='Cariocaxx',
        captain=make_team_member_1(MemberType.CAPTAIN),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[make_team_member_4(MemberType.MEMBER)])
    return team_data


def make_duel_player():
    game = Game(name='Fifa 19',
                logo_path='/images/fifa19.png',
                entity_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
                points=0,
                victories=0)
    console = Console(entity_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
                      name='Playstation 4',
                      logo_path='/images/ps4.png',
                      games=[game])
    duel = Duel(
        challenger='f930959f-63ec-4478-89d6-7d84bb748b37',
        challenger_confirmation=False,
        challenged='af1bf976-b212-42a9-af2a-fc20ed4688de',
        challenged_confirmation=False,
        game=game,
        console=console,
        star_type=CoinType.GOLDEN_STAR,
        bet_size=0,
        total_reward=0,
        time_start=None,
        creation_datetime=datetime_now_mock,
        status=DuelStatus.LOBBY,
        winner=None,
        championship=None,
        entity_id='1q2w3e',
        duel_type=DuelType.INDIVIDUAL,
        member_type=DuelMemberType.PLAYER,
        time_to_finish_duel=300,
        time_to_accept_invitation=5)
    return duel


duel_adapter_create_duel = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(autospec=True, return_value='7e6cf926'))
notification_adapter_mock = MagicMock(
    save=MagicMock(return_value='notification123'))
player_adapter_mock_1 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_1()))
player_adapter_mock_3 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_3()))
team_adapter_create_duel = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_team_1()))


@patch(f'{prefix}.aware_now')
def test_create_duel_response_current_time(mock_datetime):
    duel_data = make_duel_player()
    response_data = CreateDuelResponseModel(duel_data)
    current_server_datetime = response_data.current_server_time

    assert current_server_datetime
    assert current_server_datetime == mock_datetime().isoformat()


@patch(f'{prefix}.aware_now')
def test_create_duel_response_call(mock_datetime):
    duel_data = make_duel_player()
    response_data = CreateDuelResponseModel(duel_data)
    response_data_json = response_data()

    assert response_data_json
    assert isinstance(response_data_json, dict)
    assert response_data_json == {
        'duel_id': '1q2w3e',
        'created_at': '2020-05-21T18:00:00+00:00',
        'accept_time': 5,
        'time_to_finish': 300,
        'current_server_time': mock_datetime().isoformat()}


@patch('boto3.resource')
@patch('boto3.client')
def test_get_challenger_player(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    challenger = interactor.get_challenger()

    assert isinstance(challenger, Player)
    assert challenger == make_player_1()


@patch('boto3.resource')
@patch('boto3.client')
def test_get_challenged_player(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    challenger = interactor.get_challenged()

    assert isinstance(challenger, Player)
    assert challenger == make_player_1()


@patch('boto3.resource')
@patch('boto3.client')
def test_get_participant_team(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_team_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    challenger = interactor.get_challenger()

    assert isinstance(challenger, Team)
    assert challenger == make_team_1()


@patch('boto3.resource')
@patch('boto3.client')
def test_get_paying_player_as_player(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    interactor.challenger = make_player_1()
    paying_player = interactor.get_paying_player()

    assert isinstance(paying_player, Player)
    assert paying_player == make_player_1()


@patch('boto3.resource')
@patch('boto3.client')
def test_get_paying_player_as_team(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_team_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_3,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    interactor.challenger = make_team_2()
    paying_player = interactor.get_paying_player()

    assert isinstance(paying_player, Player)
    assert paying_player.user.name == make_player_3().user.name


@patch('boto3.resource')
@patch('boto3.client')
def test_check_red_star_balance_raises(boto_client, boto_resource):
    request_json = make_request_red_star()
    request_json['bet_size'] = 1500
    request = CreateDuelRequestModel(request_json)
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    interactor.challenger = make_player_1()

    with pytest.raises(CreateDuelException) as exc:
        interactor.check_balance()
    assert "Player zyzukab doesn't have enought red star" in str(exc.value)


@patch('boto3.resource')
@patch('boto3.client')
def test_check_golden_star_balance(boto_client, boto_resource):
    request_json = make_request_player_json()
    request_json['bet_size'] = 1500
    request = CreateDuelRequestModel(request_json)
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    interactor.challenger = make_player_1()

    with pytest.raises(CreateDuelException) as exc:
        interactor.check_balance()
    assert "Player zyzukab doesn't have enought golden star" in str(exc.value)


@patch('boto3.resource')
@patch('boto3.client')
def test_init_game(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)

    game = interactor._init_game()
    assert game == Game(
        name='Fifa 19',
        logo_path='/images/fifa19.png',
        entity_id='0e3bd0f7-e95c-4168-9083-f1859fa73902')


@patch('boto3.resource')
@patch('boto3.client')
def test_init_console(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    console = interactor._init_console()
    assert console == Console(
        entity_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        name='Playstation 4',
        logo_path='/images/ps4.png',
        tag_name=None,
        games=[Game(
            name='Fifa 19',
            logo_path='/images/fifa19.png',
            entity_id='0e3bd0f7-e95c-4168-9083-f1859fa73902'
        )])


@patch.object(CreateDuelInteractor, 'get_challenger', return_value=make_player_1())
@patch.object(CreateDuelInteractor, 'get_challenged', return_value=make_player_2())
@patch.object(CreateDuelInteractor, '_init_game')
@patch.object(CreateDuelInteractor, '_init_console')
@patch.object(CreateDuelInteractor, '_init_duel')
@patch.object(CreateDuelInteractor, 'invite_member')
@patch(f'{prefix}.CreateDuelResponseModel')
@patch(f'{prefix}.uuid')
@patch(f'{prefix}.aware_now')
@patch('boto3.resource')
@patch('boto3.client')
def test_create_duel_player(boto_client,
                            boto_resource,
                            mock_datetime,
                            uuid_mock,
                            mock_response_model,
                            mock_invite_member,
                            mock_init_duel,
                            mock_init_console,
                            mock_init_game,
                            mock_get_challenged,
                            mock_get_challenger):
    uuid_mock.uuid4 = Mock(return_value='7e6cf926')
    duel_adapter_create_duel.save.call_count = 0
    notification_adapter_mock.save.call_count = 0

    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    response = interactor.run()

    mock_get_challenger.assert_called_once()
    mock_get_challenged.assert_called_once()
    mock_init_console.assert_called()
    mock_init_game.assert_called()
    mock_init_duel.assert_called_with(game=mock_init_game(), console=mock_init_console())
    mock_invite_member.assert_called()
    mock_response_model.assert_called_with(mock_init_duel())
    assert response == mock_response_model()


@patch.object(CreateDuelInteractor, 'get_challenger', return_value=make_team_1())
@patch.object(CreateDuelInteractor, 'get_challenged', return_value=make_team_2())
@patch.object(CreateDuelInteractor, 'invite_member')
@patch.object(CreateDuelInteractor, '_init_duel')
@patch.object(CreateDuelInteractor, '_init_console')
@patch.object(CreateDuelInteractor, '_init_game')
@patch(f'{prefix}.CreateDuelResponseModel')
@patch(f'{prefix}.uuid')
@patch(f'{prefix}.aware_now')
@patch('boto3.resource')
@patch('boto3.client')
def test_create_duel_team(boto_client,
                          boto_resource,
                          mock_datetime,
                          uuid_mock,
                          mock_response_model,
                          mock_init_game,
                          mock_init_console,
                          mock_init_duel,
                          mock_invite_member,
                          mock_get_challenged,
                          mock_get_challenger):
    uuid_mock.uuid4 = Mock(return_value='7e6cf926')
    duel_adapter_create_duel.save.call_count = 0
    notification_adapter_mock.save.call_count = 0

    request = CreateDuelRequestModel(make_request_team_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    response = interactor.run()

    mock_get_challenger.assert_called_once()
    mock_get_challenged.assert_called_once()
    mock_init_game.assert_called()
    mock_init_console.assert_called()
    mock_init_duel.assert_called_with(game=mock_init_game(), console=mock_init_console())
    mock_init_duel().save.assert_called()
    mock_invite_member.assert_called()
    mock_response_model.assert_called_with(mock_init_duel())
    assert response == mock_response_model()


player_adapter_member_not_found = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=None))


@patch('boto3.resource')
@patch('boto3.client')
def test_create_duel_member_not_found(boto_client, boto_resource):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_member_not_found,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)

    with pytest.raises(EntityNotFoundException) as exc:
        interactor.run()
    assert 'Player 3ed57d64-aa2f-49f9-8d80-10fe7894e283 not found' in str(exc.value)


@patch.object(CreateDuelInteractor, 'get_challenger',
              return_value=make_player_1_without_balance())
@patch.object(CreateDuelInteractor, 'get_challenged', return_value=make_player_2())
@patch('boto3.resource')
@patch('boto3.client')
def test_member_without_balance(client, resource, challenged, challenger):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)

    with pytest.raises(CreateDuelException) as exc:
        interactor.run()
    assert "Player zyzukab doesn't have enought golden star" in str(exc.value)


@patch.object(CreateDuelInteractor, 'get_challenger', return_value=make_team_1())
@patch.object(CreateDuelInteractor, 'get_challenged', return_value=make_team_3())
@patch(f'{prefix}.uuid')
@patch('boto3.resource')
@patch('boto3.client')
def test_conflict_team_same_member(boto_client,
                                   boto_resource,
                                   uuid_mock,
                                   get_challenged,
                                   get_challenger):
    request = CreateDuelRequestModel(make_request_team_json_conflict())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_create_duel,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)

    with pytest.raises(CreateDuelException) as exc:
        interactor.run()
    assert 'Error during duel creation: Brazucas captain cannot be ' \
           'in both teams' in str(exc.value)


duel_adapter_raise_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(side_effect=Exception('oops')))


@patch.object(CreateDuelInteractor, 'get_challenger', side_effect=Exception('oops'))
@patch.object(CreateDuelInteractor, 'get_challenged', return_value=make_player_2())
@patch.object(CreateDuelInteractor, 'invite_member')
@patch(f'{prefix}.uuid')
@patch('boto3.resource')
@patch('boto3.client')
def test_create_duel_raises(boto_client,
                            boto_resource,
                            uuid_mock,
                            mock_invite_member,
                            get_challenged,
                            get_challenger):
    request = CreateDuelRequestModel(make_request_player_json())
    interactor = CreateDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_raise_mock,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_create_duel,
        time_to_finish=300,
        accept_time=5)
    mock_invite_member.assert_not_called()

    with pytest.raises(CreateDuelException) as exc:
        interactor.run()
    assert 'Error during duel creation: oops' in str(exc.value)


@patch(f'{prefix}.aware_now')
@patch(f'{prefix}.create_notification')
@patch.object(CreateDuelInteractor, '_get_captain')
@patch.object(CreateDuelInteractor, '_get_member_player')
@patch.object(CreateDuelInteractor, '_get_member_team_id')
def test_invite_member_player(mock_get_member_team_id,
                              mock_get_member_player,
                              mock_get_captain,
                              mock_create_notification,
                              mock_aware_now):
    mock_request = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)

    mock_challenger = MagicMock()
    interactor.challenger = mock_challenger
    mock_challenged = MagicMock()
    interactor.challenged = mock_challenged
    mock_duel = MagicMock()
    interactor.duel = mock_duel
    interactor.invite_member()

    mock_get_member_player.assert_called()
    mock_get_member_team_id.assert_called_with(mock_challenged)
    mock_aware_now.assert_called()
    mock_create_notification.assert_called_with(
        player_data=mock_get_member_player(),
        notification_adapter=mock_notification_adapter,
        notification_type=NotificationType.DUEL_INVITE,
        duel_id=mock_duel.entity_id,
        team_id=mock_get_member_team_id(),
        notification_image=mock_duel.game.logo_path,
        notification_complement=mock_get_member_player().user.nickname,
        creation_datetime=mock_aware_now(),
        logger_instance=interactor.logger)


@patch(f'{prefix}.isinstance', return_value=True)
@patch.object(CreateDuelInteractor, '_get_captain')
def test__get_member_player_as_player(mock_get_captain, mock_isinstance):
    mock_member = MagicMock()
    mock_request = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)
    member = interactor._get_member_player(mock_member)

    mock_isinstance.assert_called()
    mock_get_captain.assert_not_called()
    assert member == mock_member


@patch(f'{prefix}.isinstance', return_value=False)
@patch.object(CreateDuelInteractor, '_get_captain')
def test__get_member_player_as_team(mock_get_captain, mock_isinstance):
    mock_member = MagicMock()
    mock_request = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)
    member = interactor._get_member_player(mock_member)

    mock_isinstance.assert_called()
    mock_get_captain.assert_called_with(mock_member.captain.player_id)
    assert member == mock_get_captain()


@patch(f'{prefix}.isinstance', return_value=False)
def test__get_member_team_id_as_player(mock_isinstance):
    mock_request = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)
    mock_member = MagicMock()
    team_id = interactor._get_member_team_id(mock_member)

    mock_isinstance.assert_called()
    assert team_id is None


@patch(f'{prefix}.isinstance', return_value=True)
def test__get_member_team_id_as_team(mock_isinstance):
    mock_request = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)
    mock_member = MagicMock()
    team_id = interactor._get_member_team_id(mock_member)

    mock_isinstance.assert_called()
    assert team_id == mock_member.entity_id


@patch(f'{prefix}.aware_now')
@patch(f'{prefix}.uuid')
@patch(f'{prefix}.DuelMemberType')
@patch(f'{prefix}.DuelType')
@patch(f'{prefix}.Duel')
def test__init_duel(mock_duel,
                    mock_duel_type,
                    mock_duel_member_type,
                    mock_uuid,
                    mock_aware_now):
    mock_request = MagicMock()
    mock_request.challenger = MagicMock()
    mock_request.challenger_team = None

    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_time_to_finish = MagicMock()
    mock_accept_time = MagicMock()
    interactor = CreateDuelInteractor(
        request=mock_request,
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        time_to_finish=mock_time_to_finish,
        accept_time=mock_accept_time)

    mock_console = MagicMock()
    mock_game = MagicMock()
    duel_data = interactor._init_duel(mock_game, mock_console)

    mock_aware_now.assert_called()
    mock_duel.assert_called_with(
        entity_id=str(mock_uuid.uuid4()),
        challenger=mock_request.challenger,
        challenged=mock_request.challenged,
        challenged_accept=False,
        game=mock_game,
        console=mock_console,
        star_type=mock_request.star_type,
        bet_size=mock_request.bet_size,
        challenged_confirmation=False,
        challenger_confirmation=False,
        participants=2,
        time_start=None,
        creation_datetime=mock_aware_now(),
        member_type=mock_duel_member_type(),
        duel_type=mock_duel_type(),
        time_to_finish_duel=mock_time_to_finish,
        time_to_accept_invitation=mock_accept_time)
    assert duel_data == mock_duel()
