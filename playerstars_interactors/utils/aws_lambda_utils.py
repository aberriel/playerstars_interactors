from collections import namedtuple
from datetime import datetime
import boto3
import json


runtime = 'python3.7'


def _make_cron_expression_for_lambda_event(event_date: datetime):
    expression = 'cron({0} {1} {2} {3} ? {4})'.format(
        event_date.minute,
        event_date.hour,
        event_date.day,
        event_date.month,
        event_date.year)
    return expression


def _get_lambda_function_list(region):
    lambda_client = boto3.client('lambda', region_name=region)
    lambda_function_list = lambda_client.list_functions()
    return lambda_function_list


def _get_lambda_function_info(lambda_name_part, region):
    RetType = namedtuple('RetType', 'name, arn')
    function_list = _get_lambda_function_list(region)
    function_info_raw = [
        x for x in function_list['Functions']
        if lambda_name_part in x['FunctionName']][0]
    return RetType(name=function_info_raw['FunctionName'],
                   arn=function_info_raw['FunctionArn'])


def add_event_lambda(event_datetime: datetime,
                     lambda_name_part: str,
                     event_params: dict,
                     event_name: str,
                     region: str = 'us-east-1'):
    events_client = _get_events_client()
    lambda_client = _get_lambda_client()

    schedule_exp = _make_cron_expression_for_lambda_event(event_datetime)

    fn_info = _get_lambda_function_info(lambda_name_part, region)

    event_datetime_str = event_datetime.isoformat()
    event_statement_id = _format_statement_id(event_datetime_str, fn_info.name)

    events_response = events_client.put_rule(
        Name=event_name,
        ScheduleExpression=schedule_exp)
    event_rule_arn = events_response['RuleArn']

    lambda_client.add_permission(
        FunctionName=fn_info.name,
        StatementId=event_statement_id,
        Action='lambda:InvokeFunction',
        Principal='events.amazonaws.com',
        SourceArn=event_rule_arn)
    scheduled_lambda = [{
        'Id': fn_info.name,
        'Arn': fn_info.arn,
        'Input': json.dumps(event_params)
    }]
    target_response = events_client.put_targets(Rule=event_name,
                                                Targets=scheduled_lambda)
    return target_response


def _format_statement_id(event_datetime_str, lambda_name):
    event_statement_id = f'{lambda_name}-{event_datetime_str}-invoke'
    return event_statement_id


def _get_lambda_client():
    lambda_client = boto3.client('lambda')
    return lambda_client


def _get_events_client():
    events_client = boto3.client('events')
    return events_client
