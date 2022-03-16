from datetime import date, datetime
from decouple import config
from playerstars_domain import (
    MemberStatus, MemberType, Team, TeamMember, CoinType, ComponentResult,
    Console, Duel, DuelComponentResult, DuelMemberType, DuelStatus, DuelType,
    Game, GamePoints, Player, PlayerConsoles, PlayerStatus, User, PreDuel)
from playerstars_domain.duel.pre_duel import Status
from playerstars_domain.utils.datetime_helper import aware_utc


class Settings:
    LOG_LEVEL = 'DEBUG'
    CONSOLE_TABLE_NAME = 'console'
    DUEL_TABLE_NAME = 'duel'
    PLAYER_TABLE_NAME = 'player'
    PURCHASE_HISTORY_TABLE_NAME = 'purchase'
    REGION_COUNTRY_TABLE_NAME = 'region_country'
    REGION_STATE_TABLE_NAME = 'region_state'
    TEAM_TABLE_NAME = 'team'
    USER_TABLE_NAME = 'user'
    USER_ADMIN_TABLE_NAME = 'user_admin'
    NOTIFICATION_TABLE_NAME = 'notification'
    DYNAMODB_URL = None
    PAGSEGURO_RETURN_URL = 'http:localhost:8003/post_purchase'
    PURCHASE_OPERATION_TIMEOUT = 20
    PAGSEGURO_SANDBOX_ENABLE = True
    PAGSEGURO_EMAIL = 'felipe.duarte@pagseguro.com.br'
    PAGSEGURO_SANDBOX_TOKEN = \
        config('PAGSEGURO_SANDBOX_TOKEN', 'PAG-SEGURO-SANDBOX-123')
    PAGSEGURO_TOKEN = config('PAGSEGURO_TOKEN', 'PAG-SEGURO-123')
    RETURN_URL = 'http://pagina-de-retorno-do-front'
    PLAYERSTARS_NOTIFICATION_URL = \
        "http://pagina-para-onde-pagseguro-envia-update"
    PAGSEGURO_UPDATE_NOTIFICATION_URL = \
        "https://ws.sandbox.pagseguro.uol.com.br/v3/transactions/" \
        "notifications/code?email={email}&token={token}"
    S3_BUCKET_NAME = "playerstars-images"
    S3_BUCKET_URL = "http://bolao-abbr-images.s3-website-us-east-1." \
                    "amazonaws.com"
    TIME_TO_ACCEPTING_DUEL_INVITATION = '5'
    TIME_TO_FINISH_DUEL = '300'
    GRAPHQL_API_URL = config(
        'GRAPHQL_API_URL',
        'https://c7zo7ax3oze6rk3gko45hnjcpy.appsync-'
        'api.us-east-1.amazonaws.com/graphql')

    AWS_DEFAULT_REGION = 'us-east-1'
    GRAPHQL_API_ID = '3l2u7ok2cjfwdclv5qz3zb5z54'
    GRAPHQL_API_KEY = 'da2-xqu7fukowrcilcwoxvcjsrfawm'


player_json = {
    'entity_id': '',
    'red_star_balance': 15,
    'consoles': [{
        'console_id': '1',
        'tag_name': 'lols',
        "game_points": [{
            'game_id': '11',
            'victories': 0
        }]
    }],
    'countries_regions': ['id123'],
    'states_regions': ['id123'],
    'favorites': ['ght232141-3a12-5t67-19ehdufasuu'],
    'golden_star_balance': 0,
    'star_transactions': [{
        "value": 2,
        "operation_date": "2019-08-21T13:11:07+00:00",
        "coin_type": "GOLDEN_STAR",
        "operation_type": "DEBIT",
        "source": "DUEL",
        "source_id": "68dc45c5-43eb-4351-bead-4319aba7af85"
    }],
    "purchases": [{
        "product": {
            "price": 1050,
            "star_value": "3",
            "description": "teste teste teste",
            "star_type": "RED_STAR",
            "duration": 3
        },
        "purchase_type": "GOLDEN_STAR_PURCHASE",
        "purchase_datetime": "2017-11-21T09:58:00+00:00",
        "payment": {
            "code": "schrubles1241",
            "payment_datetime": "2017-11-22T09:58:00+00:00",
            "payment_type": "PAGSEGURO",
            "transactions": []
        }
    }],
    "user": {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "2018-11-11",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "city": "Rio de Janeiro",
        "state": "Rio de Janeiro",
        "country": "Brasil",
        "postal_code": "22333-000",
        "phone_number": "(21) 99663-6963",
        "cpf": "123.456.789-00",
        "nickname": "anselmo.lira",
        "profile_image": "http://bolao-abbr-images.s3-website-us-east-1."
                         "amazonaws.com/3371aa2b-ad8b-4d59-bd51-b71d0b03b"
                         "4ec-photo.jpeg"
    },
    "points": 300,
    "terms": True,
    "player_status": "OFFLINE"
}

team_json = {
    "captain": {
        "association_date": "2019-11-04T20:42:55.159301+00:00",
        "last_status_change_datetime": "2019-11-04T21:52:44.123456",
        "member_type": "CAPTAIN",
        "player_id": "2423e622-621b-4162-89c9-4e9e22d259d1",
        "status": "ACCEPTED"
    },
    "console_id": "a03be321-622c-4908-826c-2522f71a355e",
    "description": "Descrição do time",
    "entity_id": "04babb99-ce24-4970-9c67-def8366080de",
    "logo_path": "http://playerstars-dev-photos.s3-website-us-east-1.amazona"
    "ws.com/04babb99-ce24-4970-9c67-def8366080de-photo.jpeg",
    "members": [{
        "association_date": "2019-11-04T20:42:55.277663+00:00",
        "last_status_change_datetime": "2019-11-04T20:44:07.123456",
        "player_id": "9b8c1e9c-a872-46f8-8c72-ed5677f0374c",
        "status": "INVITED",
        "member_type": "MEMBER"
    }, {
        "association_date": "2019-11-04T20:42:55.320131+00:00",
        "last_status_change_datetime": "2019-11-04T21:13:13.131313",
        "player_id": "ecc4a0c8-329a-41e9-a069-a76fc27abb69",
        "status": "INVITED",
        "member_type": "MEMBER"
    }, {
        "association_date": "2019-11-04T20:42:55.159301+00:00",
        "last_status_change_datetime": "2019-11-04T21:52:44.123456",
        "member_type": "CAPTAIN",
        "player_id": "2423e622-621b-4162-89c9-4e9e22d259d1",
        "status": "ACCEPTED"
    }],
    "name": "OS BEBEDORES DE GROSELHA",
    "victories": 10,
    "status": "ACTIVE"
}


duel_json = {
    'bet_size': 200,
    'challenged': 'ecc4a0c8-329a-41e9-a069-a76fc27abb69',
    'challenger': '2423e622-621b-4162-89c9-4e9e22d259d1',
    'console': {
        'entity_id': 'abec7b9a-a410-4cc0-bdf1-1ac8e763c8aa',
        'logo_path': '/teste/atari.png',
        'name': 'Atari'
    },
    'entity_id': '14844ee5-454f-412e-89d4-fdb69cd46bf0',
    'game': {
        'entity_id': '3a793ed7-3558-4dc1-a310-676dc49d81fb',
        'logo_path': 'images/sonic.jpg',
        'name': 'Sonic'
    },
    'participants': 2,
    'star_type': 'GOLDEN_STAR',
    'status': 'LOBBY',
    'time_start': '2019-11-04T20:47:00.320655',
    "creation_datetime": "2019-11-04T20:45:15.012345",
    'total_reward': 400,
    'duel_type': 'individual',
    'member_type': 'player',
    "result_time": 30000,
    "response_time": 300
}


def make_game_data():
    return Game(name='Fifa 19',
                logo_path='/images/fifa19.png',
                entity_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
                points=0,
                victories=0)


def make_console_data():
    game_data = make_game_data()
    game_list = [game_data]
    return Console(entity_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
                   name='Playstation 4',
                   logo_path='/images/ps4.png',
                   games=game_list)


def make_game_points():
    return GamePoints(
        game_id='0e3bd0f7-e95c-4168-9083-f1859fa73902',
        victories=0)


def make_player_console():
    game_points_data = make_game_points()
    return PlayerConsoles(
        console_id='531f6ee2-dfef-458e-b918-ebf12793fe37',
        game_points=[game_points_data],
        tag_name='tag#1')


def make_player_data():
    user_data = User(name='Felipe Duarte',
                     email='felipe.duarte@stormsec.com.br',
                     date_birth=date(1990, 6, 5),
                     street='Rua Fortunato de Brito',
                     street_number='22',
                     street_complement='apto 101',
                     neighborhood='Freguesia',
                     city='Rio de Janeiro',
                     state='Rio de Janeiro',
                     country='Brasil',
                     postal_code='25520-012',
                     phone_number='(21) 98144-1317',
                     cpf='123.456.789-01',
                     nickname='aabbcc')
    player_data = Player(entity_id='f930959f-63ec-4478-89d6-7d84bb748b37',
                         user=user_data,
                         consoles=[make_player_console()],
                         red_star_balance=5,
                         golden_star_balance=5,
                         player_status=PlayerStatus.AVAILABLE,
                         states_regions=[],
                         favorites=[],
                         countries_regions=[],
                         points=800,
                         star_transactions=[],
                         star_reservations=[],
                         terms=True)
    return player_data


def make_game_data2():
    return Game(entity_id='90e3ac18-1634-4648-ac88-c86ee6dbeae9',
                name='Need for Speed',
                logo_path='/images/nfs.jpg')


def make_console_data2():
    game = make_game_data2()
    return Console(entity_id='415fed32-c2db-4607-b80c-2275d4587364',
                   name='Xbox One',
                   logo_path='/images/xbox_one.jpg',
                   tag_name='nick#1',
                   games=[game])


def make_player_console_2():
    game_points_data = GamePoints(
        game_id='90e3ac18-1634-4648-ac88-c86ee6dbeae9',
        victories=0)
    player_console_data = PlayerConsoles(
        console_id='415fed32-c2db-4607-b80c-2275d4587364',
        game_points=[game_points_data],
        tag_name='tag#3')
    return player_console_data


def make_player_1():
    console = make_player_console_2()
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
    return Player(entity_id='a1b2c3',
                  user=user_data,
                  consoles=[console],
                  red_star_balance=10,
                  golden_star_balance=10,
                  player_status=PlayerStatus.AVAILABLE,
                  terms=True)


def make_player_2():
    console = make_player_console_2()
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
    return Player(entity_id='q1w2e3r4',
                  user=user_data,
                  consoles=[console],
                  red_star_balance=15,
                  golden_star_balance=15,
                  player_status=PlayerStatus.AVAILABLE,
                  terms=True)


def make_duel_player_in_progress():
    game = make_game_data2()
    console = make_console_data2()

    duel = Duel(
        entity_id='f13eb50c',
        challenger=make_player_1().entity_id,
        challenged=make_player_2().entity_id,
        game=game,
        console=console,
        star_type=CoinType.GOLDEN_STAR,
        bet_size=3,
        time_start=aware_utc(datetime(1986, 12, 16, 15, 40, 8)),
        challenged_accept=False,
        status=DuelStatus.DUELING,
        duel_type=DuelType.INDIVIDUAL,
        member_type=DuelMemberType.PLAYER,
        time_to_finish_duel=300,
        time_to_accept_invitation=5)
    return duel


def make_duel_in_progress_with_results():
    duel_data = make_duel_player_in_progress()
    challenger_result = DuelComponentResult(result=ComponentResult.WINNER)
    challenged_result = DuelComponentResult(result=ComponentResult.LOSER)
    duel_data.challenger_duel_result = challenger_result
    duel_data.challenged_duel_result = challenged_result
    return duel_data


def make_duel_finished():
    game = make_game_data2()
    console = make_console_data2()

    duel = Duel(
        entity_id='f13eb50c',
        challenger=make_player_1().entity_id,
        challenged=make_player_2().entity_id,
        game=game,
        console=console,
        star_type=CoinType.GOLDEN_STAR,
        bet_size=3,
        time_start=aware_utc(datetime(1986, 12, 16, 15, 40, 8)),
        challenged_accept=False,
        status=DuelStatus.FINISHED_BY_VICTORY,
        duel_type=DuelType.INDIVIDUAL,
        member_type=DuelMemberType.PLAYER,
        time_to_finish_duel=300,
        time_to_accept_invitation=5)
    return duel


def make_duel_finished_with_results():
    duel_data = make_duel_finished()
    challenger_result = DuelComponentResult(result=ComponentResult.WINNER)
    challenged_result = DuelComponentResult(result=ComponentResult.LOSER)
    duel_data.challenger_duel_result = challenger_result
    duel_data.challenged_duel_result = challenged_result
    return duel_data


def make_duel_canceled():
    duel = make_duel_player_in_progress()
    duel.status = DuelStatus.CANCELED_BY_INCONSISTENT_RESULT
    return duel


def make_lambda_list_functions_result():
    return {
        'ResponseMetadata':
        {
            'RequestId': '1af68322-0967-41bc-88d6-cf328b19af9f',
            'HTTPStatusCode': 200,
            'HTTPHeaders':
            {
                'date': 'Thu, 23 Jan 2020 23:36:49 GMT',
                'content-type': 'application/json',
                'content-length': '2661',
                'connection': 'keep-alive',
                'x-amzn-requestid': '1af68322-0967-41bc-88d6-cf328b19af9f'
            },
            'RetryAttempts': 0
        },
        'Functions': [
            {
                'FunctionName': 'PlayerStars-dev-duel_scheduled_finisher',
                'FunctionArn': 'arn:aws:lambda:us-east-1:230639242520:'
                               'function:PlayerStars-dev-duel_scheduled_'
                               'finisher',
                'Runtime': 'python3.7',
                'Role': 'arn:aws:iam::230639242520:role/'
                        'PlayerStars-dev-duel_scheduled_finisher',
                'Handler': 'app.duel_finish_handler',
                'CodeSize': 10424770,
                'Description': '',
                'Timeout': 60,
                'MemorySize': 128,
                'LastModified': '2020-01-23T23:03:02.915+0000',
                'CodeSha256': '1GG6X5AHRnDw3JVF33ipieA5x7rAAmPBRzKdgoKG65A=',
                'Version': '$LATEST',
                'VpcConfig': {
                    'SubnetIds': [],
                    'SecurityGroupIds': [],
                    'VpcId': ''
                },
                'Environment':
                {
                    'Variables':
                    {
                        'PLAYER_TABLE_NAME': 'player',
                        'REGION_STATE_TABLE_NAME': 'region_state',
                        'USER_ADMIN_TABLE_NAME': 'user_admin',
                        'DUEL_TABLE_NAME': 'duel',
                        'PURCHASE_HISTORY_TABLE_NAME': 'purchase',
                        'REGION_COUNTRY_TABLE_NAME': 'region_country',
                        'USER_TABLE_NAME': 'user',
                        'CONSOLE_TABLE_NAME': 'console',
                        'DUEL_SCHEDULED_FINISHER_NAME':
                            'duel_scheduled_finisher',
                        'TEAM_TABLE_NAME': 'team',
                        'TIME_TO_FINISH_DUEL': '300',
                        'LOG_LEVEL': 'DEBUG'
                    }
                },
                'TracingConfig': {'Mode': 'PassThrough'},
                'RevisionId': '13adcad1-d9fd-4bd0-af18-7ce671766de7',
                'Layers': []
            },
            {
                'FunctionName': 'PlayerStars-dev',
                'FunctionArn': 'arn:aws:lambda:us-east-1:230639242520:'
                               'function:PlayerStars-dev',
                'Runtime': 'python3.7',
                'Role': 'arn:aws:iam::230639242520:role/'
                        'PlayerStars-dev-api_handler',
                'Handler': 'app.app',
                'CodeSize': 10424770,
                'Description': '',
                'Timeout': 60,
                'MemorySize': 128,
                'LastModified': '2020-01-23T23:03:04.615+0000',
                'CodeSha256': '1GG6X5AHRnDw3JVF33ipieA5x7rAAmPBRzKdgoKG65A=',
                'Version': '$LATEST',
                'VpcConfig':
                {
                    'SubnetIds': [],
                    'SecurityGroupIds': [],
                    'VpcId': ''
                },
                'Environment':
                {
                    'Variables':
                    {
                        'PLAYER_TABLE_NAME': 'player',
                        'REGION_STATE_TABLE_NAME': 'region_state',
                        'USER_ADMIN_TABLE_NAME': 'user_admin',
                        'DUEL_TABLE_NAME': 'duel',
                        'PURCHASE_HISTORY_TABLE_NAME': 'purchase',
                        'REGION_COUNTRY_TABLE_NAME': 'region_country',
                        'USER_TABLE_NAME': 'user',
                        'CONSOLE_TABLE_NAME': 'console',
                        'DUEL_SCHEDULED_FINISHER_NAME':
                            'duel_scheduled_finisher',
                        'TEAM_TABLE_NAME': 'team',
                        'TIME_TO_FINISH_DUEL': '300',
                        'LOG_LEVEL': 'DEBUG'
                    }
                },
                'TracingConfig': {'Mode': 'PassThrough'},
                'RevisionId': '64247274-b4a0-4525-bd6f-b8938a9b5845',
                'Layers': []
            }
        ]
    }


duel_game_1 = Game(
    entity_id="fca58cc9-8762-4bce-82be-6bf356defff0",
    name="Uncharted1",
    logo_path="images/uncharted.jpg")


duel_game_2 = Game(
    entity_id="fca58cc9-8762-4bce-82be-6bf356defff0",
    name="Uncharted2",
    logo_path="images/uncharted.jpg")


duel_game_3 = Game(
    entity_id="ac6ecbd4-1d3d-4ae9-89f6-d8a5e864e0e7",
    name="Xbox3",
    logo_path="/images/ss.png")


duel_console_1 = Console(
    entity_id="72042841-e7f4-4af2-aa2a-c319163243a2",
    name="Xbox1",
    logo_path="/images/ss.png",
    games=[duel_game_1])


duel_console_2 = Console(
    entity_id="ac6ecbd4-1d3d-4ae9-89f6-d8a5e864e0e7",
    name="Xbox2",
    logo_path="/images/ss.png")


duel_console_3 = Console(
    entity_id="fca58cc9-8762-4bce-82be-6bf356defff0",
    name="Uncharted3",
    logo_path="images/uncharted.jpg")


duel_1 = Duel(
    game=duel_game_1,
    console=duel_console_1,
    bet_size=190,
    time_start=aware_utc(datetime(2019, 10, 9, 20, 20, 20)),
    creation_datetime=aware_utc(datetime(2019, 10, 9, 20, 18, 9)),
    entity_id="75b30fa6-a321-4bf6-9296-3af70aab2bc5",
    total_reward=380,
    challenged="8f547626-d1f7-49a3-ba2e-eb7a7504ad22",
    challenger="7e436515-d1f7-49a3-ba2e-eb7a7504ad22",
    star_type=CoinType.RED_STAR,
    status=DuelStatus.FINISHED_BY_VICTORY,
    participants=2,
    challenger_confirmation=False,
    challenged_confirmation=False,
    challenged_accept=False,
    duel_type=DuelType.INDIVIDUAL,
    member_type=DuelMemberType.PLAYER,
    time_to_finish_duel=300,
    time_to_accept_invitation=5)


duel_2 = Duel(
    game=duel_game_2,
    console=duel_console_2,
    bet_size=190,
    time_start=aware_utc(datetime(2019, 10, 9, 20, 10, 50)),
    creation_datetime=aware_utc(datetime(2019, 10, 9, 20, 8, 35)),
    entity_id="7f12ac55-e942-4f3f-a6a2-13bd9d7a7bd3",
    total_reward=380,
    challenged='7e436515-d1f7-49a3-ba2e-eb7a7504ad22',
    challenged_accept=True,
    challenger="8f547626-d1f7-49a3-ba2e-eb7a7504ad22",
    star_type=CoinType.RED_STAR,
    status=DuelStatus.LOBBY,
    participants=2,
    challenger_confirmation=False,
    challenged_confirmation=False,
    duel_type=DuelType.INDIVIDUAL,
    member_type=DuelMemberType.PLAYER,
    time_to_finish_duel=300,
    time_to_accept_invitation=5)


duel_3 = Duel(
    console=duel_console_3,
    game=duel_game_3,
    bet_size=190,
    time_start=aware_utc(datetime(2019, 10, 9, 23, 23, 45)),
    creation_datetime=aware_utc(datetime(2019, 10, 9, 23, 20, 15)),
    entity_id="7f12ac55-e942-4f3f-a6a2-13bd9d7a7bd3",
    total_reward=380,
    challenged="7e436515-d1f7-49a3-ba2e-e43a7504ad22",
    challenged_accept=True,
    challenger="8f547626-d1f7-49a3-ba2e-eb7a7434ad22",
    star_type=CoinType.RED_STAR,
    status=DuelStatus.LOBBY,
    participants=2,
    challenger_confirmation=False,
    challenged_confirmation=False,
    duel_type=DuelType.INDIVIDUAL,
    member_type=DuelMemberType.TEAM,
    time_to_finish_duel=300,
    time_to_accept_invitation=5)


duel_list = [duel_1, duel_2, duel_3]


duel_team = Duel(
    console=duel_console_3,
    game=duel_game_3,
    bet_size=190,
    time_start=aware_utc(datetime(2019, 10, 9, 23, 23, 45)),
    creation_datetime=aware_utc(datetime(2019, 10, 9, 23, 20, 15)),
    entity_id="7f12ac55-e942-4f3f-a6a2-13bd9d7a7bd3",
    total_reward=380,
    challenged="7e436515-d1f7-49a3-ba2e-e43a7504ad22",
    challenged_accept=True,
    challenger="8f547626-d1f7-49a3-ba2e-eb7a7434ad22",
    star_type=CoinType.RED_STAR,
    status=DuelStatus.LOBBY,
    participants=2,
    challenger_confirmation=False,
    challenged_confirmation=False,
    duel_type=DuelType.INDIVIDUAL,
    member_type=DuelMemberType.TEAM,
    time_to_finish_duel=300,
    time_to_accept_invitation=5)

console_list = [
    PlayerConsoles(
        console_id='1', tag_name='tag#1',
        game_points=[
            GamePoints(game_id='9', victories=100),
            GamePoints(game_id='8', victories=200)]
    ),
    PlayerConsoles(
        console_id='2', tag_name='tag#3',
        game_points=[
            GamePoints(game_id='7', victories=300),
            GamePoints(game_id='6', victories=400)]
    )
]


user_1 = User(
    date_birth=date(1991, 3, 14),
    country="Brasil",
    street='Avenida Brasil',
    street_number='500',
    street_complement='apt 607',
    neighborhood='pechinchão',
    city="Rio de Janeiro",
    cpf="14217868774",
    name="Felipe Duarte",
    nickname="Zyzukab",
    phone_number="21991419397",
    state="RJ",
    postal_code="22770233",
    email="felipe.duarte@stormsec.com.br")

player_1 = Player(
    entity_id="8f547626-d1f7-49a3-ba2e-eb7a7504ad22",
    user=user_1,
    consoles=console_list,
    player_status=PlayerStatus.OFFLINE,
    states_regions=[],
    favorites=[],
    countries_regions=[],
    points=800,
    red_star_balance=90,
    golden_star_balance=100,
    star_transactions=[],
    star_reservations=[],
    terms=True,
    is_admin=False,
    is_blocked=False,
    elo_rating=1500.0)


user_2 = User(
    date_birth=date(1991, 3, 14),
    country="Brasil",
    street='Avenida Brasil',
    street_number='500',
    street_complement='apt 607',
    neighborhood='pechinchão',
    city="Rio de Janeiro",
    nickname="Zyzukab",
    cpf="14217868774",
    name="Felipe Duarte",
    phone_number="21991419397",
    state="RJ",
    postal_code="22770233",
    email="felipe.duarte@stormsec.com.br")
player_2 = Player(
    entity_id="7e436515-d1f7-49a3-ba2e-e43a7504ad22",
    user=user_2,
    consoles=console_list,
    player_status=PlayerStatus.OFFLINE,
    states_regions=[],
    favorites=[],
    countries_regions=[],
    points=800,
    red_star_balance=90,
    golden_star_balance=100,
    star_transactions=[],
    star_reservations=[],
    terms=True,
    is_admin=False,
    is_blocked=False)


user_3 = User(
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
player_3 = Player(
    entity_id="q1w2e3abc",
    user=user_3,
    consoles=console_list,
    player_status=PlayerStatus.AVAILABLE,
    states_regions=[],
    favorites=[],
    countries_regions=[],
    points=900,
    red_star_balance=130,
    golden_star_balance=275,
    star_transactions=[],
    star_reservations=[],
    terms=True,
    is_admin=False,
    is_blocked=False)


team_1_captain = TeamMember(
    player_id=player_1.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.CAPTAIN,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 937668)),
    last_status_change_datetime=aware_utc(
        datetime(2019, 10, 11, 17, 12, 21, 123456)),
    bet_amount=100)
team_1_member = TeamMember(
    player_id=player_2.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.MEMBER,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(
        datetime(2019, 10, 11, 17, 2, 45, 123456)),
    bet_amount=100)
team_1 = Team(
    entity_id="fe5c6aea-6928-4008-a08d-f90440983dd4",
    name="brazucas1",
    description="TESTE TES TESTES",
    captain=team_1_captain,
    members=[team_1_captain, team_1_member],
    game_id="0e3bd0f7-e95c-4168-9083-f1859fa73902",
    console_id="531f6ee2-dfef-458e-b918-ebf12793fe37")


team_2_captain = TeamMember(
    player_id=player_2.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.CAPTAIN,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(
        datetime(2019, 10, 11, 17, 8, 33, 123456)))
team_2_member = TeamMember(
    player_id=player_1.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.MEMBER,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 937668)),
    last_status_change_datetime=aware_utc(
        datetime(2019, 10, 11, 16, 53, 11, 123456)))
team_2 = Team(
    entity_id="fe5c6aea-6928-4008-a08d-f90440983dd2",
    name="brazucas2",
    description="TESTE TES TESTES",
    captain=team_2_captain,
    members=[team_2_captain, team_2_member])


team_3_captain = TeamMember(
    player_id=player_1.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.CAPTAIN,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 937668)),
    last_status_change_datetime=aware_utc(datetime(2019, 10, 12, 0, 11, 23)))
team_3_member = TeamMember(
    player_id=player_2.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.MEMBER,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(datetime(2019, 10, 11, 18, 1, 2)))
team_3 = Team(
    name="brazucas3",
    entity_id="fe5c6aea-6928-4008-a08d-f90440983dd3",
    description="TESTE TES TESTES",
    captain=team_3_captain,
    members=[team_3_captain, team_3_member],
    victories=3)


team_4_captain = TeamMember(
    player_id=player_3.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.CAPTAIN,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(datetime(2019, 10, 11, 18, 1, 2)))
team_4_member = TeamMember(
    player_id=player_2.entity_id,
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.MEMBER,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(datetime(2019, 10, 11, 18, 1, 2)))
team_4 = Team(
    name="brazucas4",
    entity_id="fe5c6aea-6928-4008-a08d-f90440983dd4",
    description="TESTE TES TESTES",
    captain=team_4_captain,
    members=[team_4_captain, team_4_member],
    victories=3)

team_5 = Team(
    name="brazucas5",
    entity_id="fe5c6aea-6928-4008-a08d-f90440983dd5",
    description="TESTE TES TESTES",
    captain=team_4_captain,
    members=[team_4_captain, team_4_member],
    victories=3)

team_list = [team_1, team_2, team_3, team_4]

team_list_with_1 = [team_2]

console_by_id = Console.from_json({
    "games": [{
        "victories": 0,
        "logo_path": "https://s2.glbimg.com/V7249rL9MNWhMckASzn9eXwS",
        "name": "FIFA 2019",
        "points": 0,
        "entity_id": "6086715d-8f78-41a3-810d-d15f42659005"
    }],
    "logo_path": "http://playerstars-dev-photos.s3-website-us-east-1",
    "name": "Playstation 4",
    "entity_id": "1",
    "tag_name": None
})


def make_duel_player_golden():
    game_1 = Game(entity_id='17dfe88b-482f-42e9-a3d1-b30f2a92ca78',
                  name='Need for Speed',
                  logo_path='http://s3.aws.com/nfs.jpg')
    game_2 = Game(entity_id='7ccd6553-aab2-4e41-9ea0-9edb6f4e96f8',
                  name='Sonic The Hedgehog',
                  logo_path='http://s3.aws.com/sonic.jpg')
    console = Console(entity_id='94aee28a-4d21-4f12-8f29-b2e5c00110fb',
                      name='Xbox One',
                      logo_path='http://s3.aws.com/xbox_one.jpg',
                      tag_name='nick#1',
                      games=[game_1, game_2])

    duel = Duel(
        entity_id='f13eb50c',
        status=DuelStatus.LOBBY,
        challenger='duelmember1',
        challenger_confirmation=True,
        challenged='duelmember2',
        member_type=DuelMemberType.PLAYER,
        game=game_1,
        console=console,
        star_type=CoinType.GOLDEN_STAR,
        bet_size=3,
        creation_datetime=aware_utc(datetime(2020, 5, 21, 17, 58, 0)),
        time_send_invitation=aware_utc(datetime(2020, 5, 21, 17, 58, 10)),
        time_start=None,
        challenged_accept=False,
        time_to_accept_invitation=5,
        time_to_finish_duel=300)
    return duel


def make_duel_team_golden():
    duel_data = make_duel_player_golden()
    duel_data.star_type = CoinType.GOLDEN_STAR
    duel_data.member_type = DuelMemberType.TEAM
    return duel_data


def make_duel_team_red():
    duel_data = make_duel_player_golden()
    duel_data.star_type = CoinType.RED_STAR
    duel_data.member_type = DuelMemberType.TEAM
    return duel_data


preduel_list = [
    PreDuel(
        status=Status.AWAITING,
        game_entity_id='game1234',
        console_entity_id='console123',
        duel_type=DuelMemberType.PLAYER,
        star_type=CoinType.GOLDEN_STAR,
        star_amount=5,
        challenger='player1',
        challenged=None,
        ack=False),
    PreDuel(
        status=Status.AWAITING,
        game_entity_id='game1234',
        console_entity_id='console123',
        duel_type=DuelMemberType.PLAYER,
        star_type=CoinType.RED_STAR,
        star_amount=10,
        challenger='player1',
        challenged='player3',
        ack=False),
    PreDuel(
        status=Status.AWAITING,
        game_entity_id='game1234',
        console_entity_id='console123',
        duel_type=DuelMemberType.PLAYER,
        star_type=CoinType.GOLDEN_STAR,
        star_amount=15,
        challenger='player2',
        challenged='player3',
        ack=False),
    PreDuel(
        status=Status.AWAITING,
        game_entity_id='game123456',
        console_entity_id='console123',
        duel_type=DuelMemberType.PLAYER,
        star_type=CoinType.RED_STAR,
        star_amount=10,
        challenger='player4',
        challenged='player5',
        ack=False)
]


team_1337_member = TeamMember(
    player_id='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
    status=MemberStatus.ACCEPTED,
    member_type=MemberType.MEMBER,
    association_date=aware_utc(datetime(2019, 10, 11, 16, 50, 9, 956180)),
    last_status_change_datetime=aware_utc(datetime(2019, 10, 11, 18, 1, 2)))

team_get_duels = Team(
    name="brazucas4",
    entity_id="duelmember2",
    description="TESTE TES TESTES",
    captain=team_4_captain,
    members=[team_4_captain, team_4_member, team_1337_member],
    victories=3)
