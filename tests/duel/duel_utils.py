from datetime import date, datetime, timezone
from playerstars_domain import (
    CoinType, ComponentResult, Console, Duel, DuelComponentResult, PreDuel,
    DuelMemberType, DuelStatus, Game, GamePoints, MemberStatus, User,
    MemberType, Player, PlayerConsoles, PlayerStatus, Team, TeamMember)
from playerstars_domain.duel.pre_duel import Status as PreDuelStatus


result_submit_datetime = datetime(2020, 1, 15, 18, 1, 13, tzinfo=timezone.utc)


team_creation_datetime = datetime(2020, 1, 15, 18, 1, 13, 123456,
                                  tzinfo=timezone.utc)


def make_coded_matrix():
    return '''\
        I
        1X
        12I
        122I
        2222X
        22221I
        222211I
        TXTTXTTT
        T2II1ITTT
        T2TI11ITTT'''


def make_duel_player_finished_to_compare():
    duel_data = make_duel_player_progress_with_result_challenged()
    player_result = DuelComponentResult(
        result=ComponentResult.LOSER,
        submission_datetime=result_submit_datetime,
        result_image='bucket_url/placar.jpg')
    duel_data.challenger_duel_result = player_result
    duel_data.winner = duel_data.challenger
    duel_data.status = DuelStatus.FINISHED_BY_VICTORY

    winner = duel_data.challenger
    duel_data.challenger = winner
    return duel_data


def make_duel_team_finished_to_challenger_to_compare():
    duel_data = make_duel_team_progress_result_challenger()
    team_result = DuelComponentResult(
        result=ComponentResult.LOSER,
        submission_datetime=result_submit_datetime,
        result_image='bucket_url/placar.jpg')
    duel_data.challenged_duel_result = team_result
    duel_data.winner = duel_data.challenger
    duel_data.status = DuelStatus.FINISHED_BY_VICTORY
    return duel_data


def make_game_1():
    return Game(entity_id='17dfe88b-482f-42e9-a3d1-b30f2a92ca78',
                name='Need for Speed',
                logo_path='http://s3.aws.com/nfs.jpg',
                active=True)


def make_game_2():
    return Game(entity_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
                name='Sonic The Hedgehog',
                logo_path='http://s3.aws.com/sonic.jpg',
                active=True)


def make_game_3():
    return Game(entity_id='05336490-d9f3-4dce-8907-44fa746a06e9',
                name='Street Fight X',
                logo_path='http://s3.aws.com/streetfightx.jpg',
                active=True)


def make_console_1():
    game_1 = make_game_1()
    game_2 = make_game_2()
    return Console(entity_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
                   name='Xbox One',
                   logo_path='http://s3.aws.com/xbox_one.jpg',
                   tag_name='nick#1',
                   games=[game_1, game_2])


def make_console_1_without_games():
    console_1 = make_console_1()
    console_1.games = []
    return console_1


def make_console_2():
    game_1 = make_game_1()
    game_2 = make_game_2()
    game_3 = make_game_3()
    return Console(entity_id='3be80d13-6052-416c-87a3-eec497e12c82',
                   name='Nintendo Switch',
                   tag_name='nick#2',
                   logo_path='http://s3.aws.com/switch.jpg',
                   games=[game_1, game_2, game_3])


def make_player_1():
    game_points_1 = GamePoints(make_game_1().entity_id, 0)
    game_points_2 = GamePoints(make_game_2().entity_id, 0)
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#1',
        game_points=[game_points_1, game_points_2])

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
                         consoles=[player_consoles_1],
                         red_star_balance=10,
                         golden_star_balance=10,
                         player_status=PlayerStatus.AVAILABLE,
                         terms=True)
    return player_data


def make_player_1_without_game_points():
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#1',
        game_points=[])
    player_data = make_player_1()
    player_data.consoles = [player_consoles_1]
    return player_data


def make_player_2():
    game_points_1 = GamePoints(make_game_1().entity_id, 0)
    game_points_2 = GamePoints(make_game_2().entity_id, 0)
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#2',
        game_points=[game_points_1, game_points_2])

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


def make_player_2_without_game_points():
    player_data = make_player_2()
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#2',
        game_points=[])
    player_data.consoles = [player_consoles_1]
    return player_data


def make_player_3():
    game_points_1 = GamePoints(make_game_1().entity_id, 0)
    game_points_2 = GamePoints(make_game_2().entity_id, 0)
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#3',
        game_points=[game_points_1, game_points_2])
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
                         consoles=[player_consoles_1],
                         red_star_balance=0,
                         golden_star_balance=0,
                         player_status=PlayerStatus.AVAILABLE)
    return player_data


def make_player_4():
    game_points_1 = GamePoints(make_game_1().entity_id, 0)
    game_points_2 = GamePoints(make_game_2().entity_id, 0)
    player_consoles_1 = PlayerConsoles(
        console_id=make_console_1().entity_id,
        tag_name='tag#4',
        game_points=[game_points_1, game_points_2])
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
    player_data = Player(entity_id='556c0fa8-69c1-4759-b9aa-948b61a595df',
                         user=user_data,
                         consoles=[player_consoles_1],
                         red_star_balance=0,
                         golden_star_balance=0,
                         player_status=PlayerStatus.AVAILABLE)
    return player_data


def make_team_member_1(member_type, member_status):
    player_data = make_player_1()
    return TeamMember(
        player_id=player_data.entity_id,
        association_date=datetime(2019, 6, 7, 13, 11, 9,
                                  tzinfo=timezone.utc),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9,
                                             tzinfo=timezone.utc),
        member_type=member_type,
        status=member_status)


def make_team_member_2(member_type, member_status):
    player_data = make_player_2()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9,
                                  tzinfo=timezone.utc),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 10,
                                             tzinfo=timezone.utc))


def make_team_member_3(member_type, member_status):
    player_data = make_player_3()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2019, 6, 7, 13, 11, 9,
                                  tzinfo=timezone.utc),
        last_status_change_datetime=datetime(2019, 6, 7, 13, 11, 9,
                                             tzinfo=timezone.utc))


def make_team_member_4(member_type, member_status):
    player_data = make_player_4()
    return TeamMember(
        player_id=player_data.entity_id,
        member_type=member_type,
        status=member_status,
        association_date=datetime(2020, 1, 20, 19, 11, 44,
                                  tzinfo=timezone.utc),
        last_status_change_datetime=datetime(2020, 1, 20, 19, 11, 44,
                                             tzinfo=timezone.utc))


def make_team_1():
    team_data = Team(
        entity_id='02c8a4b5-33cf-4b28-b618-0e7cb9d6707e',
        name='Brazucas',
        victories=0,
        captain=make_team_member_2(MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id=make_console_1().entity_id,
        members=[make_team_member_1(MemberType.MEMBER,
                                    MemberStatus.ACCEPTED)],
        creation_datetime=team_creation_datetime)
    return team_data


def make_team_2():
    team_data = Team(
        entity_id='6d3cbd57-974c-4559-a363-eee8d88ba17e',
        name='Vascuuu',
        victories=0,
        captain=make_team_member_3(MemberType.CAPTAIN, MemberStatus.ACCEPTED),
        console_id=make_console_1().entity_id,
        members=[make_team_member_4(MemberType.MEMBER, MemberStatus.INVITED)],
        creation_datetime=team_creation_datetime)
    return team_data


def make_duel(challenger: str,
              challenged: str,
              member_type: DuelMemberType,
              duel_status: DuelStatus = DuelStatus.DUELING,
              coin_type: CoinType = CoinType.GOLDEN_STAR):
    game = make_game_1()
    console = make_console_1_without_games()

    duel = Duel(
        entity_id='f13eb50c',
        status=duel_status,
        challenger=challenger,
        challenger_confirmation=True,
        challenged=challenged,
        member_type=member_type,
        game=game,
        console=console,
        star_type=coin_type,
        bet_size=3,
        creation_datetime=datetime(1986, 12, 16, 15, 40, 8,
                                   tzinfo=timezone.utc),
        time_start=datetime(1986, 12, 16, 15, 40, 8,
                            tzinfo=timezone.utc),
        challenged_accept=False,
        time_to_finish_duel=300,
        time_to_accept_invitation=5)
    return duel


def make_duel_player(
        challenger=make_player_1(),
        challenged=make_player_2()):
    duel_data = make_duel(
        challenger=challenger.entity_id,
        challenged=challenged.entity_id,
        member_type=DuelMemberType.PLAYER)
    return duel_data


def make_duel_player_in_progress_golden(
        challenger=make_player_1(),
        challenged=make_player_2()):
    duel_data = make_duel_player(challenger, challenged)
    duel_data.star_type = CoinType.GOLDEN_STAR
    duel_data.challenged_confirmation = True
    return duel_data


def make_duel_player_progress_with_result_challenged(
        challenged_result=ComponentResult.WINNER,
        challenger=make_player_1(),
        challenged=make_player_2()):
    duel_data = make_duel_player(challenger, challenged)
    challenged_result = DuelComponentResult(
        result=challenged_result,
        submission_datetime=result_submit_datetime,
        result_image='bucket_url/placar.jpg')
    duel_data.challenged_duel_result = challenged_result
    duel_data.challenged_confirmation = True
    return duel_data


def make_duel_team(
        challenger=make_team_1(),
        challenged=make_team_2()):
    duel_data = make_duel(
        challenger=challenger.entity_id,
        challenged=challenged.entity_id,
        member_type=DuelMemberType.TEAM)
    return duel_data


def make_duel_team_progress_result_challenger(
        challenger=make_team_1(),
        challenged=make_team_2()):
    duel_data = make_duel_team(challenger, challenged)
    challenger_result = DuelComponentResult(
        result=ComponentResult.WINNER,
        submission_datetime=result_submit_datetime,
        result_image='bucket_url/placar.jpg')
    duel_data.challenger_duel_result = challenger_result
    duel_data.challenged_confirmation = True
    return duel_data


def make_duel_team_in_progress_with_results(
        challenger=make_team_1(),
        challenged=make_team_2()):
    duel_data = make_duel_team(challenger, challenged)
    challenger_result = DuelComponentResult(result=ComponentResult.WINNER)
    challenged_result = DuelComponentResult(result=ComponentResult.LOSER)
    duel_data.challenger_duel_result = challenger_result
    duel_data.challenged_duel_result = challenged_result
    duel_data.challenged_confirmation = True
    return duel_data


def preduel_red_star_created(challenger='asadhashas'):
    return PreDuel(
        ack=False,
        challenger=challenger,
        challenged=None,
        game_entity_id='9',
        console_entity_id='801202',
        star_type=CoinType.RED_STAR,
        star_amount=10,
        status=PreDuelStatus.AWAITING,
        duel_type=DuelMemberType.PLAYER)


def preduel_red_star_team_created(challenger='asadhashas'):
    return PreDuel(
        ack=False,
        challenger=challenger,
        challenged=None,
        game_entity_id='9',
        console_entity_id='801202',
        star_type=CoinType.RED_STAR,
        star_amount=10,
        status=PreDuelStatus.AWAITING,
        duel_type=DuelMemberType.TEAM)
