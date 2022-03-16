from playerstars_domain import Console


def make_console_list_from_database():
    console_list = make_json_console_list()
    list_dict_consoles = [Console.from_json(x) for x in console_list]

    return list_dict_consoles


def make_json_console_list():
    return [
        {
            "tag_name": "nick#1",
            "entity_id": "11",
            "games":
            [
                {
                    "name": "Sonic",
                    "entity_id": "1",
                    "logo_path": "/images/sonic.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "GTA V",
                    "entity_id": "2",
                    "logo_path": "/images/gta5.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "FIFA 19",
                    "entity_id": "3",
                    "logo_path": "images/fifa19.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                }
            ],
            "name": "Xbox One",
            "logo_path": "/images/xbox.png"
        },
        {
            "tag_name": "nick#2",
            "entity_id": "id1234",
            "games": [
                {
                    "name": "GTA V",
                    "entity_id": "2",
                    "logo_path": "/images/gta5.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "FIFA 19",
                    "entity_id": "3",
                    "logo_path": "images/fifa19.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "Fortnite",
                    "entity_id": "4",
                    "logo_path": "/images/fortnite.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                }],
            "name": "PS 4",
            "logo_path": "/images/ps4.png"
        },
        {
            "tag_name": "nick#3",
            "entity_id": "13",
            "games": [
                {
                    "name": "Sonic",
                    "entity_id": "1",
                    "logo_path": "/images/sonic.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "GTA V",
                    "entity_id": "2",
                    "logo_path": "/images/gta5.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "FIFA 19",
                    "entity_id": "3",
                    "logo_path": "images/fifa19.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                },
                {
                    "name": "Fortnite",
                    "entity_id": "4",
                    "logo_path": "/images/fortnite.png",
                    "points": 0,
                    "victories": 0,
                    "active": True
                }
            ],
            "name": "Nintendo Switch",
            "logo_path": "/images/nintendo.png"
        }
    ]


def make_game_get_all_result():
    return [{
        "name": "GTA V",
        "entity_id": "2",
        "logo_path": "/images/gta5.png",
        "points": 0,
        "victories": 0,
        "tutorial": None,
        'game_type': 'BOTH',
        'mask': None,
        'active': True
    }, {
        "name": "FIFA 19",
        "entity_id": "3",
        "logo_path": "images/fifa19.png",
        "points": 0,
        "victories": 0,
        "tutorial": None,
        'game_type': 'BOTH',
        'mask': None,
        'active': True
    }, {
        "name": "Fortnite",
        "entity_id": "4",
        "logo_path": "/images/fortnite.png",
        "points": 0,
        "victories": 0,
        "tutorial": None,
        'game_type': 'BOTH',
        'mask': None,
        'active': True
    }]


def make_game_data():
    return dict(
        entity_id='1',
        name='Sonic',
        logo_path='/images/sonic.png',
        points=0,
        victories=0,
        tutorial=None,
        game_type='BOTH',
        mask=None,
        active=True)


def make_console_by_id():
    return Console.from_json({
        "tag_name": "nick#2",
        "entity_id": "id1234",
        "games": [
            {
                "name": "GTA V",
                "entity_id": "2",
                "logo_path": "/images/gta5.png",
                'points': 0,
                "victories": 0,
                'mask': None,
                'active': True
            },
            {
                "name": "FIFA 19",
                "entity_id": "3",
                "logo_path": "images/fifa19.png",
                'points': 0,
                "victories": 0,
                'mask': None,
                'active': True
            },
            {
                "name": "Fortnite",
                "entity_id": "4",
                "logo_path": "/images/fortnite.png",
                'points': 0,
                "victories": 0,
                'mask': None,
                'active': True
            }],
        "name": "PS 4",
        "logo_path": "/images/ps4.png"
    })


def make_console_no_games():
    return Console.from_json({
        'tag_name': 'nick#2',
        'entity_id': 'id1234',
        'games': [],
        'name': 'PS 4',
        'logo_path': '/images/ps4.png'
    })
