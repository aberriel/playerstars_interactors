from playerstars_interactors import (
    GetDuelInteractor,
    GetDuelRequestModel,
    GetDuelResponseModel)
from tests.duel.duel_utils import (
    make_player_1,
    make_team_1,
    make_team_2,
    make_duel_player_finished_to_compare,
    make_duel_team_finished_to_challenger_to_compare)
from unittest.mock import patch, MagicMock


prefix = 'playerstars_interactors.duel.get_duel'


duel_adapter_player = MagicMock(
    get_by_id=MagicMock(return_value=make_duel_player_finished_to_compare()))
duel_adapter_team = MagicMock(
    get_by_id=MagicMock(return_value=make_duel_team_finished_to_challenger_to_compare()))
player_adapter = MagicMock(get_by_id=MagicMock(return_value=make_player_1()))
team_adapter = MagicMock(get_by_id=MagicMock(return_value=make_team_1()))


def make_get_duel_request_json(duel_id, player_id):
    return {'duel_id': duel_id, 'player_id': player_id}


@patch(f'{prefix}.aware_now')
def test_get_duel(mock_datetime):
    request_json = make_get_duel_request_json(
        duel_id='f13eb50c',
        player_id='51ee013a-d7eb-428d-a856-8d5b2853a68e')
    request = GetDuelRequestModel(request_json)
    interactor = GetDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_player,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    response = interactor.run()
    assert response
    assert isinstance(response, GetDuelResponseModel)
    assert response() == {
        "challenger": {
            "entity_id": "51ee013a-d7eb-428d-a856-8d5b2853a68e",
            "name": "zyzukab",
            "image": None,
            "tag_name": "tag#1"},
        "challenger_confirmation": True,
        "challenger_duel_result": {
            "result": "LOSER",
            "result_image": 'bucket_url/placar.jpg',
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "challenged": {
            "entity_id": "8734e07d-d629-458c-bc18-2b4be326fc84",
            "name": "zyzukab",
            "image": None,
            "tag_name": "tag#1"},
        "challenged_confirmation": True,
        "challenged_duel_result": {
            "result": "WINNER",
            "result_image": 'bucket_url/placar.jpg',
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "console": {
            "logo_path": "http://s3.aws.com/xbox_one.jpg",
            "entity_id": "94aee28a-4d21-4f12-8f29-b2e5c00110fb",
            "games": [],
            "name": "Xbox One",
            "tag_name": "nick#1"},
        "status": "FINISHED_BY_VICTORY",
        "championship_level": None,
        "challenged_last_duel": None,
        "championship": None,
        "duel_type": "INDIVIDUAL",
        "member_type": "PLAYER",
        "entity_id": "f13eb50c",
        "creation_datetime": "1986-12-16T15:40:08+00:00",
        "time_start": "1986-12-16T15:40:08+00:00",
        "time_send_invitation": None,
        "time_finish": None,
        "time_cancel": None,
        "time_to_finish_duel": 300,
        "time_to_accept_invitation": 5,
        "challenged_accept": False,
        "challenger_last_duel": None,
        "participants": 2,
        "winner": "51ee013a-d7eb-428d-a856-8d5b2853a68e",
        "game": {
            'entity_id': '17dfe88b-482f-42e9-a3d1-b30f2a92ca78',
            'name': 'Need for Speed',
            'logo_path': 'http://s3.aws.com/nfs.jpg',
            'points': 0,
            'victories': 0,
            'tutorial': None,
            'mask': None,
            'game_type': 'BOTH',
            'active': True},
        "star_type": "GOLDEN_STAR",
        "bet_size": 3,
        "total_reward": 6,
        "current_server_time": mock_datetime().isoformat(),
        "challenger_duel_info": None,
        "challenged_duel_info": None}


@patch(f'{prefix}.GetDuelInteractor.get_challenger',
       return_value=make_team_1())
@patch(f'{prefix}.GetDuelInteractor.get_challenged',
       return_value=make_team_2())
@patch(f'{prefix}.aware_now')
def test_get_duel_team_challenger(
        mock_datetime, get_challenged, get_challenger):
    request_json = make_get_duel_request_json(
        duel_id='f13eb50c',
        player_id='8734e07d-d629-458c-bc18-2b4be326fc84')
    request = GetDuelRequestModel(request_json)
    interactor = GetDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_team,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    response = interactor.run()
    assert response
    assert isinstance(response, GetDuelResponseModel)
    assert response() == {
        "challenger": {
            "entity_id": "02c8a4b5-33cf-4b28-b618-0e7cb9d6707e",
            "name": "Brazucas",
            "image": None,
            "tag_name": "tag#1"},
        "challenger_confirmation": True,
        "challenger_duel_result": {
            "result": "WINNER",
            "result_image": "bucket_url/placar.jpg",
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "challenged": {
            "entity_id": "6d3cbd57-974c-4559-a363-eee8d88ba17e",
            "name": "Vascuuu",
            "image": None,
            "tag_name": "tag#1"},
        "challenged_confirmation": True,
        "challenged_duel_result": {
            "result": "LOSER",
            "result_image": "bucket_url/placar.jpg",
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "player_team": "02c8a4b5-33cf-4b28-b618-0e7cb9d6707e",
        "console": {
            "logo_path": "http://s3.aws.com/xbox_one.jpg",
            "entity_id": "94aee28a-4d21-4f12-8f29-b2e5c00110fb",
            "games": [],
            "name": "Xbox One",
            "tag_name": "nick#1"},
        "status": "FINISHED_BY_VICTORY",
        "championship_level": None,
        "challenged_last_duel": None,
        "championship": None,
        "duel_type": "INDIVIDUAL",
        "member_type": "TEAM",
        "entity_id": "f13eb50c",
        "creation_datetime": "1986-12-16T15:40:08+00:00",
        "time_start": "1986-12-16T15:40:08+00:00",
        "time_send_invitation": None,
        "time_finish": None,
        "time_cancel": None,
        "time_to_finish_duel": 300,
        "time_to_accept_invitation": 5,
        "challenged_accept": False,
        "challenger_last_duel": None,
        "participants": 2,
        "winner": "02c8a4b5-33cf-4b28-b618-0e7cb9d6707e",
        "game": {
            'entity_id': '17dfe88b-482f-42e9-a3d1-b30f2a92ca78',
            'name': 'Need for Speed',
            'logo_path': 'http://s3.aws.com/nfs.jpg',
            'points': 0,
            'victories': 0,
            'tutorial': None,
            'mask': None,
            'game_type': 'BOTH',
            'active': True},
        "star_type": "GOLDEN_STAR",
        "bet_size": 3,
        "total_reward": 6,
        "current_server_time": mock_datetime().isoformat(),
        "challenger_duel_info": None,
        "challenged_duel_info": None}


@patch(f'{prefix}.GetDuelInteractor.get_challenger',
       return_value=make_team_1())
@patch(f'{prefix}.GetDuelInteractor.get_challenged',
       return_value=make_team_2())
@patch(f'{prefix}.aware_now')
def test_get_duel_team_challenged(
        mock_datetime, get_challenged, get_challenger):
    request_json = make_get_duel_request_json(
        duel_id='f13eb50c',
        player_id='af1bf976-b212-42a9-af2a-fc20ed4688de')
    request = GetDuelRequestModel(request_json)
    interactor = GetDuelInteractor(
        request=request,
        duel_adapter=duel_adapter_team,
        player_adapter=player_adapter,
        team_adapter=team_adapter)

    response = interactor.run()
    assert response
    assert isinstance(response, GetDuelResponseModel)
    assert response() == {
        "challenger": {
            "entity_id": "02c8a4b5-33cf-4b28-b618-0e7cb9d6707e",
            "name": "Brazucas",
            "image": None,
            "tag_name": "tag#1"},
        "challenger_confirmation": True,
        "challenger_duel_result": {
            "result": "WINNER",
            "result_image": "bucket_url/placar.jpg",
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "challenged": {
            "entity_id": "6d3cbd57-974c-4559-a363-eee8d88ba17e",
            "name": "Vascuuu",
            "image": None,
            "tag_name": "tag#1"},
        "challenged_confirmation": True,
        "challenged_duel_result": {
            "result": "LOSER",
            "result_image": "bucket_url/placar.jpg",
            "submission_datetime": "2020-01-15T18:01:13+00:00"},
        "player_team": "6d3cbd57-974c-4559-a363-eee8d88ba17e",
        "console": {
            "logo_path": "http://s3.aws.com/xbox_one.jpg",
            "entity_id": "94aee28a-4d21-4f12-8f29-b2e5c00110fb",
            "games": [],
            "name": "Xbox One",
            "tag_name": "nick#1"},
        "status": "FINISHED_BY_VICTORY",
        "championship_level": None,
        "challenged_last_duel": None,
        "championship": None,
        "duel_type": "INDIVIDUAL",
        "member_type": "TEAM",
        "entity_id": "f13eb50c",
        "creation_datetime": "1986-12-16T15:40:08+00:00",
        "time_start": "1986-12-16T15:40:08+00:00",
        "time_send_invitation": None,
        "time_finish": None,
        "time_cancel": None,
        "time_to_finish_duel": 300,
        "time_to_accept_invitation": 5,
        "challenged_accept": False,
        "challenger_last_duel": None,
        "participants": 2,
        "winner": "02c8a4b5-33cf-4b28-b618-0e7cb9d6707e",
        "game": {
            'entity_id': '17dfe88b-482f-42e9-a3d1-b30f2a92ca78',
            'name': 'Need for Speed',
            'logo_path': 'http://s3.aws.com/nfs.jpg',
            'points': 0,
            'victories': 0,
            'tutorial': None,
            'mask': None,
            'game_type': 'BOTH',
            'active': True},
        "star_type": "GOLDEN_STAR",
        "bet_size": 3,
        "total_reward": 6,
        "current_server_time": mock_datetime().isoformat(),
        "challenger_duel_info": None,
        "challenged_duel_info": None}


duel_empty_adapter = MagicMock(get_by_id=MagicMock(return_value=None))


def test_get_duel_not_found():
    request_json = make_get_duel_request_json('duel123', 'player123')
    request = GetDuelRequestModel(request_json)
    interactor = GetDuelInteractor(
        request=request,
        duel_adapter=duel_empty_adapter,
        player_adapter=player_adapter,
        team_adapter=team_adapter)
    response = interactor.run()
    assert isinstance(response, GetDuelResponseModel)

    response_dict = response()
    assert response_dict is None
