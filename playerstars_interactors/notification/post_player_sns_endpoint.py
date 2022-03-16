from playerstars_adapters import PlayerAdapter
from playerstars_domain import Player, PushNotificationData
from playerstars_interactors.utils.domain_utils import find_entity_by_id

import boto3
import logging


class PostPlayerSnsEndpointException(BaseException):
    pass


class PostPlayerSnsEndpointRequestModel:
    def __init__(self, json_data: dict):
        self.player_id = json_data['player_id']
        self.token = json_data['token']


class PostPlayerSnsEndpointResponseModel:
    def __init__(self, endpoint_arn: str):
        self.endpoint_arn = endpoint_arn

    def __call__(self):
        return self.endpoint_arn


class PostPlayerSnsEndpointInteractor:
    def __init__(self, request: PostPlayerSnsEndpointRequestModel,
                 player_adapter: PlayerAdapter,
                 platform_arn: str,
                 aws_region: str):
        self.request = request
        self.player_adapter = player_adapter
        self.platform_arn = platform_arn
        self.aws_region = aws_region
        self.logger = logging.getLogger(__name__)

    def get_player(self, player_id):
        return find_entity_by_id(
            _id=player_id,
            adapter_instance=self.player_adapter,
            class_name='Player')

    def get_endpoint(self, player_data):
        try:
            if player_data.push_notification_data is not None:
                endpoint_arn = player_data.push_notification_data.endpoint_arn
                return boto3.client('sns').get_endpoint_attributes(
                    EndpointArn=endpoint_arn)
            return None
        except BaseException:
            return None

    def create_endpoint(self):
        response = boto3.client('sns').create_platform_endpoint(
            PlatformApplicationArn=self.platform_arn,
            Token=self.request.token)
        return response['EndpointArn']

    def update_endpoint(self, endpoint_arn):
        boto3.client('sns').set_endpoint_attributes(
            EndpointArn=endpoint_arn,
            Attributes={
                'Token': self.request.token})

    def update_player_sns_endpoint(self, endpoint_arn,
                                   player_data):
        push_notification_data = PushNotificationData(
            endpoint_arn=endpoint_arn,
            device_token=self.request.token)
        player_data.push_notification_data = push_notification_data
        player_data.save()

    def run(self):
        try:
            player_data: Player = self.get_player(self.request.player_id)
            current_endpoint = self.get_endpoint(player_data)
            if not current_endpoint:
                endpoint_arn = self.create_endpoint()
            else:
                endpoint_arn = player_data.push_notification_data.endpoint_arn
                self.update_endpoint(endpoint_arn)
            self.update_player_sns_endpoint(
                endpoint_arn=endpoint_arn,
                player_data=player_data)
            return PostPlayerSnsEndpointResponseModel(endpoint_arn)
        except BaseException as exc:
            msg = f'Error during persist SNS endpoint: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise PostPlayerSnsEndpointException(msg)
