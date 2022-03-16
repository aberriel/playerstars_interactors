from playerstars_domain import (
    ComponentResult, DuelComponentResult, DuelMemberType, Duel, Values, Team,
    ImageValidity, PlayerDuelInfo)
import logging
from playerstars_interactors.utils.report_exception import exception_str
from playerstars_interactors.utils.upload_photos import \
    upload_photo_and_return_url
from playerstars_interactors.utils.image_utils import check_image


class ValidatePhotoException(BaseException):
    pass


class UploadImageException(BaseException):
    pass


class ValidatePhotoRequestModel:
    def __init__(self, query_params):
        self.photo = query_params.get('image_base64')
        self.duel_id = query_params.get('duel_id')
        self.player_id = query_params.get('player_id')
        self.claimed_result = query_params.get('result')


class ValidatePhotoResponseModel:
    def __init__(self, duel_info: PlayerDuelInfo):
        self.informed_result = duel_info.inform.value
        self.image_validity = duel_info.image_validity.value
        self.validation_result = duel_info.report_state.value

    def __call__(self):
        return {
            "informed_result": self.informed_result,
            "image_validity": self.image_validity,
            "validation_result": self.validation_result
        }


class ValidatePhotoAdapters:
    def __init__(self, player_adapter, team_adapter,
                 duel_adapter, values_adapter):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.duel_adapter = duel_adapter
        self.values_adapter = values_adapter


class ValidatePhotoInteractor:
    def __init__(self, request: ValidatePhotoRequestModel,
                 adapters: ValidatePhotoAdapters,
                 s3_bucket_name, s3_bucket_url):
        self.request = request
        self.adapters = adapters
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.logger = logging.getLogger(__name__)

    def upload_image(self):
        try:
            if self.request.photo:
                return upload_photo_and_return_url(
                    sent_image=self.request.photo,
                    unique_name='duel_{0}_{1}'.format(
                        self.request.duel_id, self.request.player_id),
                    s3_bucket_name=self.s3_bucket_name,
                    s3_bucket_url=self.s3_bucket_url)
        except Exception as e:
            msg = f'Error uploading result image: {exception_str(e)}'
            raise UploadImageException(msg)

    def get_claimed_result_data(self, image_url):
        return DuelComponentResult(
            result=self.get_component_result(self.request.claimed_result),
            result_image=image_url)

    @staticmethod
    def get_component_result(result_str):
        result_matrix = {
            'victory': ComponentResult.WINNER,
            'defeat': ComponentResult.LOSER,
            'resignation': ComponentResult.RESIGNED,
            'tie': ComponentResult.TIED
        }
        return result_matrix[result_str]

    def get_team_captain_tag_name(self, team, console_id):
        captain = self.adapters.player_adapter.get_by_id(
            team.captain.player_id)
        return captain.get_tag_name(console_id)

    def process_member_result(self, duel_result, member, duel):
        self.logger.info('processing member result')
        self.logger.info(f'Duel member type: {duel.member_type}')
        tag_name = member.get_tag_name(duel.console.entity_id) \
            if duel.member_type == DuelMemberType.PLAYER \
            else self.get_team_captain_tag_name(
            member, duel.console.entity_id)
        self.logger.info(f'Tag Name: {tag_name}')

        image_validation: ImageValidity = self.compare_result_with_image(
            duel_result, tag_name, duel.game.entity_id)
        self.logger.info('image validation')
        self.logger.info(image_validation)
        self.logger.info('duel result.result')
        if duel_result:
            self.logger.info(duel_result.result)
        else:
            self.logger.info('none')
        player_duel_info = PlayerDuelInfo.get_player_duel_info(
            duel_member_result=duel_result, image_validation=image_validation)
        return player_duel_info

    def compare_result_with_image(self, result, player_tag_name, game_id):
        if not result or not result.result_image:
            return ImageValidity.NOT_SENT
        validator_class_name = self.get_validator_class_name(game_id)
        return check_image(
            result, player_tag_name, validator_class_name, self.logger)

    def get_validator_class_name(self, game_id):
        all_values: [Values] = self.adapters.values_adapter.list_all()
        validator_maps = all_values[0].validator_maps
        for x in validator_maps:
            if x.game_id == game_id:
                return x.class_name

    def get_member(self, duel):
        if duel.member_type == DuelMemberType.PLAYER:
            return self.adapters.player_adapter.get_by_id(
                self.request.player_id)
        if duel.member_type == DuelMemberType.TEAM:
            captain = self.adapters.player_adapter.get_by_id(
                self.request.player_id)
            team_challenger: Team = self.adapters.team_adapter.get_by_id(
                duel.challenger)
            team_challenged: Team = self.adapters.team_adapter.get_by_id(
                duel.challenged)
            return team_challenger if team_challenger.check_if_member(
                    captain.entity_id) else team_challenged

    def check_challenger_or_challenged(self, duel):
        if duel.member_type == DuelMemberType.PLAYER:
            return True if duel.challenger == self.request.player_id \
                else False
        if duel.member_type == DuelMemberType.TEAM:
            team_challenger: Team = self.adapters.team_adapter.get_by_id(
                duel.challenger)
            return True if team_challenger.check_if_member(
                self.request.player_id) else False

    def update_duel(self, duel: Duel,
                    duel_info: PlayerDuelInfo, claimed_result):
        challenger = self.check_challenger_or_challenged(duel)
        if challenger:
            duel.challenger_duel_result = claimed_result
            duel.challenger_duel_info = duel_info.report_state
        else:
            duel.challenged_duel_result = claimed_result
            duel.challenged_duel_info = duel_info.report_state
        duel.set_adapter(self.adapters.duel_adapter)
        duel.save()

    def run(self):
        try:
            self.logger.info('Starting validate photo')
            duel: Duel = self.adapters.duel_adapter.get_by_id(
                self.request.duel_id)
            self.logger.info(f'Duel {duel.entity_id} loaded')

            member = self.get_member(duel)
            self.logger.info(f'Member {member} loaded')

            photo_url = self.upload_image()
            self.logger.info(f'Photo uploaded')

            claimed_result = self.get_claimed_result_data(photo_url)
            self.logger.info(f'Result being claimed : {claimed_result}')

            duel_info = self.process_member_result(
                claimed_result, member, duel)
            self.logger.info(f'Duel info generated: {duel_info}')

            self.update_duel(duel, duel_info, claimed_result)
            self.logger.info('Duel updated')

            response = ValidatePhotoResponseModel(duel_info)
            self.logger.info(f'Response: {response}')
            return response
        except BaseException as exc:
            msg = f'Error during photo validation: {exc}'
            self.logger.error(msg)
            raise ValidatePhotoException(msg)
