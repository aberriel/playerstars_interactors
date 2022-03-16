from datetime import date, datetime, timezone
from playerstars_domain import (
    Console, Game, GamePoints, MemberStatus, MemberType, Player,
    PlayerConsoles, PlayerStatus, Team, TeamMember, User
)

team_creation_datetime = datetime(
    2020, 1, 15, 18, 1, 13, 123456, tzinfo=timezone.utc)


def make_game_points_list():
    game_points_1 = GamePoints(
        game_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        victories=0)
    game_points_2 = GamePoints(
        game_id='52e0eb14-eacb-43ac-89e1-d40f0dd49c93',
        victories=0)
    return [game_points_1, game_points_2]


def make_player_console_1():
    player_console_data = PlayerConsoles(
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        game_points=make_game_points_list(),
        tag_name='tag#01')
    return player_console_data


def make_player_console_2():
    player_console_data = PlayerConsoles(
        console_id='7a5e1697-1e7d-4967-a437-ffc6ce5159cb',
        game_points=make_game_points_list(),
        tag_name='tag#02')
    return player_console_data


def make_console():
    game_1 = Game(
        entity_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        name='Sonic',
        logo_path='http://s3.aws.com/sonic.jpg')
    game_2 = Game(
        entity_id='52e0eb14-eacb-43ac-89e1-d40f0dd49c93',
        name='Super Mario',
        logo_path='http://s3.aws.com/supermario.jpg')

    console = Console(
        entity_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        name='Super Nintendo',
        logo_path='http://s3.aws.com/snes.jpg',
        games=[game_1, game_2])

    return console


def make_team_member_duarte(member_type, member_status):
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
        consoles=[make_player_console_1(), make_player_console_2()],
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


def make_team_member_luan(member_type, member_status):
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
        consoles=[make_player_console_1(), make_player_console_2()],
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9))
    return team_member_data


def make_team_member_rogerio(member_type, member_status):
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
        consoles=[make_player_console_1(), make_player_console_2()],
        red_star_balance=0,
        golden_star_balance=0,
        player_status=PlayerStatus.AVAILABLE)
    team_member_data = TeamMember(
        player_id=player_data.entity_id,
        association_date=datetime(2019, 6, 7, 13, 11, 9),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9),
        member_type=member_type,
        status=member_status)
    return team_member_data


def make_team_duarte_member_accepted():
    team_data = Team(
        entity_id='02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        name='Brazucas',
        captain=make_team_member_luan(
            MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_duarte(
                MemberType.MEMBER, MemberStatus.ACCEPTED),
            make_team_member_rogerio(
                MemberType.MEMBER, MemberStatus.INVITED)
        ],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_duarte_member_accepted_json():
    team_1_json = make_team_duarte_member_accepted().to_json()
    team_1_json['console'] = make_console().to_json()
    return team_1_json


def make_team_duarte_member_invited():
    team_data = Team(
        entity_id='6d3cbd57-974c-4559-a363-eee8d88ba17e',
        name='Vascuuu',
        captain=make_team_member_rogerio(
            MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_duarte(
                MemberType.MEMBER, MemberStatus.INVITED),
            make_team_member_luan(
                MemberType.MEMBER, MemberStatus.ACCEPTED)
        ],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_duarte_member_invited_json():
    team_2_json = make_team_duarte_member_invited().to_json()
    team_2_json['console'] = make_console().to_json()
    return team_2_json


def make_team_duarte_captain():
    team_data = Team(
        entity_id='521dc268-42ea-4569-8316-005458a2457f',
        name='Cariocaxx',
        captain=make_team_member_duarte(
            MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[
            make_team_member_luan(
                MemberType.MEMBER, MemberStatus.ACCEPTED),
            make_team_member_rogerio(
                MemberType.MEMBER, MemberStatus.ACCEPTED)
        ],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_duarte_captain_json():
    team_3_json = make_team_duarte_captain().to_json()
    team_3_json['console'] = make_console().to_json()
    return team_3_json


def make_team_duarte_captain_no_members():
    team_data = Team(
        entity_id='ab529bdb-1942-4254-9579-52daeae73566',
        name='Stormtroopers',
        captain=make_team_member_duarte(
            MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_duarte_captain_no_members_json():
    team_4_json = make_team_duarte_captain_no_members().to_json()
    team_4_json['console'] = make_console().to_json()
    return team_4_json


def make_team_duarte_captain_rogerio_invited():
    team_data = Team(
        entity_id='6a74faab-76ca-4bec-8e17-d3efd0af7959',
        name='FURIA',
        captain=make_team_member_duarte(
            MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        members=[make_team_member_rogerio(
            MemberType.MEMBER, MemberStatus.INVITED)],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_duarte_captain_rogerio_invited_json():
    team_5_json = make_team_duarte_captain_rogerio_invited().to_json()
    team_5_json['console'] = make_console().to_json()
    return team_5_json


team_list = [make_team_duarte_member_invited(),
             make_team_duarte_member_accepted(),
             make_team_duarte_captain(),
             make_team_duarte_captain_no_members(),
             make_team_duarte_captain_rogerio_invited()]
