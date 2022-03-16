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
    Player,
    PlayerConsoles,
    PlayerStatus,
    User,
    Tournament,
    TournamentMember,
    TournamentMemberStatus,
    TournamentStatus)

post_data = {
    "entity_id": '',
    "red_star_balance": 15,
    "consoles": [{
        "entity_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "entity_id": '123',
            "victories": 400
        }]
    }],
    "countries_regions": ["id123"],
    "states_regions": ["id123"],
    "favorites": ["ght232141-3a12-5t67-19ehdufasuu"],
    "golden_star_balance": 0,
    "star_transactions": [{
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
            "star_type": "red",
            "duration": 3
        },
        "purchase_type": "GOLDEN_STAR_PURCHASE",
        "purchase_datetime": "2017-11-21T09:58:00+00:00",
        "payment": {
            "code": "schrubles123",
            "payment_datetime": "2017-11-22T09:58:00+00:00",
            "payment_type": "PAGSEGURO",
            "transactions": []
        }
    }],
    "user": {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "11/11/1997",
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
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAA"
                         "DUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    },
    "player_status": "OFFLINE",
    "terms": True,
    "points": 200
}

console_data = Console(
    entity_id='1',
    logo_path='ahashiaudhaisas',
    tag_name='Leoplay4',
    name='schrubles',
    games=[
        Game(
            entity_id='123',
            name='pepsi',
            victories=0,
            points=0,
            logo_path='ahsiauhsiuas')
    ])


data_post_friends = {
    "user": {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "1986-12-16",
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
        "profile_image": "ACCBB4762CF23AA35690CC"
    },
    "favorites": [],
    "player_status": "OFFLINE",
    "red_star_balance": 123,
    "golden_star_balance": 4321,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": '123',
            "victories": 400
        }]
    }],
    "states_regions": [],
    "countries_regions": [],
    "entity_id": "player_id_005",
    "points": 1200,
    "star_transactions": [],
    "terms": True
}


player1 = Player(
    entity_id='1',
    red_star_balance=15,
    consoles=[
        PlayerConsoles(
            console_id='1',
            tag_name='Leoplay4',
            game_points=[
                GamePoints(game_id='f16c9f9a-9b22-4884-b890-bcc3294e91be',
                           victories=10,
                           elo_rating=5000)])],
    favorites=['121324', '1231413123'],
    golden_star_balance=0,
    user=User(
        name="Anselmo Lira",
        email="playerstars@playerstars.com.br",
        date_birth=date(2018, 11, 11),
        street='Avenida Brasil',
        street_number='500',
        street_complement='apt 607',
        neighborhood='pechinchão',
        city="Rio de Janeiro",
        state="Rio de Janeiro",
        country="Brasil",
        postal_code="22333-000",
        phone_number="(21) 99663-6963",
        cpf="123.456.789-00",
        nickname="player1",
        profile_image="iVBORw0KGgoAAAANSUhEUgAA"
    ),
    points=100,
    terms=True,
    player_status=PlayerStatus.OFFLINE)

player2 = Player.from_json({
    "entity_id": '2',
    "red_star_balance": 15,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 40,
            "elo_rating": 4000
        }]
    }],
    "favorites": [],
    "golden_star_balance": 0,
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
        "nickname": "player2",
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAA"
    },
    "points": 400,
    "terms": True,
    "player_status": "OFFLINE"
})

player3 = Player.from_json({
    "entity_id": '3',
    "red_star_balance": 15,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 30,
            "elo_rating": 3000
        }]
    }],
    "favorites": [],
    "golden_star_balance": 0,
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
        "nickname": "player3",
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAA"
    },
    "points": 300,
    "terms": True,
    "player_status": "OFFLINE"
})

player4 = Player.from_json({
    "entity_id": '4',
    "red_star_balance": 15,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 5,
            "elo_rating": 2000
        }]
    }],
    "favorites": [],
    "golden_star_balance": 0,
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
        "nickname": "player4",
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAA"
    },
    "points": 300,
    "terms": True,
    "player_status": "OFFLINE"
})

player5 = Player.from_json({
    "entity_id": '5',
    "red_star_balance": 15,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 300
        }]
    }],
    "favorites": [],
    "golden_star_balance": 0,
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
        "nickname": "player5",
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAA"
    },
    "points": 300,
    "terms": True,
    "player_status": "OFFLINE"
})

player6 = Player.from_json({
    "entity_id": '6',
    "red_star_balance": 15,
    "consoles": [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 30
        }]
    }],
    "favorites": [],
    "golden_star_balance": 0,
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
        "nickname": "player6",
        "profile_image": "iVBORw0KGgoAAAANSUhEUgAA"
    },
    "points": 30,
    "terms": True,
    "player_status": "OFFLINE"
})

console = Console(
    entity_id='1',
    logo_path="/images/ss.png",
    name="Playstation 4",
    tag_name="Leoplay4",
    games=[
        Game(entity_id="id1234",
             logo_path="images/sonic.jpg",
             name="Sonic"),
        Game(entity_id="f16c9f9a-9b22-4884-b890-bcc3294e91be",
             logo_path="images/sonic.jpg",
             name="Sonic",
             points=0,
             victories=0),
        Game(entity_id="6411df96-799b-4e6d-84f6-f277cff016e7",
             logo_path="images/sonic.jpg",
             name="teste",
             points=0,
             victories=0)
    ]
)


console_lol = Console(name='PC',
                      entity_id='c5a73eaa-9c87-4c32-9a49-05125fb79387',
                      logo_path='images/LOL.jpg')
game_lol = Game(name='LOL',
                entity_id='6411df96-799b-4e6d-84f6-f277cff016e7',
                logo_path='/images/lol.png')

console_sonic = Console(name='PC',
                        entity_id='c5a73eaa-9c87-4c32-9a49-05125fb79387',
                        logo_path='images/sonic.jpg')
game_csgo = Game(name='CS:GO',
                 entity_id='6411df96-799b-4e6d-84f6-f277cff016e7',
                 logo_path='/images/csgo.png')


duel1 = Duel(console=console_sonic,
             game=game_csgo,
             challenger='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged_accept=False,
             entity_id='66225276-03b5-487c-9b27-8e91e0fe1e12',
             status=DuelStatus.FINISHED_BY_VICTORY,
             time_start=datetime(1986, 12, 16, 15, 40, 8),
             creation_datetime=datetime(1986, 12, 16, 15, 37, 12),
             bet_size=15,
             star_type=CoinType.RED_STAR,
             challenged_confirmation=False,
             challenger_confirmation=False,
             participants=2,
             total_reward=30,
             winner='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             duel_type=DuelType.INDIVIDUAL,
             member_type=DuelMemberType.PLAYER,
             time_to_finish_duel=300,
             time_to_accept_invitation=5)
duel1_lobby = Duel(console=console_sonic,
                   game=game_csgo,
                   challenger='7e436515-d1f7-49a3-ba2e-eb7a7504ad22',
                   challenged='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
                   challenged_accept=False,
                   entity_id='66225276-03b5-487c-9b27-8e91e0fe1e12',
                   status=DuelStatus.LOBBY,
                   time_start=datetime(1986, 12, 16, 15, 40, 8),
                   creation_datetime=datetime(1986, 12, 16, 15, 37, 1),
                   bet_size=15,
                   star_type=CoinType.RED_STAR,
                   challenged_confirmation=False,
                   challenger_confirmation=False,
                   participants=2,
                   total_reward=30,
                   winner='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
                   duel_type=DuelType.INDIVIDUAL,
                   member_type=DuelMemberType.PLAYER,
                   time_to_finish_duel=300,
                   time_to_accept_invitation=5)


duel2 = Duel(console=console_lol,
             game=game_lol,
             challenger='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged_accept=False,
             entity_id='55d2737c-d7ac-4084-9bcf-d42954e1938c',
             status=DuelStatus.FINISHED_BY_VICTORY,
             time_start=datetime(1558, 2, 21, 15, 40, 8),
             creation_datetime=datetime(1558, 2, 21, 15, 38, 44),
             star_type=CoinType.GOLDEN_STAR,
             winner='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             bet_size=90,
             challenged_confirmation=False,
             challenger_confirmation=False,
             participants=2,
             total_reward=180,
             duel_type=DuelType.INDIVIDUAL,
             member_type=DuelMemberType.PLAYER,
             time_to_finish_duel=300,
             time_to_accept_invitation=5)


duel3 = Duel(console=console_lol,
             game=game_lol,
             challenger='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged_accept=False,
             entity_id='980001de-368e-4486-a6e5-379fbe4120f1',
             status=DuelStatus.LOBBY,
             time_start=datetime(1558, 2, 21, 15, 40, 8),
             creation_datetime=datetime(1550, 2, 21, 15, 39, 22),
             star_type=CoinType.GOLDEN_STAR,
             winner=None,
             bet_size=30,
             challenged_confirmation=False,
             challenger_confirmation=False,
             participants=2,
             total_reward=60,
             duel_type=DuelType.INDIVIDUAL,
             member_type=DuelMemberType.PLAYER,
             time_to_finish_duel=300,
             time_to_accept_invitation=5)


duel4 = Duel(console=console_lol,
             game=game_lol,
             challenger='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged_accept=False,
             entity_id='325c47c4-1cc0-49c7-8b85-a35f032cbf25',
             status=DuelStatus.CANCELED_BY_INCONSISTENT_RESULT,
             time_start=datetime(2020, 1, 10, 15, 40, 8),
             creation_datetime=datetime(2020, 1, 10, 15, 35, 55),
             star_type=CoinType.GOLDEN_STAR,
             winner=None,
             bet_size=7,
             challenged_confirmation=False,
             challenger_confirmation=False,
             participants=2,
             total_reward=14,
             duel_type=DuelType.INDIVIDUAL,
             member_type=DuelMemberType.PLAYER,
             time_to_finish_duel=300,
             time_to_accept_invitation=5)


duel_status_dueling = Duel(
    console=console_sonic,
    game=game_csgo,
    challenger='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
    challenged='7e436515-d1f7-49a3-ba2e-eb7a7504ad22',
    challenged_accept=False,
    entity_id='66225276-03b5-487c-9b27-8e91e0fe1e12',
    status=DuelStatus.DUELING,
    time_start=datetime(1986, 12, 16, 15, 40, 8),
    creation_datetime=datetime(1986, 12, 16, 15, 37, 22),
    bet_size=15,
    star_type=CoinType.RED_STAR,
    challenged_confirmation=False,
    challenger_confirmation=False,
    participants=2,
    total_reward=30,
    winner=None,
    duel_type=DuelType.INDIVIDUAL,
    member_type=DuelMemberType.PLAYER,
    time_to_finish_duel=300,
    time_to_accept_invitation=5)


duel5 = Duel(console=console_lol,
             game=game_lol,
             challenger='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged='56436515-d1f7-49a3-ba2e-eb7a7504ad22',
             challenged_accept=False,
             entity_id='65d2737c-d7ac-4084-9bcf-d42954e1938c',
             status=DuelStatus.FINISHED_BY_VICTORY,
             time_start=datetime(1558, 2, 21, 15, 40, 8),
             creation_datetime=datetime(1558, 2, 21, 15, 36, 21),
             star_type=CoinType.GOLDEN_STAR,
             winner='7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
             bet_size=90,
             challenged_confirmation=False,
             challenger_confirmation=False,
             participants=2,
             total_reward=180,
             duel_type=DuelType.INDIVIDUAL,
             member_type=DuelMemberType.PLAYER,
             time_to_finish_duel=300,
             time_to_accept_invitation=5)


tourney_member_1 = TournamentMember(
    member_id='schrubles1234',
    status=TournamentMemberStatus.ACCEPTED
)


tourney_member_2 = TournamentMember(
    member_id='schrubles5678',
    status=TournamentMemberStatus.ACCEPTED
)

tourney_member_3 = TournamentMember(
    member_id='schrubles5678',
    status=TournamentMemberStatus.OWNER
)


tournament = Tournament(
    game=game_lol,
    console=console_lol,
    award_first_place_perc=70,
    award_second_place_perc=20,
    award_third_place_perc=10,
    price_to_enter=30,
    member_amount=16,
    level_duration=120,
    levels_per_day=2,
    start_datetime=datetime(2020, 7, 23, 18, 34, 6, 138139),
    members=[tourney_member_1, tourney_member_2, tourney_member_3],
    status=TournamentStatus.WAITING_START,
    creation_datetime=datetime(2020, 7, 21, 18, 34, 6, 138139)
)
