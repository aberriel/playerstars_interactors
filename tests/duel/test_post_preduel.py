from playerstars_interactors import \
    PostPreDuelInteractor, PostPreDuelRequestModel, PostPreDuelException
from unittest.mock import MagicMock, patch
from tests.util_tests import player_1, player_2, preduel_list
from tests.duel.duel_utils import \
    preduel_red_star_created, preduel_red_star_team_created, make_team_1
from playerstars_domain import GamePoints, PlayerConsoles
from playerstars_domain import PreDuel, Player
import pytest


def json_data(st, sa=5, pid='schrubles', gei='9', cei='801202', dt='PLAYER'):
    dic = {
        'player_id': pid,
        'game_entity_id': gei,
        'console_entity_id': cei,
        'star_amount': sa,
        'star_type': 'GOLDEN_STAR' if st == 'gold' else 'RED_STAR',
        'duel_type': dt
    }
    if st == 'red':
        del dic['star_amount']
    return dic


def get_interactor(json_dt, preduel=list(), player=player_1, team=list()):

    preduel_adapter = MagicMock(filter=MagicMock(return_value=preduel))
    player_adapter = MagicMock(get_by_id=MagicMock(return_value=player))
    team_adapter = MagicMock(get_by_id=MagicMock(return_Value=team))

    request = PostPreDuelRequestModel(json_dt)

    return PostPreDuelInteractor(
        request, preduel_adapter, player_adapter, team_adapter)


def test_post_preduel_create_preduel():
    interactor = get_interactor(json_data('gold'))
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'created'
    interactor.preduel_adapter.save.assert_called_once()


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_join_preduel(msg):
    interactor = get_interactor(
        json_data('gold'), preduel=preduel_list, player=player_2)
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'joined'
    interactor.preduel_adapter.save.assert_called_once()


def test_post_preduel_create_preduel_red_star():
    interactor = get_interactor(json_data('red'))
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'created'
    interactor.preduel_adapter.save.assert_called_once()


def test_post_preduel_player_without_game():
    interactor = get_interactor(json_data('gold', gei='912313'))
    with pytest.raises(PostPreDuelException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == \
        'Error during preduel creation: Player 8f547626-d1f7-49a3-ba2e-' \
        'eb7a7504ad22 não tem o jogo 912313 para criar esse duelo'


def test_post_preduel_player_without_balance():
    interactor = get_interactor(json_data('gold', sa=511111111, cei='912313'))
    with pytest.raises(PostPreDuelException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Error during preduel creation: Player ' \
                                 '8f547626-d1f7-49a3-ba2e-eb7a7504ad22 não ' \
                                 'tem GOLDEN_STAR suficientes para criar o ' \
                                 'duelo.'


json_data4 = {
    'player_id': 'schrubles',
    'game_entity_id': '912313',
    'console_entity_id': '801202',
    'star_type': 'GOLDEN_STAR',
    'duel_type': 'PLAYER'
}


def test_post_preduel_player_golden_without_star_amount():
    interactor = get_interactor(json_data4)
    with pytest.raises(PostPreDuelException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == \
        'Error during preduel creation: Preduels with golden stars need' \
        ' to inform star amount'


json_data5 = {
    'player_id': 'schrubles',
    'game_entity_id': '9',
    'console_entity_id': '801202',
    'star_amount': 1231,
    'star_type': 'RED_STAR',
    'duel_type': 'PLAYER'
}


def test_post_preduel_player_red_with_star_amount():
    interactor = get_interactor(json_data5)
    with pytest.raises(PostPreDuelException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == \
        'Error during preduel creation: Preduels with red stars should ' \
        'not inform star amount'


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_join_preduel_red_star(msg):
    interactor = get_interactor(
        json_data('red', dt='PLAYER'), player=player_2,
        preduel=[preduel_red_star_created()])
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'joined'
    interactor.preduel_adapter.save.assert_called_once()


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_join_preduel_no_condition(msg):
    player = Player.from_json(player_2.to_json())
    player.consoles.append(PlayerConsoles(
        console_id='24', tag_name='tag#3',
        game_points=[GamePoints(game_id='1337', victories=300)]))
    player.golden_star_balance = 12354123
    interactor = get_interactor(
        json_data('gold', gei='1337', cei='24', dt='PLAYER', sa=1234),
        player=player, preduel=preduel_list)
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'created'
    interactor.preduel_adapter.save.assert_called_once()


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_join_preduel_same_player(msg):
    interactor = get_interactor(
        json_data('red', gei='9', dt='PLAYER'), player=player_2,
        preduel=[preduel_red_star_created('schrubles')])
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'created'
    assert interactor.preduel_adapter.save.call_count == 2


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_team_join_preduel_raises(msg):
    interactor = get_interactor(
        json_data('red', dt='TEAM'), player=player_2, team=make_team_1(),
        preduel=[preduel_red_star_team_created()])
    with pytest.raises(PostPreDuelException) as excinfo:
        interactor.run()
    assert 'Error during preduel creation: Preduels for teams should have' \
           ' the team id in the request' == str(excinfo.value)


@patch('playerstars_interactors.duel.post_preduel.send_message')
def test_post_preduel_team_join_preduel_red_star(msg):
    team_json = json_data('red', dt='TEAM')
    team_json.update({'team_id': 'schrubles'})
    interactor = get_interactor(
        team_json, player=player_2, team=make_team_1(),
        preduel=[preduel_red_star_team_created()])
    assert isinstance(interactor.create_preduel(), PreDuel)
    response = interactor.run()
    assert response()
    assert response()[1] == 'joined'
    interactor.preduel_adapter.save.assert_called_once()
