from datetime import date
from playerstars_adapters import (
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    GamePoints,
    MemberStatus,
    MemberType,
    Player,
    PlayerConsoles,
    Team,
    TeamMember,
    User)
from playerstars_interactors import (
    GetMatchListException,
    GetMatchListInteractor,
    GetMatchListRequestModel,
    GetMatchListResponseModel)
from pytest import raises
from unittest.mock import patch


def make_game_points_list():
    game_points_1 = GamePoints(
        game_id='04324811-696f-4eb0-9f90-28ae17e61c28',
        victories=0)
    game_points_2 = GamePoints(
        game_id='8afad7e1-c572-44a5-b46c-50be45cc0472',
        victories=0)
    return [game_points_1, game_points_2]


player_console_1 = PlayerConsoles(
    console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
    game_points=make_game_points_list(),
    tag_name='tag#01')


player_console_2 = PlayerConsoles(
    console_id='ca978ce4-fc2a-4cd2-95e2-e96db8891d8d',
    game_points=make_game_points_list(),
    tag_name='tag#02')


player_console_3 = PlayerConsoles(
    console_id='1014fc3f-d867-410d-bd97-134036a25eb9',
    game_points=make_game_points_list(),
    tag_name='tag#03')


def make_player_1():
    user = User(
        name='Pablinho',
        nickname='zyzukab',
        email='menoti@hotmail.com',
        cpf='123.456.789-01',
        date_birth=date(1987, 1, 1),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='90210',
        phone_number='5555-4321')
    player_1 = Player(
        entity_id='3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        user=user,
        consoles=[player_console_1, player_console_2],
        red_star_balance=321,
        golden_star_balance=987,
        terms=True,
        is_blocked=False)
    return player_1


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
        nickname='ddeeff',
        email='luan.garcia@stormsec.com.br',
        cpf='123.456.789-01',
        date_birth=date(1988, 12, 25),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='23335-115',
        phone_number='(21) 99155-2323')
    player_data = Player(
        entity_id='b2974336-b947-471a-a8fa-8e46260d8441',
        user=user_data,
        consoles=[player_console_1, player_console_3],
        red_star_balance=0,
        golden_star_balance=0,
        terms=True,
        is_blocked=False)
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
        nickname='gghhii',
        email='rogerio.silva@stormsec.com.br',
        cpf='123.456.789-01',
        date_birth=date(1994, 12, 12),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='22666-171',
        phone_number='98666-0171')
    player_data = Player(
        entity_id='043381c1-ea75-45ce-9104-7a6e6d205a65',
        user=user_data,
        consoles=[player_console_3],
        red_star_balance=0,
        golden_star_balance=0,
        terms=True,
        is_blocked=False)
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
        name="Rebecca",
        nickname="rebequinha",
        email="rebecca@stormsec.com.br",
        cpf="14217868231",
        date_birth=date(1989, 11, 16),
        country="Brasil",
        street='Avenida Brasil',
        street_number='501',
        street_complement='apt 103',
        neighborhood='Acari',
        city="Rio de Janeiro",
        phone_number="21991419377",
        state="RJ",
        postal_code="22770234")
    player_data = Player(
        entity_id="3a8b0e09-152a-48b7-8aab-60341b22f469",
        user=user_data,
        consoles=[player_console_1],
        red_star_balance=130,
        golden_star_balance=275,
        terms=True,
        is_blocked=False)
    return player_data


def make_team_member_4(member_type):
    player_data = make_player_4()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_player_5():
    user = User(
        name='Anselmo Lira',
        nickname='lira1',
        email='anselmo.lira@stormsec.com.br',
        cpf='123.456.789-01',
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchao',
        city='Hogwarts',
        date_birth=date(1986, 12, 16),
        state='Dartmoor',
        country='England',
        postal_code='634',
        phone_number='5521991996565')
    player = Player(
        entity_id='aba08a32-2424-4a76-8610-c412aee7fa6a',
        user=user,
        consoles=[player_console_2, player_console_3],
        red_star_balance=250,
        golden_star_balance=220,
        terms=True,
        is_blocked=False)
    return player


def make_team_member_5(member_type):
    player_data = make_player_5()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_player_6():
    user_data = User(
        name='Felipe Duarte',
        nickname='dudu123',
        email='f.duarte@stormsec',
        cpf='998.776.554-32',
        date_birth=date(1990, 6, 5),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchao',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='25520-012',
        phone_number='(21) 98144-1317')
    player_data = Player(
        entity_id='6ff6ad1b-20d5-4a8e-b7ac-1b42d5100c85',
        user=user_data,
        consoles=[player_console_1, player_console_2, player_console_3],
        red_star_balance=0,
        golden_star_balance=0,
        terms=True,
        is_blocked=True)
    return player_data


def make_team_member_6(member_type):
    player_data = make_player_6()
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=MemberStatus.ACCEPTED)
    return team_member_data


def make_all_players():
    return [make_player_1(), make_player_2(),
            make_player_3(), make_player_4(),
            make_player_5(), make_player_6()]


# Time da requisição
def make_team_1():
    team_data = Team(
        entity_id='ca288ffb-5496-404d-a60c-79272b20f8f9',
        name='Brazucas',
        captain=make_team_member_1(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_2(MemberType.MEMBER)])
    return team_data


# Time de mesmo capitão
def make_team_2():
    team_data = Team(
        entity_id='7d47e6df-b375-401d-8b55-85c9d18d9d63',
        name='Vascuuu',
        captain=make_team_member_1(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_4(MemberType.MEMBER)])
    return team_data


# Time válido (eu não estou nele e tem o console)
def make_team_3():
    team_data = Team(
        entity_id='79ea6275-4805-4965-b250-f0032e757c67',
        name='Cariocaxx',
        captain=make_team_member_4(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_5(MemberType.MEMBER)])
    return team_data


# Time que não possui o console
def make_team_4():
    team_data = Team(
        entity_id='5fd959ed-1115-4de8-af6d-358eac7bfb45',
        name='Stormtroopers',
        captain=make_team_member_2(MemberType.CAPTAIN),
        console_id='1014fc3f-d867-410d-bd97-134036a25eb9',
        members=[make_team_member_4(MemberType.MEMBER),
                 make_team_member_5(MemberType.MEMBER)])
    return team_data


# Time que eu estou nos membros e tem o console
def make_team_5():
    team_data = Team(
        entity_id='fc333094-ce9a-461d-9a11-e3715780948c',
        name='Furia',
        captain=make_team_member_2(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_1(MemberType.MEMBER),
                 make_team_member_3(MemberType.MEMBER),
                 make_team_member_5(MemberType.MEMBER)])
    return team_data


# Time válido (eu não estou nele e tem o console)
def make_team_6():
    team_data = Team(
        entity_id='a207f93c-06a4-4f64-8200-ffd359d6ea0c',
        name='Cloud9',
        captain=make_team_member_5(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_3(MemberType.MEMBER)])
    return team_data


# Time de capitão desativado (is_blocked = True)
def make_team_7():
    team_data = Team(
        entity_id='173d4697-eb01-4e73-82ec-eeb5fdb136e8',
        name='FaZe Clan',
        captain=make_team_member_6(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[make_team_member_3(MemberType.MEMBER),
                 make_team_member_5(MemberType.MEMBER)]
    )
    return team_data


# Time que só tem o capitão
def make_team_8():
    team_data = Team(
        entity_id='5f4586f0-b572-4434-97dc-73047daf579b',
        name='Sentinels',
        captain=make_team_member_4(MemberType.CAPTAIN),
        console_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        members=[])
    return team_data


def make_all_teams():
    return [make_team_1(), make_team_2(),
            make_team_3(), make_team_4(),
            make_team_5(), make_team_6(),
            make_team_7(), make_team_8()]


def make_request_data_player():
    return {
        'player_id': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'member_type': 'PLAYER',
        'console_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51'}


def make_request_data_team():
    return {
        'player_id': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'member_type': 'TEAM',
        'team_id': 'ca288ffb-5496-404d-a60c-79272b20f8f9',
        'console_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51'}


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_me_player(boto_client,
                       boto_resource,
                       create_table_team,
                       get_by_id_team,
                       create_table_player,
                       get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.get_me()

    get_by_id_player.assert_called_once()
    assert get_by_id_team.call_count == 0
    assert interactor.me_player == make_player_1()
    assert not interactor.me_team


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_me_team(boto_client,
                     boto_resource,
                     create_table_team,
                     get_by_id_team,
                     create_table_player,
                     get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_team())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.get_me()

    get_by_id_player.assert_called_once()
    get_by_id_team.assert_called_once()
    assert interactor.me_team == make_team_1()
    assert interactor.me_player == make_player_1()


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_check_opponent(boto_client,
                        boto_resource,
                        create_table_team,
                        create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_team())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    interactor.me_player = make_player_1()
    interactor.me_player.set_adapter(player_adapter)
    interactor.me_team = make_team_1()
    interactor.me_team.set_adapter(team_adapter)

    # Checando para o caso de sucesso
    check_response_1 = interactor.check_opponent_team(make_team_3())
    assert check_response_1

    # Checando para o mesmo player
    check_response_2 = interactor.check_opponent_team(make_team_1())
    assert not check_response_2

    # Oponente possui o mesmo capitão
    check_response_3 = interactor.check_opponent_team(make_team_2())
    assert not check_response_3

    # Oponente não possui o console
    check_response_4 = interactor.check_opponent_team(make_team_4())
    assert not check_response_4

    # Oponente onde estou como membro
    check_response_5 = interactor.check_opponent_team(make_team_5())
    assert not check_response_5

    # Oponente tem o capitão desativado
    check_response_6 = interactor.check_opponent_team(make_team_7())
    assert check_response_6

    # Oponente só tem o capitão
    check_response_7 = interactor.check_opponent_team(make_team_8())
    assert not check_response_7


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_check_opponent_player_approved(boto_client,
                                        boto_resource,
                                        create_table_team,
                                        create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.me_player = make_player_1()
    interactor.me_player.set_adapter(player_adapter)

    check_response = interactor.check_opponent_player(make_player_2())
    assert check_response


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_check_opponent_player_is_me(boto_client,
                                     boto_resource,
                                     create_table_team,
                                     create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.me_player = make_player_1()
    interactor.me_player.set_adapter(player_adapter)

    check_response = interactor.check_opponent_player(make_player_1())
    assert not check_response


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_check_opponent_player_console(boto_client,
                                       boto_resource,
                                       create_table_team,
                                       create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.me_player = make_player_1()
    interactor.me_player.set_adapter(player_adapter)

    check_response = interactor.check_opponent_player(make_player_3())
    assert not check_response


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_check_opponent_player_not_valid(boto_client,
                                         boto_resource,
                                         create_table_team,
                                         create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    interactor.me_player = make_player_1()
    interactor.me_player.set_adapter(player_adapter)

    check_response = interactor.check_opponent_player(make_player_6())
    assert not check_response


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, 'list_all',
              autospec=True,
              return_value=make_all_players())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, 'list_all',
              autospec=True,
              return_value=make_all_teams())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_player(boto_client,
                               boto_resource,
                               create_table_team,
                               list_all_team,
                               get_by_id_team,
                               create_table_player,
                               list_all_player,
                               get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    response = interactor.run()

    get_by_id_player.assert_called_once()
    assert not get_by_id_team.called
    list_all_player.assert_called_once()
    assert not list_all_team.called
    assert response
    assert isinstance(response, GetMatchListResponseModel)

    match_list = response()
    assert len(match_list) == 2

    player_2_found = next((x for x in match_list
                           if x['entity_id'] == make_player_2().entity_id),
                          None)
    assert player_2_found

    player_3_found = next((x for x in match_list
                           if x['entity_id'] == make_player_3().entity_id),
                          None)
    assert not player_3_found

    player_4_found = next((x for x in match_list
                           if x['entity_id'] == make_player_4().entity_id),
                          None)
    assert player_4_found

    player_5_found = next((x for x in match_list
                           if x['entity_id'] == make_player_5().entity_id),
                          None)
    assert not player_5_found

    player_6_found = next((x for x in match_list
                           if x['entity_id'] == make_player_6().entity_id),
                          None)
    assert not player_6_found


def make_all_players_to_empty_result():
    return [make_player_1(), make_player_3(), make_player_6()]


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, 'list_all',
              autospec=True,
              return_value=make_all_players_to_empty_result())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_player_empty(boto_client,
                                     boto_resource,
                                     create_table_team,
                                     get_by_id_team,
                                     create_table_player,
                                     list_all_player,
                                     get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    response = interactor.run()

    get_by_id_player.assert_called_once()
    assert not get_by_id_team.called
    list_all_player.assert_called_once()
    assert response
    assert isinstance(response, GetMatchListResponseModel)
    assert len(response()) == 0


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, 'list_all',
              autospec=True,
              return_value=make_all_players())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, 'list_all',
              autospec=True,
              return_value=make_all_teams())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_team(boto_client,
                             boto_resource,
                             create_table_team,
                             list_all_team,
                             get_by_id_team,
                             create_table_player,
                             list_all_plauer,
                             get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_team())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    response = interactor.run()

    get_by_id_player.assert_called_once()
    get_by_id_team.assert_called_once()
    list_all_team.assert_called_once()
    assert not list_all_plauer.called
    assert response
    assert isinstance(response, GetMatchListResponseModel)
    match_list = response()
    assert len(match_list) == 3


def make_all_teams_to_empty_result():
    return [make_team_2(), make_team_4(), make_team_8()]


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, 'list_all',
              autospec=True,
              return_value=make_all_teams_to_empty_result())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_team_empty(boto_client,
                                   boto_resource,
                                   create_table_team,
                                   list_all_team,
                                   get_by_id_team,
                                   create_table_player,
                                   get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_team())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    response = interactor.run()

    get_by_id_team.assert_called_once()
    get_by_id_player.assert_called_once()
    list_all_team.assert_called_once()
    assert response
    assert isinstance(response, GetMatchListResponseModel)
    assert not response()


def make_request_data_team_error_captain():
    return {
        'player_id': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'member_type': 'TEAM',
        'team_id': '5fd959ed-1115-4de8-af6d-358eac7bfb45',
        'console_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51'}


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, 'list_all',
              autospec=True,
              return_value=make_all_players())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_4())
@patch.object(TeamAdapter, 'list_all',
              autospec=True,
              return_value=make_all_teams())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_team_error_captain(boto_client,
                                           boto_resource,
                                           create_table_team,
                                           list_all_team,
                                           get_by_id_team,
                                           create_table_player,
                                           list_all_player,
                                           get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_team_error_captain())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    with raises(GetMatchListException) as exc:
        interactor.run()
    assert "Error during recovery match list: " \
           "Player zyzukab isn't the captain of team Stormtroopers" \
           in str(exc.value)


@patch.object(PlayerAdapter, 'get_by_id',
              side_effect=Exception('oops'))
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_raises(boto_client,
                               boto_resource,
                               create_table_team,
                               create_table_player,
                               get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetMatchListRequestModel(make_request_data_player())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    with raises(GetMatchListException) as exc:
        interactor.run()
    assert 'Error during recovery match list: oops' in str(exc.value)


def make_request_data_team_without_console():
    return {
        'player_id': '3ed57d64-aa2f-49f9-8d80-10fe7894e283',
        'member_type': 'TEAM',
        'team_id': 'ca288ffb-5496-404d-a60c-79272b20f8f9',
        'console_id': '1234'}


@patch.object(PlayerAdapter, 'get_by_id',
              autospec=True,
              return_value=make_player_1())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, 'get_by_id',
              autospec=True,
              return_value=make_team_1())
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('boto3.client')
def test_get_match_list_team_havent_duel_console(boto_client,
                                                 boto_resource,
                                                 create_table_team,
                                                 get_by_id_team,
                                                 create_table_player,
                                                 get_by_id_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = \
        GetMatchListRequestModel(make_request_data_team_without_console())
    interactor = GetMatchListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    with raises(GetMatchListException) as exc:
        interactor.run()
    assert "Error during recovery match list: " \
           "Team haven't the duel's console" in str(exc.value)
