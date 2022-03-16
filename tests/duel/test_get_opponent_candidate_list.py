from datetime import date, datetime
from playerstars_adapters import PlayerAdapter, TeamAdapter
from playerstars_domain import (
    GamePoints, DuelMemberType, MemberStatus, MemberType, Player,
    PlayerConsoles, PlayerStatus, Team, TeamMember, User)
from playerstars_interactors import (
    GetOpponentCandidateListException,
    GetOpponentCandidateListInteractor,
    GetOpponentCandidateListRequestModel,
    GetOpponentCandidateListResponseModel)
from pytest import raises
from unittest.mock import MagicMock, patch


team_creation_datetime = datetime(2018, 6, 12, 15, 17, 19)


# Player da requisição
def make_player_1():
    game_points_1 = GamePoints('17dfe88b-482f-42e9-a3d1-b30f2a92ca78', 0)
    game_points_2 = GamePoints('7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8', 0)
    game_points_3 = GamePoints('08e56b37-8133-4363-becd-3a5c2ae164d5', 0)
    player_consoles_1 = PlayerConsoles(
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        tag_name='tag#1',
        game_points=[game_points_1, game_points_2])
    player_consoles_2 = PlayerConsoles(
        console_id='4c3aabac-ac65-48f3-93e1-33a71e633c6a',
        tag_name='tag#2',
        game_points=[game_points_2, game_points_3])

    user_data = User(name='Anselmo Lira',
                     email='anselmo.lira@stormsec.com.br',
                     date_birth=date(1986, 12, 16),
                     street='Avenida Brasil',
                     street_number='500',
                     street_complement='apt 607',
                     neighborhood='pechinchão',
                     city='Rio de Janeiro',
                     state='Rio de Janeiro',
                     country='Brasil',
                     postal_code='25525-001',
                     phone_number='(21) 2222-3333',
                     cpf='123.456.789-01',
                     nickname='zyzukab')
    player_data = Player(entity_id='51ee013a-d7eb-428d-a856-8d5b2853a68e',
                         user=user_data,
                         consoles=[player_consoles_1, player_consoles_2],
                         red_star_balance=10,
                         golden_star_balance=10,
                         player_status=PlayerStatus.AVAILABLE,
                         terms=True)
    return player_data


# Tem o console mas não tem o game
def make_player_2():
    game_points_1 = GamePoints('17dfe88b-482f-42e9-a3d1-b30f2a92ca78', 0)
    player_consoles_1 = PlayerConsoles(
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        tag_name='tag#2',
        game_points=[game_points_1])

    user_data = User(name='Felipe Duarte',
                     email='f.duarte@stormsec.com.br',
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
                     nickname='abababc')
    player_data = Player(entity_id='8734e07d-d629-458c-bc18-2b4be326fc84',
                         user=user_data,
                         consoles=[player_consoles_1],
                         red_star_balance=15,
                         golden_star_balance=15,
                         player_status=PlayerStatus.AVAILABLE,
                         terms=True)
    return player_data


# Tem o game mas não tem o console
def make_player_3():
    game_points_2 = GamePoints('7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8', 0)
    game_points_3 = GamePoints('08e56b37-8133-4363-becd-3a5c2ae164d5', 0)
    player_consoles_2 = PlayerConsoles(
        console_id='4c3aabac-ac65-48f3-93e1-33a71e633c6a',
        tag_name='tag#2',
        game_points=[game_points_2, game_points_3])
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
    player_data = Player(entity_id='af1bf976-b212-42a9-af2a-fc20ed4688de',
                         user=user_data,
                         consoles=[player_consoles_2],
                         red_star_balance=0,
                         golden_star_balance=0,
                         player_status=PlayerStatus.AVAILABLE)
    return player_data


# Oponente válido
def make_player_4():
    game_points_1 = GamePoints('17dfe88b-482f-42e9-a3d1-b30f2a92ca78', 0)
    game_points_2 = GamePoints('7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8', 0)
    game_points_3 = GamePoints('08e56b37-8133-4363-becd-3a5c2ae164d5', 0)
    player_consoles_1 = PlayerConsoles(
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        tag_name='tag#1',
        game_points=[game_points_1, game_points_2, game_points_3])
    user_data = User(
        name='Rog�rio da Silva',
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
    player_data = Player(entity_id='556c0fa8-69c1-4759-b9aa-948b61a595df',
                         user=user_data,
                         consoles=[player_consoles_1],
                         red_star_balance=0,
                         golden_star_balance=0,
                         player_status=PlayerStatus.AVAILABLE)
    return player_data


# Oponente válido
def make_player_5():
    game_points_1 = GamePoints('17dfe88b-482f-42e9-a3d1-b30f2a92ca78', 0)
    game_points_2 = GamePoints('7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8', 0)
    game_points_3 = GamePoints('08e56b37-8133-4363-becd-3a5c2ae164d5', 0)
    player_consoles_1 = PlayerConsoles(
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        tag_name='tag#1',
        game_points=[game_points_1, game_points_2])
    player_consoles_2 = PlayerConsoles(
        console_id='4c3aabac-ac65-48f3-93e1-33a71e633c6a',
        tag_name='tag#2',
        game_points=[game_points_2, game_points_3])
    user_data = User(
        name='Adriano Silva',
        email='adriano.silva@stormsec.com.br',
        date_birth=date(1972, 10, 22),
        street='Rua do Rio',
        street_number='5000',
        street_complement='apt 101',
        neighborhood='Barra da Tijuca',
        city='Rio de Janeiro',
        state='Rio de Janeiro',
        country='Brasil',
        postal_code='22666-222',
        phone_number='98666-0222',
        cpf='123.456.789-01',
        nickname='adri')
    player_data = Player(entity_id='05d84ca3-0abb-40a7-9ce5-532dfc8aaefb',
                         user=user_data,
                         consoles=[player_consoles_1, player_consoles_2],
                         red_star_balance=0,
                         golden_star_balance=0,
                         player_status=PlayerStatus.AVAILABLE)
    return player_data


def make_all_players():
    return [make_player_1(), make_player_2(),
            make_player_3(), make_player_4(),
            make_player_5()]


def make_all_players_invalids():
    return [make_player_1(), make_player_2(), make_player_3()]


def make_team_member_1(member_type, member_status):
    player_data = make_player_1()
    return TeamMember(
        player_id=player_data.entity_id,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9),
        member_type=member_type,
        status=member_status)


def make_team_member_2(member_type, member_status):
    player_data = make_player_2()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 10))


def make_team_member_3(member_type, member_status):
    player_data = make_player_3()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9))


def make_team_member_4(member_type, member_status):
    player_data = make_player_4()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2020, 1, 20, 19, 11, 44),
        last_status_change_datetime=datetime(2020, 1, 20, 19, 11, 44))


def make_team_member_5(member_type, member_status):
    player_data = make_player_5()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2020, 1, 20, 19, 11, 40),
        last_status_change_datetime=datetime(2020, 1, 20, 19, 11, 40))


# Time do player
def make_team_1():
    team_data = Team(
        entity_id='70a601a2-71da-4b16-8fd8-3f98d9612612',
        name='Brazucas',
        victories=0,
        captain=make_team_member_1(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_2(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED),
                 make_team_member_3(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Outro time do player
def make_team_2():
    team_data = Team(
        entity_id='3c029e99-e519-4b4e-8aea-97ecc7242308',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_1(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_4(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED),
                 make_team_member_5(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time válido como oponente
def make_team_3():
    team_data = Team(
        entity_id='cde71d92-3c0a-415a-8c01-103db0e083ac',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_4(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time só tem o capitão ativo
def make_team_4():
    team_data = Team(
        entity_id='91e1df79-5dc7-4cd0-bb22-1ac691f9c63b',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_4(MemberType.MEMBER,
                                    MemberStatus.INVITED),
                 make_team_member_5(MemberType.MEMBER,
                                    MemberStatus.INVITED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time válido como oponente
def make_team_5():
    team_data = Team(
        entity_id='242409d2-6879-4b2f-82ea-4632ef26a70f',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_2(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_4(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED),
                 make_team_member_5(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time tem o console mas não tem o game
def make_team_6():
    team_data = Team(
        entity_id='0d5f403b-63ee-4c1e-bec3-00787a022190',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_4(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='idgame123',
        members=[make_team_member_5(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time tem o game mas não tem o console
def make_team_7():
    team_data = Team(
        entity_id='571191ed-2fa8-405b-b2a5-0c85b6efb5de',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='idconsole123',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_4(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time tem o player como membro
def make_team_8():
    team_data = Team(
        entity_id='30129f85-29a9-4a33-a86d-e02bb5354869',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        members=[make_team_member_1(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


# Time sem membros
def make_team_9():
    team_data = Team(
        entity_id='dfc0c029-7deb-405c-beb0-df18e1d31ef3',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN,
                                   MemberStatus.ACCEPTED),
        console_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        game_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        creation_datetime=team_creation_datetime)
    team_data.members = []
    return team_data


def make_all_teams():
    return [make_team_1(), make_team_2(), make_team_3(),
            make_team_4(), make_team_5(), make_team_6(),
            make_team_7(), make_team_8(), make_team_9()]


def make_all_teams_invalids():
    return [make_team_1(), make_team_2(), make_team_4(),
            make_team_6(), make_team_7(),
            make_team_8(), make_team_9()]


def make_get_opponent_list_player_request():
    return {
        'player_id': make_player_1().entity_id,
        'console_id': '94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        'game_id': '7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        'duel_member_type': DuelMemberType.PLAYER.value}


def make_get_opponent_list_team_request():
    return {
        'player_id': make_player_1().entity_id,
        'team_id': make_team_1().entity_id,
        'console_id': '94aee28a-4d21-4f12-8f29-b2e5c00110fb',
        'game_id': '7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
        'duel_member_type': DuelMemberType.TEAM.value}


player_adapter_mock_invalids = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_valid=make_all_players_invalids()))


team_adapter_mock_invalids = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_valud=make_all_teams_invalids()))


player_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_value=make_all_players()))


team_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_value=make_all_teams()))


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_adapter_player(boto_resource,
                            create_table_team,
                            create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    adapter = interactor._get_adapter()
    assert adapter
    assert isinstance(adapter, PlayerAdapter)


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(TeamAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_adapter_team(boto_resource,
                          create_table_team,
                          create_table_player):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    team_adapter = TeamAdapter('team-table', 'localhost')
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    adapter = interactor._get_adapter()
    assert adapter
    assert isinstance(adapter, TeamAdapter)


@patch('boto3.resource')
def test_check_captain_not_on_members_same_captain(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    team_data = make_team_2()
    check_result = interactor.check_captain_not_on_members(team_data)
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_captain_not_on_members_on_members(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    team_data = make_team_8()
    check_result = interactor.check_captain_not_on_members(team_data)
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_captain_not_on_members_not_on_members(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_captain_not_on_members(make_team_5())
    assert isinstance(check_result, bool)
    assert check_result


@patch('boto3.resource')
def test_check_team_for_opponent_same_team_id(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_1())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponent_different_console(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_7())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponent_different_game(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_6())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponent_captain_on_members(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_8())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponents_without_members(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_9())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponents_only_captain_on_members(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    team_data = make_team_9()
    team_data.members.append(team_data.captain)
    assert len(team_data.members) == 1
    assert team_data.members[0].player_id == team_data.captain.player_id

    check_result = interactor.check_team_for_opponent(team_data)
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_team_for_opponent_valid(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_team_for_opponent(make_team_3())
    assert isinstance(check_result, bool)
    assert check_result


@patch('boto3.resource')
def test_check_player_for_opponent_same_player_id(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_player_for_opponent(make_player_1())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_player_for_opponent_not_console(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_player_for_opponent(make_player_3())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_player_for_opponent_not_game(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_player_for_opponent(make_player_2())
    assert isinstance(check_result, bool)
    assert not check_result


@patch('boto3.resource')
def test_check_player_for_opponent_valid(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    check_result = interactor.check_player_for_opponent(make_player_4())
    assert isinstance(check_result, bool)
    assert check_result


@patch('boto3.resource')
def test_get_candidate_list_player_empty(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock_invalids,
        team_adapter=team_adapter_mock_invalids)

    oppoennt_list = interactor.get_candidate_list_player()
    assert isinstance(oppoennt_list, list)
    assert len(oppoennt_list) == 0


@patch('boto3.resource')
def test_get_candidate_list_player(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    opponent_list = interactor.get_candidate_list_player()
    assert isinstance(opponent_list, list)
    assert len(opponent_list) == 2

    player_4_found = next((x for x in opponent_list
                           if x.entity_id == make_player_4().entity_id),
                          None)
    player_5_found = next((x for x in opponent_list
                           if x.entity_id == make_player_5().entity_id),
                          None)
    assert player_4_found
    assert player_5_found


@patch('boto3.resource')
def test_get_candidate_list_team_empty(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock_invalids,
        team_adapter=team_adapter_mock_invalids)

    opponent_list = interactor.get_candidate_list_team()
    assert isinstance(opponent_list, list)
    assert len(opponent_list) == 0


@patch('boto3.resource')
def test_get_candidate_list_team(boto_resource):
    player_adapter_mock.list_all.call_count = 0
    team_adapter_mock.list_all.call_count = 0
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    opponent_list = interactor.get_candidate_list_team()
    team_adapter_mock.list_all.assert_called_once()
    assert player_adapter_mock.list_all.call_count == 0
    assert isinstance(opponent_list, list)
    assert len(opponent_list) == 2

    team_3_found = next((x for x in opponent_list
                         if x.entity_id == make_team_3().entity_id),
                        None)
    assert team_3_found
    team_5_found = next((x for x in opponent_list
                         if x.entity_id == make_team_5().entity_id),
                        None)
    assert team_5_found


@patch('boto3.resource')
def test_get_opponent_list_team(boto_resource):
    player_adapter_mock.list_all.call_count = 0
    team_adapter_mock.list_all.call_count = 0
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    response = interactor.run()
    team_adapter_mock.list_all.assert_called_once()
    assert player_adapter_mock.list_all.call_count == 0
    assert response
    assert response.candidate_list
    assert len(response.candidate_list) == 2
    assert isinstance(response, GetOpponentCandidateListResponseModel)
    assert response() == [
        make_team_3().to_json(),
        make_team_5().to_json()]


@patch('boto3.resource')
def test_get_opponent_list_team_empty(boto_resource):
    player_adapter_mock_invalids.list_all.call_count = 0
    team_adapter_mock_invalids.list_all.call_count = 0
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_team_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock_invalids,
        team_adapter=team_adapter_mock_invalids)

    response = interactor.run()
    team_adapter_mock_invalids.list_all.assert_called_once()
    assert player_adapter_mock_invalids.list_all.call_count == 0
    assert isinstance(response, GetOpponentCandidateListResponseModel)
    assert response() == []


@patch('boto3.resource')
def test_get_opponent_list_player(boto_resource):
    player_adapter_mock.list_all.call_count = 0
    team_adapter_mock.list_all.call_count = 0
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        team_adapter=team_adapter_mock)

    response = interactor.run()
    player_adapter_mock.list_all.assert_called_once()
    assert team_adapter_mock.list_all.call_count == 0
    assert response
    assert isinstance(response, GetOpponentCandidateListResponseModel)
    assert response.candidate_list
    assert len(response.candidate_list) == 2
    assert response() == [
        make_player_4().to_json(),
        make_player_5().to_json()]


@patch('boto3.resource')
def test_get_opponent_list_player_empty(boto_resource):
    player_adapter_mock_invalids.list_all.call_count = 0
    team_adapter_mock_invalids.list_all.call_count = 0
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock_invalids,
        team_adapter=team_adapter_mock_invalids)

    response = interactor.run()
    player_adapter_mock_invalids.list_all.assert_called_once()
    assert team_adapter_mock_invalids.list_all.call_count == 0
    assert isinstance(response, GetOpponentCandidateListResponseModel)
    assert response() == []


player_adapter_mock_error = MagicMock(
    _create_table_if_dont_exist=MagicMock(),
    list_all=MagicMock(side_effect=Exception('oops')))


@patch('boto3.resource')
def test_get_opponent_list_raises(boto_resource):
    request = GetOpponentCandidateListRequestModel(
        make_get_opponent_list_player_request())
    interactor = GetOpponentCandidateListInteractor(
        request=request,
        player_adapter=player_adapter_mock_error,
        team_adapter=team_adapter_mock)

    with raises(GetOpponentCandidateListException) as exc:
        interactor.run()
    assert 'Error during restoring duel candidates: oops' in str(exc.value)
