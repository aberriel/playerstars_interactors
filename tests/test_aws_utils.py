import json
from datetime import datetime
from unittest.mock import patch

# noinspection PyProtectedMember
from playerstars_interactors.utils.aws_lambda_utils import (
    add_event_lambda,
    _get_lambda_function_info,
    _get_lambda_function_list,
    _make_cron_expression_for_lambda_event, _get_lambda_client,
    _get_events_client, _format_statement_id
)
from tests.util_tests import make_lambda_list_functions_result


class Patches:
    prefix = 'playerstars_interactors.utils.aws_lambda_utils'

    BOTO3 = prefix + '.boto3'
    MAKE_CRON_EFLE = prefix + '._make_cron_expression_for_lambda_event'
    GET_LAMBDA_FUNCTION_INFO = prefix + '._get_lambda_function_info'
    GET_EVENTS_CLIENT = prefix + '._get_events_client'
    GET_LAMBDA_CLIENT = prefix + '._get_lambda_client'
    FORMAT_STATEMENT_ID = prefix + '._format_statement_id'


p = Patches()


event_function_params = {
    'key1': 'Anselmo',
    'key2': 'Duarte',
    'key3': 'Luciano',
}


def test_make_cron_expression_for_event():
    test_dt = datetime(2019, 12, 15, 22, 35, 40)
    cron_expression = _make_cron_expression_for_lambda_event(test_dt)
    assert cron_expression == 'cron(35 22 15 12 ? 2019)'

    test_dt_2 = datetime(2020, 1, 10, 9, 5, 40)
    cron_expression_2 = _make_cron_expression_for_lambda_event(test_dt_2)
    assert cron_expression_2 == 'cron(5 9 10 1 ? 2020)'


@patch(p.MAKE_CRON_EFLE)
@patch(p.GET_LAMBDA_FUNCTION_INFO)
@patch(p.GET_LAMBDA_CLIENT)
@patch(p.GET_EVENTS_CLIENT)
@patch(p.FORMAT_STATEMENT_ID)
def test_add_event_for_lambda_function(mock_format_stmt_id,
                                       mock_get_events,
                                       mock_get_lambda,
                                       mock_glfi,
                                       mock_mcefle):
    event_datetime = datetime(2025, 1, 25, 11, 45, 21)
    result = add_event_lambda(event_datetime,
                              'asfd',
                              event_function_params,
                              'opt')
    mock_get_events.assert_called_once()
    mock_get_lambda.assert_called_once()
    mock_mcefle.assert_called_with(event_datetime)
    mock_glfi.assert_called_with('asfd', 'us-east-1')

    event_client = mock_get_events.return_value
    exp = mock_mcefle.return_value
    event_client.put_rule.assert_called_with(Name='opt',
                                             ScheduleExpression=exp)

    lambda_client = mock_get_lambda.return_value
    fn_name = mock_glfi.return_value.name
    fn_arn = mock_glfi.return_value.arn
    source_arn = event_client.put_rule.return_value.__getitem__.return_value
    stmt_id = mock_format_stmt_id.return_value
    lambda_client.add_permission.assert_called_with(
        FunctionName=fn_name,
        StatementId=stmt_id,
        Action='lambda:InvokeFunction',
        Principal='events.amazonaws.com',
        SourceArn=source_arn)

    event_client.put_targets.assert_called_with(
        Rule='opt',
        Targets=[
            {'Id': fn_name,
             'Arn': fn_arn,
             'Input': json.dumps(event_function_params)}])

    assert result == event_client.put_targets.return_value


@patch(p.BOTO3)
def test_get_lambda_client(mock_boto):
    result = _get_lambda_client()
    mock_boto.client.assert_called_with('lambda')
    assert result == mock_boto.client.return_value


@patch(p.BOTO3)
def test_get_events_client(mock_boto):
    result = _get_events_client()
    mock_boto.client.assert_called_with('events')
    assert result == mock_boto.client.return_value


def test_format_stmt_id():
    result = _format_statement_id('date-str', 'lambda')
    assert result == 'lambda-date-str-invoke'


@patch('playerstars_interactors.utils.aws_lambda_utils.boto3')
@patch('playerstars_interactors.utils.aws_lambda_utils.'
       '_get_lambda_function_list',
       return_value=make_lambda_list_functions_result())
def test_get_lambda_info(mock_get_lambda_function_list,
                         boto_mock):
    lambda_info = _get_lambda_function_info(
        lambda_name_part='duel_scheduled_finisher',
        region='us-east-1')
    assert lambda_info


@patch('playerstars_interactors.utils.aws_lambda_utils.boto3')
def test_get_lambda_function_list(mock_boto):
    function_list = _get_lambda_function_list('us-east-1')
    assert function_list
