from playerstars_domain import DuelStatus
from playerstars_interactors import (
    EndDuelLambdaException,
    EndDuelLambdaInteractor,
    EndDuelLambdaRequestModel,
    EndDuelLambdaResponseModel)
from playerstars_interactors.duel import DuelSettlementTaskPlayer
from tests.duel.duel_utils import (
    make_coded_matrix,
    make_duel_team_in_progress_with_results,
    make_player_2_without_game_points,
    make_team_1,
    make_team_2)
from tests.util_tests import (
    make_duel_canceled,
    make_duel_finished_with_results,
    make_duel_in_progress_with_results,
    make_player_1)
from unittest.mock import MagicMock, patch
import pytest


def make_end_duel_request(duel_id: str = 'f13eb50c'):
    return {'duel_id': duel_id}


duel_adapter_mock_canceled = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_duel_canceled()),
    save=MagicMock(return_value='f13eb50c'))
duel_adapter_mock_player = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_duel_in_progress_with_results()),
    save=MagicMock(return_value='f13eb50c'))
duel_adapter_mock_team = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(
        return_value=make_duel_team_in_progress_with_results()),
    save=MagicMock(return_value='f13eb50c'))
notification_adapter_mock = MagicMock(
    save=MagicMock(return_value='q1w2e3'))
player_adapter_mock_1 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_1()),
    save=MagicMock(return_value='a1b2c3'))
player_adapter_mock_1_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_1()),
    save=MagicMock(side_effect=Exception('oops')))
player_adapter_mock_2 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_2_without_game_points()),
    save=MagicMock(return_value='player123'))
team_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(return_value='team123'))
values_adapter_mock = MagicMock()


@patch.object(DuelSettlementTaskPlayer,
              'run', return_value=make_duel_finished_with_results())
@patch('boto3.resource')
@patch('boto3.client')
def test_end_duel_lambda_performed(boto_client,
                                   boto_resource,
                                   duel_set_run):
    request_json = make_end_duel_request()
    request = EndDuelLambdaRequestModel(request_json)
    interactor = EndDuelLambdaInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_mock_player,
        duel_adapter_graphql=duel_adapter_mock_player,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_mock,
        values_adapter=values_adapter_mock,
        judge_matrix=make_coded_matrix())
    process_result = interactor.run()

    assert process_result
    assert isinstance(process_result, EndDuelLambdaResponseModel)

    process_result_json = process_result()
    assert process_result_json['processing_performed']
    assert process_result_json['duel_id'] == 'f13eb50c'
    assert process_result_json['duel_status'] == \
        DuelStatus.FINISHED_BY_VICTORY.value


@patch('playerstars_interactors.duel.duel_settlement_task.'
       'duel_settlement_task_team.DuelSettlementTaskTeam.get_challenger',
       return_value=make_team_1())
@patch('playerstars_interactors.duel.duel_settlement_task.'
       'duel_settlement_task_team.DuelSettlementTaskTeam.get_challenged',
       return_value=make_team_2())
@patch('boto3.resource')
@patch('boto3.client')
def test_end_duel_team_performed(client, resource, challenged, challenger):
    request_json = make_end_duel_request(
        make_duel_team_in_progress_with_results().entity_id)
    request = EndDuelLambdaRequestModel(request_json)
    interactor = EndDuelLambdaInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_mock_team,
        duel_adapter_graphql=duel_adapter_mock_team,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_2,
        team_adapter=team_adapter_mock,
        values_adapter=values_adapter_mock,
        judge_matrix=make_coded_matrix())
    process_result = interactor.run()

    assert process_result
    assert isinstance(process_result, EndDuelLambdaResponseModel)

    process_result_json = process_result()
    assert process_result_json['processing_performed']
    assert process_result_json['duel_id'] == 'f13eb50c'
    assert process_result_json['duel_status'] == \
        DuelStatus.FINISHED_BY_VICTORY.value


@patch.object(DuelSettlementTaskPlayer,
              'run', return_value=make_duel_finished_with_results())
@patch('boto3.resource')
@patch('boto3.client')
def test_end_duel_not_performed(client, resource, duel_set_run):
    request_json = make_end_duel_request()
    request = EndDuelLambdaRequestModel(request_json)
    interactor = EndDuelLambdaInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_mock_canceled,
        duel_adapter_graphql=duel_adapter_mock_canceled,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_mock,
        values_adapter=values_adapter_mock,
        judge_matrix=make_coded_matrix())
    process_result = interactor.run()

    assert process_result
    assert isinstance(process_result, EndDuelLambdaResponseModel)

    process_result_json = process_result()
    assert not process_result_json['processing_performed']
    assert process_result_json['duel_id'] == 'f13eb50c'
    assert process_result_json['duel_status'] == \
        DuelStatus.CANCELED_BY_INCONSISTENT_RESULT.value


@patch.object(DuelSettlementTaskPlayer, 'run',
              side_effect=Exception('oops'))
@patch('boto3.resource')
@patch('boto3.client')
def test_end_duel_lambda_raises(boto_client, boto_resource, duel_set_run):
    request_json = make_end_duel_request()
    request = EndDuelLambdaRequestModel(request_json)
    interactor = EndDuelLambdaInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_mock_player,
        duel_adapter_graphql=duel_adapter_mock_player,
        notification_adapter=notification_adapter_mock,
        player_adapter=player_adapter_mock_1_raises,
        team_adapter=team_adapter_mock,
        values_adapter=values_adapter_mock,
        judge_matrix=make_coded_matrix())

    with pytest.raises(EndDuelLambdaException) as exc:
        interactor.run()
    assert 'oops' in str(exc.value)
